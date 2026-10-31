"""Global capture rules plus explicit additive family and local overlays."""
import fnmatch
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FAMILIES = ("mac", "linux", "wsl", "nas", "pi")


def load_policy(base, family=None, local=None):
    policy = json.loads(Path(base).read_text())
    if "files" in policy or "directories" in policy:
        raise ValueError("Combine capture files and directories into patterns")
    policy.setdefault("excludes", [])
    policy.setdefault("exclude_components", [])
    layers = []
    if family:
        if family not in FAMILIES:
            raise ValueError("Unknown family")
        if family in ("wsl", "nas", "pi"):
            layers.append(REPO / "policies/linux.json")
        layers.append(REPO / "policies" / (family + ".json"))
    if local:
        layers.append(Path(local))
    for path in layers:
        overlay = json.loads(path.read_text())
        keys = ("patterns", "excludes", "exclude_components")
        if set(overlay) - (set(keys) | {"remove_" + key for key in keys}):
            raise ValueError("Unknown policy overlay key")
        if any(not isinstance(v, list) or not all(isinstance(p, str) and p for p in v)
               for v in overlay.values()):
            raise ValueError("Policy overlay fields must be lists of nonempty strings")
        for key in keys:
            removed = set(overlay.get("remove_" + key, []))
            policy[key] = sorted((set(policy[key]) - removed) | set(overlay.get(key, [])))
    policy["family"] = family or "unspecified"
    return policy


def excluded(path, policy):
    # Match the entire relative path and each ancestor, so excluded directories prune their trees.
    names = [path.as_posix()] + [p.as_posix() for p in path.parents if str(p) != "."]
    return (".git" in path.parts or
            any(fnmatch.fnmatchcase(name, pattern)
                for name in names for pattern in policy.get("excludes", [])) or
            any(fnmatch.fnmatchcase(part.lower(), pattern.lower())
                for part in path.parts for pattern in policy.get("exclude_components", [])))
