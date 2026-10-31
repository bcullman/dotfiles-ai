#!/usr/bin/env python3
"""Read-only, allowlisted dotfile capture. Output is private, never auto-staged."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import stat
import sys
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parents[1]
BLOCKED = re.compile(
    r"(^|[._-])(private|local|secret|secrets|token|tokens|credentials|auth|"
    r"history|cache|sessions?|buffers|backups?)([._-]|$)", re.I
)
BLOCKED_PARTS = {".git", ".ssh", ".aws", ".gnupg", ".codex", ".agents",
                 ".claude", "node_modules", ".env"}


def relative_path(value):
    path = Path(value)
    if not value or path.is_absolute() or ".." in path.parts or str(path) == ".":
        raise ValueError("Policy paths must be nonempty relative paths without '..'")
    return path


def blocked(path):
    return any(part in BLOCKED_PARTS or BLOCKED.search(part)
               or part.startswith('.env.') or part.endswith(('.pem', '.key'))
               for part in path.parts)


def linked(root, relative):
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def read_file(path, limit):
    # No final symlink following; parent links are checked separately.
    fd = os.open(str(path), os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                 | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(fd, "rb") as stream:
        mode = os.fstat(stream.fileno()).st_mode
        if not stat.S_ISREG(mode):
            return None, "not-regular-file", None
        data = stream.read(limit + 1)
    if len(data) > limit:
        return None, "too-large", None
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return None, "non-text", None
    if b"\0" in data:
        return None, "non-text", None
    return data, "captured", stat.S_IMODE(mode)


def capture(root, output, label, policy, source_kind):
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Source root must be a directory")
    paths = {relative_path(p) for p in policy["files"]}
    directories = [relative_path(p) for p in policy["directories"]]
    limit = policy["max_file_bytes"]
    if not isinstance(limit, int) or limit < 1:
        raise ValueError("max_file_bytes must be positive")
    rows = []
    for relative in directories:
        if blocked(relative) or linked(root, relative):
            rows.append({"path": relative.as_posix(), "status": "excluded-directory"})
            continue
        directory = root / relative
        if not directory.exists():
            rows.append({"path": relative.as_posix(), "status": "missing-directory"})
            continue
        if not directory.is_dir():
            rows.append({"path": relative.as_posix(), "status": "not-directory"})
            continue
        def walk_error(error):
            rows.append({"path": Path(error.filename).relative_to(root).as_posix(),
                         "status": "unreadable-directory"})
        for base, dirs, files in os.walk(str(directory), followlinks=False, onerror=walk_error):
            for name in list(dirs):
                rel = (Path(base) / name).relative_to(root)
                if blocked(rel) or linked(root, rel):
                    dirs.remove(name)
                    rows.append({"path": rel.as_posix(), "status": "excluded-directory"})
            paths.update((Path(base) / name).relative_to(root) for name in files)
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    os.chmod(str(output), 0o700)
    for relative in sorted(paths):
        row = {"path": relative.as_posix()}
        data = None
        if blocked(relative):
            row["status"] = "excluded-name"
        elif linked(root, relative):
            row["status"] = "symlink-not-followed"
        else:
            try:
                data, row["status"], mode = read_file(root / relative, limit)
            except FileNotFoundError:
                row["status"] = "missing"
            except OSError:
                row["status"] = "unreadable"
        if data is not None:
            target = output / "files" / relative
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            with target.open("xb") as stream:
                os.chmod(str(target), 0o600)
                stream.write(data)
            row.update(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), mode=oct(mode))
        rows.append(row)
    # Names only; these may still be private. Never enumerate credential stores.
    inventory = {}
    for name in [".", ".config"]:
        directory = root / name
        if directory.is_dir() and not directory.is_symlink():
            try:
                inventory[name] = sorted(p.name for p in directory.iterdir()
                                         if name != "." or p.name.startswith("."))
            except OSError:
                inventory[name] = ["<unreadable>"]
    manifest = {
        "schema_version": 1, "label": label, "source_kind": source_kind,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "collector_platform": platform.system(), "collector_arch": platform.machine(),
        "collector_wsl": "microsoft" in platform.release().lower(),
        "policy": policy, "inventory_names_only": inventory,
        "files": sorted(rows, key=lambda row: row["path"]),
    }
    target = output / "manifest.json"
    target.write_text(json.dumps(manifest, indent=2) + "\n")
    os.chmod(str(target), 0o600)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True, help="Non-sensitive alias, e.g. mac or work-wsl")
    parser.add_argument("--root", type=Path, default=Path.home(), help="Home or legacy src directory")
    parser.add_argument("--source-kind", choices=["machine", "legacy"], default="machine")
    parser.add_argument("--policy", type=Path, default=REPO / "capture-policy.json")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,39}", args.label):
        parser.error("Use a lowercase alias containing only letters, digits, and hyphens")
    # Always inside the ignored private area; never accept a publishable output path.
    private = REPO / ".private"
    if private.is_symlink():
        parser.error("Private output directory must not be a symlink")
    private.mkdir(mode=0o700, exist_ok=True)
    os.chmod(str(private), 0o700)
    output = private / (args.label + "-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    try:
        result = capture(args.root, output, args.label,
                         json.loads(args.policy.read_text()), args.source_kind)
    except (OSError, ValueError, KeyError) as error:
        print("Capture failed ({}); inspect private output locally.".format(type(error).__name__), file=sys.stderr)
        return 1
    print(output.relative_to(REPO))
    print("Captured {} files. PRIVATE: review before sharing; no secret detection guarantee.".format(
        sum(row["status"] == "captured" for row in result["files"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
