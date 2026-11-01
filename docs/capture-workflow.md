# Capture, sanitize, review, commit

This workflow supersedes the initial summary-only evidence plan. Commit sanitized file copies from
each machine so later comparisons can inspect real configuration structure. Raw files and the values
used to sanitize them stay on that machine. Sanitized evidence is not an installable configuration.

## 1. Start with zsh

```sh
zsh dotfiles.zsh doctor
```

Only zsh is assumed initially. The launcher searches for `python3` or `python` and verifies Python
3.8+ before running Python code. No Python means no capture and an actionable failure. Capture and
comparison use only the Python standard library. Git is needed for commits/transfers, not capture.
Export additionally requires Gitleaks with `dir`, `--ignore-gitleaks-allow`, and decoding support.
The integration tests were run with Gitleaks 8.30.1; any unsupported scanner invocation fails closed.

The launcher does not install packages or assume sudo, Homebrew, apt, curl, or an internet connection.
Use the machine's supported package manager to install missing prerequisites. On a Mac already using
Homebrew, `brew install python gitleaks` is one route. On an appliance, use its supported Python
package and a Gitleaks binary matching its OS/CPU. See the [official Gitleaks installation
instructions](https://github.com/gitleaks/gitleaks#installing) and release checksums.
Run WSL copies on its Linux filesystem so private output permissions work as intended.

Gitleaks is a detector; `--redact` hides findings in its output, **not in the scanned source files**.
The scrubber here performs the actual replacements. Upstream currently describes Gitleaks as feature
complete with future security patches; this narrow scanner integration does not depend on new
features. See [upstream documentation](https://github.com/gitleaks/gitleaks).

## 2. Resolve global, family, and local capture rules

```sh
zsh dotfiles.zsh capture --label mac --family mac
zsh dotfiles.zsh capture --label nas --family nas
zsh dotfiles.zsh capture --label work-wsl --family wsl
```

Run the appropriate command on each machine. Family is explicit: a generic Linux kernel cannot tell
us whether this is a NAS, Pi, work machine, or something else. WSL/NAS/Pi inherit the Linux layer.
The current family files are deliberately small until captures justify additional rules.

Precedence:

1. `capture-policy.json`: global file/directory allowlist and exclusion patterns.
2. `policies/linux.json` for Linux-derived families, then `policies/<family>.json`.
3. Optional private overlay passed with `--local-policy .private/capture.local.json`.

Each overlay may add `patterns`, `excludes`, and `exclude_components`. Corresponding
`remove_patterns`, `remove_excludes`, and `remove_exclude_components` lists remove
exact entries inherited from earlier layers. Removals happen before additions in that layer.
An included file still loses to an exclusion: remove the exclusion explicitly if it is intentional.

`patterns` entries select files or directories and accept case-sensitive wildcards: `*`, `?`, and character classes such as `[ab]`.
For example, `.config/.shell_*` captures the matching shell files without listing each one.
Patterns match one path component at a time (`*` does not cross `/`) and include dotfiles.
Overlapping entries are deduplicated. Exclusions still apply, and expansion never traverses an
excluded or symlinked directory. Unmatched/incomplete patterns are recorded under `patterns` in the
private manifest; missing literal paths are recorded as `missing`. Matched files are copied;
matched directories are recursively captured, including when selected by a wildcard. Exclusions
prune that recursion. Recursive `**` patterns are unnecessary and remain unsupported. Overlay removal lists remove the exact pattern entry,
not its expanded matches; use `excludes` to omit one file from a wildcard selection.

`excludes` uses case-sensitive relative-path glob matches, including ancestor paths. Python glob
matching here allows `*` to span slashes. `exclude_components` matches individual path components,
case-insensitively, so a private directory is pruned at any depth. Default component patterns are
conservative and can exclude legitimate settings: inspect the recorded statuses. `.git` and symlink
following remain prohibited independently of overlays.

Example private overlay:

```json
{
  "patterns": [".config/example/settings.json", ".config/utils"],
  "remove_patterns": [".config/nvim"],
  "excludes": [".config/utils/work-only.sh"]
}
```

Existing local capture policies must combine their old `files` and `directories` lists into
`patterns`, and replace their removal lists with `remove_patterns`. Old capture manifests remain
readable by comparison/export; export maps still use `files` for explicit source/target mappings.

The complete resolved policy is embedded in the private capture manifest for reproducibility.
Filename inventory stays private too. Do not commit machine-local policy paths or work details.

## 3. Select export files and define replacements locally

Use the capture directory printed by the collector:

```sh
zsh dotfiles.zsh init-export --capture .private/<capture-id> --rules .private/export.local.json
```

This creates a mode-600 local JSON file with the captured file list and a home-directory replacement.
It refuses to overwrite an existing map. Edit it locally: remove files that should not be shared,
rename sensitive target paths, and add known values to replace. Never paste the real map into chat,
put real values in command-line arguments, or commit it. A fictitious example of its shape:

```json
{
  "files": [
    {"source": ".zshrc", "target": ".zshrc"},
    {"source": ".gitconfig", "target": ".gitconfig"}
  ],
  "replacements": [
    {"value": "/home/example", "placeholder": "__HOME__", "files": ["*"]},
    {"value": "person@example.invalid", "placeholder": "__GIT_EMAIL__", "files": [".gitconfig"]},
    {"value": "fictional-private-value", "placeholder": "__API_TOKEN__", "files": ["*"]}
  ]
}
```

Replacements are exact literal strings, longest first in one pass; they are not executable regexes.
Use the same semantic placeholders across machines. Match exact sensitive values, not overly broad
short strings. Replacement rules can be file-scoped, but **any known original left anywhere in the
candidate, including a target filename, blocks export**. Add encoded variants explicitly if needed;
the scanner also checks common encodings to a depth of three. No complete decoding guarantee exists.

Entire private files should be omitted rather than transformed into a meaningless wall of redactions.
Shared code with a few embedded values is a good candidate for replacements. Future deployment can
move these values to local includes or a secret store; this evidence step does not install placeholders.

## 4. Build and scan a private candidate

```sh
zsh dotfiles.zsh export --capture .private/<capture-id> --rules .private/export.local.json
```

The command verifies captured file hashes, sanitizes selected files into a new private candidate,
checks for remaining known values, rejects unredacted literal credential assignments, then scans
the whole candidate with Gitleaks default rules. The assignment check covers simple variable
assignments (including `export`) whose names contain password, passwd, secret, token, or API-key
terms. Empty values, semantic placeholders, and direct variable references are permitted; other
values require review. This is an additional guard, not a complete shell/configuration parser.
Inherited scanner configuration, local ignore files, and inline allow comments cannot suppress this
scan. Missing scanner, failed scan, unknown flags, nonempty findings, or missing report block export.
Reports/logs stay private; they may include private context even with scanner redaction enabled.

The command prints a candidate directory and digest after a clean scan. Review every candidate file
locally, including filenames and manifest. Review for personal/work context as well as credentials:
scanners cannot recognize every internal endpoint, name, custom password, or business detail.
If anything needs changing, edit the rules or recapture; do not edit the candidate directly.

## 5. Approve the exact candidate and commit it

```sh
zsh dotfiles.zsh export --capture .private/<capture-id> --rules .private/export.local.json --reviewed <full-digest>
```

This rebuilds and rescans from the original capture/rules, requires the exact reviewed digest, and
moves the sanitized result to `evidence/snapshots/<alias>/<digest-prefix>/`. It refuses to overwrite.
The manifest contains sanitized-file hashes and original permission modes, not original-content
hashes, home inventory, replacement values, or private capture policy. No raw hash of a credential
file is published as a potentially guessable fingerprint.

From a clean working branch on that machine, commit only the printed snapshot path:

```sh
git status --short
git add -- evidence/snapshots/<alias>/<digest-prefix>
git diff --cached --stat
git diff --cached
git commit -m "Capture sanitized settings for <alias>"
```

Ensure no unrelated changes are staged before committing. Do not modify an approved snapshot; create
a new one through export. There is no globally installed Git hook and nothing prevents a deliberate
`git add -f .private`: the supported workflow enforces the gates, arbitrary Git commands do not.

Once a remote is chosen, use a separate capture branch per machine, push its sanitized commit, then
merge or cherry-pick into the analysis checkout. Without a remote, transfer only that commit using a
Git bundle or the reviewed snapshot directory. Do not transfer raw work captures to a personal repo.
The tooling never automatically stages, commits, pushes, or publishes captures.

## 6. Compare the committed file trees

```sh
zsh dotfiles.zsh compare evidence/snapshots/mac/<id>/manifest.json evidence/snapshots/work-wsl/<id>/manifest.json
git diff --no-index -- evidence/snapshots/mac/<id>/files evidence/snapshots/work-wsl/<id>/files
```

`git diff --no-index` exits 1 when differences exist. The manifest comparison distinguishes content
and permission changes. It conservatively marks files omitted by one export as unresolved rather
than assuming they do not exist on that machine. Both command output and file diffs are now based on
committed, reviewed evidence, so analysis can happen later without access to the original machines.

Comparison is of **sanitized structure**, not original secret equality. Two different tokens mapped
to `__API_TOKEN__` compare equal intentionally. Consistent placeholder names prevent irrelevant
identity differences from obscuring meaningful configuration differences.
