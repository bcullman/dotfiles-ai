# Mac and NAS configuration comparison

Evidence: Mac `a6dfc5b4ee7e23d6` (352 files) and NAS `b753781a9fc1abfb` (11 files).
The NAS evidence arrived in commit `3808aec`. All file contents were checked against their manifests.
Work WSL and Pi remain pending. No live settings were changed or captured scripts executed.

## Evidence limits

The Mac has 341 paths not represented in the NAS snapshot; the NAS has no unique paths. Exported
snapshots do not include missing/excluded-file records, so a one-sided path does not establish that
the application or file is absent from the machine. Much of the Mac count is vendored plugin/syntax
code, not independent preferences.

Replacement numbering is local to each machine. Different `__LOCAL_PATH_*__` markers cannot establish
whether original paths were equal. The NAS whole-line `__REMOTE_COMMAND__` marker masks behavior as
well as values. The previous privacy review conservatively masked some generic example paths in
comments. Do not treat these redaction differences as configuration decisions.

## Shared and different settings

| File | Observed difference | Proposed scope or next decision |
| --- | --- | --- |
| `.config/.shell_utils` | Byte-identical; sources the same three helpers. | Shared, after reviewing each helper's behavior. |
| Three files under `.config/utils/` | NAS adds a final newline. Mac modes are 755; NAS modes are 644. | Same source behavior; normalize text and choose modes deliberately. Sourced scripts need not be executable. |
| `.zshrc` | Same basic exports/aliases/completion/helpers/prompt structure. Mac adds OpenClaw, GitHub CLI completion, Homebrew NVM initialization, and additional tool paths. NAS initializes completion here and selects emacs keybindings. | Shared startup skeleton, optional integrations, platform initialization. Initialize completion once. |
| `.config/.shell_alias` | 64 shared nonempty lines. Mac uses eza; NAS uses exa. Help behavior, Python aliases, tool aliases and mounted paths differ. | Shared aliases where commands exist; platform/capability-specific variants; local mounted paths. |
| `.config/.shell_completers` | Different matching styles; NAS invokes dircolors; Mac initializes compinit in this file. | Choose shared matching preferences; guard optional tools; align initialization ownership. |
| `.config/.shell_exports` | Shared editor/color/Go basics. Mac adds SDK/tool settings, Docker architecture/build choices, and secret placeholders. NAS enables Volta and sets terminal and locale values. | Platform and developer-role paths; choose Node ownership per role; secrets belong in local includes or a secret store. |
| `.config/starship.toml` | NAS enables repo truncation, an eight-component truncation length, and a directory substitution that are commented on Mac. | User preference decision; no evidence this must be platform-specific. |
| `.nanorc` | Mac uses tab width 2 and guide-stripe options; NAS uses width 4 and zap. Include lists differ. | Choose shared editing preferences with version-aware options and managed syntax dependencies. |
| `.config/btop/btop.conf` | Headers identify versions 1.4.0 and 1.2.3. Color/background, ordering, CPU graphs, I/O display and network scaling differ; Mac has extra version-specific settings. | Separate version differences from presentation preferences; do not blindly copy the newer file to the older application. |

Of the 11 shared paths, one is byte-identical, three differ only by final newline plus mode, and
seven have substantive content differences (including some redaction artifacts).

## Issues to resolve during normalization

1. Both completion files contain a concatenated line joining `list-suffixes`, another `zstyle`, and
   a PATH export. Shell syntax validation alone would not establish its intended behavior; split
   and validate these statements during implementation.
2. Both export files add `/snap/completion.zsh.inc` to PATH. PATH expects executable directories;
   determine whether the intention was to source a completion script. The Mac also retains Linux
   snap paths, suggesting historical drift.
3. NAS aliases retain Homebrew commands and a macOS hosts-file path. Its observed account mapping
   also makes `sudo` change from UID 0 to a nonzero UID. Treat this appliance as an explicit exception,
   not as evidence for how all Linux hosts should behave.
4. The ls wrappers assume eza/exa is installed when invoked without arguments. Add a real capability
   check if the intended behavior is fallback to ordinary ls.
5. Both alias files define `portkill` with command substitution around lsof. That executes lsof while
   sourcing the file and makes its output the alias value; it does not create the apparent intended
   runtime command. Resolve intent before adopting it.
6. NAS `.nanorc` has 90 includes whose files are not represented in its snapshot. All 89 active Mac
   includes have corresponding captured files. Check the NAS source paths, skipped symlinks, and
   collection manifest before concluding those dependencies are missing on disk.
7. The shared symlink-conversion helper copies to a symlink path then removes that path. It is not a
   safe general-purpose conversion algorithm as written, especially for relative link targets.
   Do not run it or promote it simply because both machines contain it; retire or repair separately.

## Privacy correction discovered during comparison

The earlier Mac snapshot contained a literal service password that the default scanner and prior
review missed. The corrected snapshot replaces it, and export now independently checks literal
credential assignments. Tests include a synthetic punctuation-heavy password, and the actual prior
snapshot was verified to fail the new guard without printing its value.

The prior snapshot was already pushed. Rotation of the affected Scrypted password is needed, and
history cleanup requires explicit authorization and coordination with the NAS clone. Removing the
old tree at HEAD does not purge prior commits. No history rewrite or credential rotation was done.

## Next steps

Finish credential remediation, collect work WSL, then implement shared shell defaults with separate
platform/role/local layers. The evidence continues to fit the proposed chezmoi approach, but this
comparison does not activate a manager or select final editor/prompt preferences on the user's behalf.
