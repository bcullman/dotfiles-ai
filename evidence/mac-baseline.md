# Reviewed Mac baseline

Collected 2026-10-31. This committed summary contains no raw configuration values, usernames, hostnames,
endpoints, credentials, or home-directory paths. Exact bytes and manifests remain in ignored local
captures. Findings describe selected files, not an exhaustive backup.

## Provenance

- `dotfiles` revision: `9be6aff322fa00a1938da65ba3b94637b05fd048`; tracked content is the old
  collection workflow. An existing README edit was preserved.
- `dotfiles-mac` revision: `fe428f7480070a029e677f8f062be2908be85a31`.
  Capture read its **working tree** `src/`, not a Git archive. One captured file,
  `.config/htop/htoprc`, is not tracked; do not attribute it to that commit.
- Legacy capture: `legacy-mac-20261031T190300448208Z`, 18 captured files.
- Live capture: `mac-20261031T190300404098Z`, 41 captured files.
- Existing chezmoi source: separate private capture `chezmoi-existing`; no commits and one untracked
  `dot_zshrc`. Its contents differ from both live and legacy files.
- Capture policy: repository `capture-policy.json` at the initial commit; each private manifest also
  embeds its policy. Historical capture metadata describes the collecting Mac, not an inferred old OS.

## Exact comparisons

Of 15 files captured on both sides, 12 have different contents and three have identical contents.
Three utility scripts also have different permission modes. These measurements do not establish
which version is preferable.

| Files | Evidence | Proposed treatment |
| --- | --- | --- |
| `.zshrc`, `.zprofile` | Contents changed; line counts 17→34 and 1→6. | Separate common shell behavior from Mac initialization and optional integrations. |
| `.config/.shell_alias` | Changed, 79→98 lines. | Review aliases individually for shared versus platform/role commands. |
| `.config/.shell_exports` | Changed, 19→52 lines; contains multiple language-tool/PATH integrations. | Resolve intended tool ownership and platform paths before merging. |
| `.config/.shell_completers`, `.config/.shell_utils` | Contents changed. | Include only available tools; review sourced helper behavior. |
| `.config/starship.toml`, `.config/micro/settings.json`, `.nanorc` | Contents changed. | Shared preference candidates, subject to application/version compatibility. |
| `.gitconfig` | Contents changed. | Reconcile with `ai-config` ownership before migration. |
| `convert-symlinks.sh`, `term-colors-demo.sh` under `.config/utils/` | Contents and modes changed. | Review behavior and intended executable modes. |
| `.config/utils/term-colors-list.sh` | Contents identical; mode changed. | Resolve mode; possible common utility. |
| `.config/micro/bindings.json` | Identical. | Strong shared candidate if micro is installed. |
| `.config/htop/htoprc` | Identical; legacy copy is not tracked. | Working-tree evidence only. |

Legacy-only selected files: `.bashrc`, `.bash_logout`, `.zsh_logout`. Absence from this Mac is not proof
that Linux machines should lose them.

Live-only explicitly selected files: `.tmux.conf`, `.vimrc`, Kitty configuration, btop configuration,
PowerShell profile, and the optional OpenClaw completer. Neovim also has a captured configuration tree
absent from the legacy source. Directory descendants appear conservatively as unresolved in the
generic comparator when the other manifest has no individual file record; its missing-directory
record provides the additional context here.

## Limitations

The collector omits credential stores and private/local files intentionally. Most application
directories are name-inventoried only. Shell dependencies, external include paths, macOS preferences,
system services and package versions are not captured transitively. Raw files were not executed.
No claim of safe installation or full startup validation is made.

NAS, work WSL, and Pi comparisons remain pending actual captures. Tool selection and configuration
classification are provisional until those inputs establish their requirements.
