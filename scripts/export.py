#!/usr/bin/env python3
"""Prepare, scan, review, then publish sanitized file evidence. Never auto-commit."""
import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from capture import REPO, linked, relative_path


class ExportError(ValueError):
    """A diagnostic authored here that contains no user-provided values."""


def private_path(path):
    private = REPO / ".private"
    if private.is_symlink():
        raise ExportError("Private directory must not be a symlink")
    private.mkdir(mode=0o700, exist_ok=True)
    os.chmod(str(private), 0o700)
    path = path.absolute()
    path.resolve().relative_to(private.resolve())
    if linked(private, path.relative_to(private)):
        raise ExportError("Private inputs must not be symlinks")
    return path


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.chmod(str(path), 0o600)


def init_rules(capture, rules):
    if rules.exists():
        raise ExportError("Rules already exist; refusing to overwrite")
    manifest = read_json(capture / "manifest.json")
    write_json(rules, {
        "files": [{"source": r["path"], "target": r["path"]}
                  for r in manifest["files"] if r["status"] == "captured"],
        "replacements": [{"value": str(Path.home()), "placeholder": "__HOME__", "files": ["*"]}]
    })


def validate_rules(rules):
    if set(rules) != {"files", "replacements"} or not rules["files"]:
        raise ExportError("Rules require a nonempty files list and a replacements list")
    targets = set()
    for entry in rules["files"]:
        if set(entry) != {"source", "target"}:
            raise ExportError("Each selected file requires source and target")
        relative_path(entry["source"])
        target = relative_path(entry["target"]).as_posix()
        if not re.fullmatch(r"[A-Za-z0-9_./-]+", target) or ".git" in Path(target).parts:
            raise ExportError("Use generic portable target filenames")
        if target in targets:
            raise ExportError("Duplicate target")
        targets.add(target)
    values = set()
    for rule in rules["replacements"]:
        if set(rule) != {"value", "placeholder", "files"}:
            raise ExportError("Replacement requires value, placeholder, files")
        if not isinstance(rule["value"], str) or not rule["value"] or rule["value"] in values:
            raise ExportError("Replacement values must be nonempty and unique")
        if not re.fullmatch(r"__[A-Z][A-Z0-9_]*__", rule["placeholder"]):
            raise ExportError("Use semantic placeholders such as __HOME__ or __API_TOKEN__")
        if not isinstance(rule["files"], list) or not rule["files"] or not all(isinstance(p, str) and p for p in rule["files"]):
            raise ExportError("Replacement files must be nonempty path glob lists")
        values.add(rule["value"])


def scrub(text, source, replacements):
    mapping = {r["value"]: r["placeholder"] for r in replacements
               if any(fnmatch.fnmatchcase(source, p) for p in r["files"])}
    if not mapping:
        return text
    # Longest first and one pass: overlapping values do not cascade into other replacements.
    pattern = re.compile("|".join(re.escape(v) for v in sorted(mapping, key=len, reverse=True)))
    return pattern.sub(lambda match: mapping[match.group(0)], text)


def build(capture, rules, candidate):
    validate_rules(rules)
    original = read_json(capture / "manifest.json")
    label = original["label"]
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,39}", label):
        raise ExportError("Invalid public alias")
    family = original["policy"].get("family", "unspecified")
    if family not in {"mac", "linux", "wsl", "nas", "pi", "unspecified"}:
        raise ExportError("Invalid family")
    records = {r["path"]: r for r in original["files"]}
    candidate.mkdir(mode=0o700)
    rows = []
    for entry in rules["files"]:
        source, target = entry["source"], entry["target"]
        row = records[source]
        if row["status"] != "captured" or linked(capture, Path("files") / source):
            raise ExportError("Selected source is unavailable or symlinked")
        raw = (capture / "files" / source).read_bytes()
        if hashlib.sha256(raw).hexdigest() != row["sha256"]:
            raise ExportError("Captured file changed; recapture before export")
        data = scrub(raw.decode("utf-8"), source, rules["replacements"]).encode("utf-8")
        destination = candidate / "files" / target
        destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        destination.write_bytes(data)
        os.chmod(str(destination), 0o600)
        rows.append({"path": target, "status": "captured", "mode": row["mode"],
                     "sha256": hashlib.sha256(data).hexdigest()})
    write_json(candidate / "manifest.json", {
        "schema_version": 1, "representation": "sanitized-not-installable",
        "label": label, "family": family,
        "files": sorted(rows, key=lambda r: r["path"])
    })
    # Check all known originals everywhere, even if their replacement was file-scoped.
    # Also check filenames and JSON-decoded metadata, not just file text.
    texts = [str(p.relative_to(candidate)) for p in candidate.rglob("*")]
    texts += [p.read_text(encoding="utf-8") for p in candidate.rglob("*") if p.is_file()]
    texts += [json.dumps(read_json(candidate / "manifest.json"), ensure_ascii=False)]
    if any(r["value"] in text for r in rules["replacements"] for text in texts):
        raise ExportError("A configured private value remains; revise rules or target filenames")
    return label


def digest_tree(candidate):
    digest = hashlib.sha256()
    for path in sorted(p for p in candidate.rglob("*") if p.is_file()):
        digest.update(path.relative_to(candidate).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def scan(candidate, scratch):
    # Provider/entropy rules can miss ordinary punctuation-heavy passwords.
    # Independently reject literal credential assignments without printing their values.
    assignment = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")
    for path in candidate.rglob("*"):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            match = assignment.match(line)
            if not match or not re.search(r"password|passwd|secret|token|api_?key", match[1], re.I):
                continue
            value = match[2]
            quoted = re.fullmatch(r"(['\"])(.*?)\1\s*(?:#.*)?", value)
            if quoted:
                value = quoted[2]
            else:
                value = value.split(" #", 1)[0].strip()
            if not value or re.fullmatch(r"__[A-Z][A-Z0-9_]*__|\$[A-Za-z_][A-Za-z0-9_]*|\$\{[A-Za-z_][A-Za-z0-9_]*\}", value):
                continue
            raise ExportError("Unredacted credential assignment found; review the private candidate")
    executable = shutil.which("gitleaks")
    if executable is None:
        raise ExportError("Gitleaks is required for export; no publishable snapshot created")
    ignore = scratch / "empty-ignore"
    ignore.write_text("")
    report = scratch / "scan.json"
    env = {k: v for k, v in os.environ.items() if not k.startswith("GITLEAKS_")}
    with (scratch / "scan.log").open("wb") as log:
        result = subprocess.run([
            executable, "dir", str(candidate), "--config", str(REPO / "scanner.toml"),
            "--gitleaks-ignore-path", str(ignore), "--ignore-gitleaks-allow",
            "--max-decode-depth", "3", "--redact=100", "--no-banner",
            "--report-format", "json", "--report-path", str(report),
        ], stdout=log, stderr=log, env=env, cwd=str(scratch), timeout=180)
    if result.returncode != 0 or not report.is_file() or read_json(report) != []:
        raise ExportError("Secret scan failed or found secrets; inspect private scan logs/report")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["init-export", "export"])
    parser.add_argument("--capture", required=True, type=Path)
    parser.add_argument("--rules", required=True, type=Path)
    parser.add_argument("--reviewed", help="Full digest of the exact sanitized snapshot you reviewed")
    args = parser.parse_args()
    # All generated intermediates and scanner logs remain private, even on failure.
    os.umask(0o077)
    try:
        capture = private_path(args.capture)
        rules = private_path(args.rules)
        if args.action == "init-export":
            init_rules(capture, rules)
            print("Private rules created. Review selected files, target names, and replacement values locally.")
            return 0
        scratch = Path(tempfile.mkdtemp(prefix="export-", dir=str(REPO / ".private")))
        candidate = scratch / "candidate"
        print("Private review directory: " + str(scratch.relative_to(REPO)))
        label = build(capture, read_json(rules), candidate)
        scan(candidate, scratch)
        digest = digest_tree(candidate)
        if not args.reviewed:
            print("Scan passed. Review candidate files locally; they are not yet publishable.")
            print("After review, repeat with --reviewed " + digest)
            return 0
        if args.reviewed != digest:
            raise ExportError("Snapshot differs from reviewed digest; review the new candidate")
        parent = REPO / "evidence/snapshots" / label
        if linked(REPO, parent.relative_to(REPO)):
            raise ExportError("Snapshot directories must not be symlinks")
        parent.mkdir(parents=True, exist_ok=True)
        destination = parent / digest[:16]
        if destination.exists():
            raise ExportError("Snapshot already exists; no overwrite performed")
        candidate.rename(destination)
        print("Reviewed sanitized snapshot: " + str(destination.relative_to(REPO)))
        print("Review git diff, then add/commit only this snapshot directory. Nothing was staged or pushed.")
    except ExportError as error:
        print("Stopped: " + str(error), file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        # Never print arbitrary exceptions: JSON/OS errors can contain private values or paths.
        print("Stopped safely ({}). Check local rules, capture integrity, and private scan report; "
              "no snapshot was published.".format(type(error).__name__), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
