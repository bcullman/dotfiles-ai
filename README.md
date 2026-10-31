# dotfiles-ai

Inventory first, normalize second, deploy third. This repository currently captures and compares
configuration; it does not install settings or execute captured files.

## Capture a machine

Requires Python 3.8+ on macOS or Linux (including WSL, Linux NAS devices, and Raspberry Pi).
No third-party Python packages, root access, Git, zsh, or network are needed for capture.
Copy this directory to a machine if a Git remote is not yet available. On a NAS without Python,
install Python through its supported package system first; appliance compatibility is not assumed.

From this repository:

```sh
python3 scripts/capture.py --label mac
python3 scripts/capture.py --label nas
python3 scripts/capture.py --label work-wsl
python3 scripts/capture.py --label pi
```

Run only the command for that machine. Each run prints a new `.private/<label>-<timestamp>` directory.
Use an alias, not a real hostname. Captures contain exact allowlisted file bytes, original permission
modes, SHA-256 hashes, statuses, collection time, collector OS/architecture, and the capture policy.
They also inventory top-level dotfile and `.config` names to reveal gaps in the allowlist.

**Raw captures are private and ignored by Git.** Shell and Git files can contain secrets even when
their names look harmless. There is no claim of automatic sanitization. Output directories are mode
700 and copied files mode 600. Never force-add `.private`, upload it to a public service, or move work
configuration into a personal repository. On WSL, run on its Linux filesystem to retain Unix modes.
Capture while configuration files are not being edited; this is not an atomic filesystem snapshot.

The collector does not read credential stores, histories, private/local overrides, or arbitrary
`.config` trees. Symlinks (including parent directories) are recorded and not followed. Non-text,
oversized, missing, and unreadable files are recorded without aborting the entire capture. Consult
`manifest.json` for skipped files; a successful exit means the manifest was written, not full coverage.
Files outside the allowlist are not claimed to be absent. XDG paths outside `~/.config`, custom
ZDOTDIR, system configuration, macOS preferences, and installed package inventories need a separate
scoped collection decision. The initial collector targets user configuration, not a machine backup.

Add specific paths to `capture-policy.json` after reviewing their purpose, or pass `--policy` with
a private JSON policy of the same shape. Directory entries recurse, so prefer individual file paths.
Name exclusions are a guardrail, not a secret scanner. Do not use this against a hostile filesystem.

## Compare captures

```sh
python3 scripts/capture.py --label legacy-mac --source-kind legacy --root ../dotfiles-mac/src
python3 scripts/compare.py .private/<old>/manifest.json .private/<new>/manifest.json
```

Comparison reports exact content and mode equality, one-sided files, and unresolved cases. Its output
contains paths that may be private; review before saving it under `evidence/`. Keep raw transfers
between trusted machines private. For work WSL, review on the work machine and share only approved
generic findings; retain private work files there.

The committed `evidence/` directory contains reviewed summaries, not raw home-directory copies.
Promote a sanitized, reusable configuration file into managed source only after classifying it as
shared, platform, role, or host-specific. Never infer that the newest version is the best version.

## Current findings and proposal

- [Initial inventory and ownership](docs/inventory.md)
- [Tool comparison and recommendation](docs/tool-selection.md)
- [Reviewed Mac comparison](evidence/mac-baseline.md)

NAS, WSL, and Pi captures are still pending. No settings have been deployed, existing repositories
have not been modified, and no remote repository has been created.

## Validation

```sh
python3 -m unittest discover -s tests -v
```

Tests cover copying integrity, exclusion boundaries, traversal, symlinks, FIFO avoidance, size/text
limits, output permissions, repeat capture protection, and unknown-versus-missing comparisons.
