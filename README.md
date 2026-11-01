# dotfiles-ai

Inventory first, normalize second, deploy third. This repository currently captures and compares
configuration; it does not install settings or execute captured files.

## Capture a machine

Start with `zsh dotfiles.zsh doctor`. The zsh launcher checks for Python 3.8+ on macOS or Linux
(including WSL, Linux NAS devices, and Raspberry Pi); it does not assume Python is installed.
No third-party Python packages, root access, Git, zsh, or network are needed for capture.
Copy this directory to a machine if a Git remote is not yet available. On a NAS without Python,
install Python through its supported package system first; appliance compatibility is not assumed.

From this repository:

```sh
zsh dotfiles.zsh capture --label mac --family mac
zsh dotfiles.zsh capture --label nas --family nas
zsh dotfiles.zsh capture --label work-wsl --family wsl
zsh dotfiles.zsh capture --label pi --family pi
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
a private JSON policy of the same shape. Use the unified `patterns` list for files, wildcards, and directories. Matched directories recurse,
so use narrower patterns when only selected files are needed.
Global rules are overlaid by the explicit family and optional local policy.
Name exclusions are a guardrail, not a secret scanner. Do not use this against a hostile filesystem.

## Compare captures

```sh
zsh dotfiles.zsh capture --label legacy-mac --family mac --source-kind legacy --root ../dotfiles-mac/src
zsh dotfiles.zsh compare .private/<old>/manifest.json .private/<new>/manifest.json
```

Comparison reports exact content and mode equality, one-sided files, and unresolved cases. Its output
contains paths that may be private; review before saving it under `evidence/`. Keep raw transfers
between trusted machines private. For work WSL, review on the work machine and share only approved
generic findings; retain private work files there.

The committed `evidence/` directory contains reviewed summaries and can receive sanitized file
snapshots through the gated export workflow. It never receives raw home-directory copies.
See [capture, sanitize, review, commit](docs/capture-workflow.md) for family policies, private
replacement maps, required secret scanning, and per-machine Git commits.
Promote a sanitized, reusable configuration file into managed source only after classifying it as
shared, platform, role, or host-specific. Never infer that the newest version is the best version.

## Current findings and proposal

- [Initial inventory and ownership](docs/inventory.md)
- [Tool comparison and recommendation](docs/tool-selection.md)
- [Reviewed Mac comparison](evidence/mac-baseline.md)
- [Mac–NAS comparison and remediation findings](docs/mac-nas-comparison.md)

Mac and NAS snapshots are available; work WSL and Pi captures remain pending. No live settings have
been deployed. The repository has a GitHub remote. See the Mac–NAS comparison for the credential
remediation discovered in the earlier Mac snapshot. The published branch history and both known
clones have been cleaned; credential rotation remains pending. See [cleanup record](docs/history-cleanup.md).

## Validation

```sh
python3 -m unittest discover -s tests -v
```

Tests cover copying integrity, exclusion boundaries, traversal, symlinks, FIFO avoidance, size/text
limits, output permissions, repeat capture protection, unknown-versus-missing comparisons, policy
layering, missing prerequisites, literal scrubbing, residual secrets, and exact-review export gates.
The real-scanner integration test runs when Gitleaks is on PATH; otherwise it is explicitly skipped.
