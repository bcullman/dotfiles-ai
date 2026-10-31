#!/usr/bin/env python3
"""Compare private capture manifests without printing file contents or hashes."""
import argparse
import json
from pathlib import Path


def compare(left, right):
    a = {r["path"]: r for r in left["files"]}
    b = {r["path"]: r for r in right["files"]}
    rows = []
    for path in sorted(a.keys() | b.keys()):
        x, y = a.get(path, {}), b.get(path, {})
        sx, sy = x.get("status", "not-in-policy"), y.get("status", "not-in-policy")
        if sx == sy == "captured":
            status = "identical" if x["sha256"] == y["sha256"] else "content-differs"
            if x.get("mode") != y.get("mode"):
                status += "+mode-differs"
        elif sx == "captured" and sy == "missing":
            status = "left-only"
        elif sy == "captured" and sx == "missing":
            status = "right-only"
        elif sx == sy == "missing":
            status = "absent-both"
        else:
            # Unreadable, excluded, symlinked and out-of-policy are not evidence of absence.
            status = "unresolved"
        rows.append({"path": path, "comparison": status, "left": sx, "right": sy})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    args = parser.parse_args()
    print(json.dumps(compare(json.loads(args.left.read_text()), json.loads(args.right.read_text())), indent=2))


if __name__ == "__main__":
    main()
