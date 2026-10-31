# Initial inventory

Reviewed 2026-10-31. This is a working-tree inventory, not a reconstruction of every historical commit.

| Source | Finding | Treatment |
| --- | --- | --- |
| `dotfiles` | Sync script, JSON configuration, and documentation; no tracked settings tree. README has an existing user modification. | Preserve; useful as workflow history, not a configuration baseline. |
| `dotfiles-mac` | Older settings tree, package list, and the same sync-script approach. | Compare selected files; do not re-run its automatic sync. |
| Current Mac | Substantial shell drift and additional terminal/editor configuration. | Private allowlisted snapshot plus reviewed evidence. |
| Existing chezmoi source | No commits; one untracked `dot_zshrc`, different from both live and legacy `.zshrc`. | Preserved privately; not an authoritative source or completed migration. |
| `ai-config` | Owns AI guidance/skills; recognizes `.gitconfig` and owns a Git template and global ignore rules. | Keep ownership intact until a deliberate handoff. |
| NAS / work WSL / Pi | Not captured in this session. | Pending; do not extrapolate from the Mac. |

The generated user guidance was newer than its source fragments and companion configuration, so no
guidance recomposition was needed. Neither legacy dotfiles repository had an OKF index. This new
repository uses ordinary documentation; no OKF bootstrap was requested.

## Problems with the old collection approach

The old Mac policy copies `.config/` broadly. Its tracked tree includes private-named configuration,
editor history/buffers, container machine state, a binary settings database, and many vendored syntax
files. Tracked names establish the boundary problem; this review did not audit secrets in Git history.

The shell copy uses `*`, which omits hidden directory entries, so its policy also cannot reliably
refresh the hidden `.shell_*` files it depends on. The script reads its JSON relative to the caller's
working directory, although the README suggests cron invocation by absolute script path. Automated
mode stages everything and pushes, rather than limiting the commit to reviewed configuration.

The new collector never executes either old script. Raw captures are explicitly private; committed
evidence is curated. Existing private-named files are not copied into the new repository.

## Proposed configuration boundaries

These are classification proposals, not applied changes or proof of cross-machine agreement.

| Area | Proposed scope | Decision needed |
| --- | --- | --- |
| Basic shell ergonomics, editor defaults, prompt preferences | Shared when the application exists | Compare NAS/WSL preferences; keep shell-specific syntax out of common POSIX fragments. |
| Homebrew initialization, platform utility flags, OS paths | Platform | Detect capabilities and use macOS/Linux sections; do not spread Mac paths globally. |
| Developer language managers and SDK paths | Role plus capability | Mac exports mention multiple Node managers; choose an intended setup instead of merging all PATH additions. |
| Service-management aliases and work tooling | Role | Keep work and server responsibilities separate; review commands before sharing. |
| User identity, local paths, endpoints, private environment values | Local or work-owned | Use native includes/local files; exclude sensitive values from personal Git. |
| Prompt, micro bindings/settings, terminal preferences | Shared candidate plus optional app | Similarity does not prove all machines want the application installed. |
| tmux, Vim/Neovim, Kitty, PowerShell | Optional app / role | Newly captured here, not automatically mandatory on NAS or Pi. |
| Utility scripts | Review individually | A symlink-conversion helper changes files; never execute it during collection. |
| Histories, caches, editor buffers, container VM state | Excluded | Do not migrate as configuration. |
| Vendored nano syntax files | Dependency, pending version choice | Prefer a pinned upstream dependency over an unexplained historical copy. |
| Git settings and AI configuration | Existing `ai-config` ownership | Avoid two tools writing the same target; decide on ownership before activation. |

## Next sequence

1. Run the collector on NAS and work WSL (Pi when available); review work evidence in place.
2. Extend the allowlist for meaningful gaps in each machine's name inventory. Identify custom XDG,
   shell, and appliance locations; do not recursively copy a home directory.
3. Compare captures, record intended behavior per configuration area, and resolve the Node manager,
   Git ownership, shell compatibility, and local-value decisions.
4. Confirm the recommended manager, build a minimal managed source tree, and render each platform/role
   into a disposable home. Check shell syntax and startup without running unreviewed captured code.
5. Preview a small Mac pilot, retain recoverable backups, apply that explicit scope, and verify.
6. Add an AI maintenance skill once the source layout and update workflow are stable. Archive old
   workflows only after replacement is verified on the relevant machines.

No remote has been created. Repository hosting and visibility remain a later publishing decision;
the initial local commit is sufficient for reviewing scripts and sanitized evidence.
