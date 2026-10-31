# Dotfile manager evaluation

Recommendation as of 2026-10-31: **chezmoi**, provisionally pending NAS and work WSL captures.
This is a comparison of established approaches that fit the request, not a claim to enumerate every
dotfile project. The ranking is a judgment against this inventory, not a benchmark.

Priorities, in order: a simple daily workflow; explicit machine differences; previewable changes;
maintained documentation and distribution; minimal custom glue; predictable AI-assisted maintenance.

| Approach | Strength | Cost for this inventory | Verdict |
| --- | --- | --- | --- |
| chezmoi | Separate intended source and live files, templates/ignores for differences, diff/apply workflow, broad binary distribution. | Learn its source naming and template syntax; keep templates small. | Best fit. |
| yadm | Familiar Git-like workflow in the home directory; OS/host alternates, templates, encryption. | Home is the working tree; source/live separation is less explicit. Alternates need careful organization as differences grow. | Strong runner-up if direct editing is the dominant preference. |
| GNU Stow | Small, mature symlink model; straightforward app packages and dry-run support. | Platform/role selection, rendered fragments, secrets and drift policy need conventions or extra tooling. | Best for mostly identical files; more glue here. |
| Bare Git with home as work tree | Only Git required; transparent version history. | Alternate files, safe installation, local overrides, and onboarding are a custom workflow. | Simple mechanism, insufficient complete solution for this task. |
| Dotbot | Declarative bootstrap with linking and commands; easy to read. | Primarily installation orchestration; ongoing reconciliation and shared/platform logic still need design. | Useful bootstrap tool, less complete match. |
| Nix Home Manager | Declarative home configuration plus package management. | Introduces Nix and a broader environment-management model; appliance suitability needs checking. | More system than this task currently needs. |
| Existing custom sync scripts | Familiar and already present. | Broad capture, hidden-file omissions, automatic staging, no reliable normalization/install model. | Retire after migration; do not expand into another manager. |

Primary sources: [chezmoi differences](https://www.chezmoi.io/user-guide/manage-machine-to-machine-differences/),
[chezmoi daily operations](https://www.chezmoi.io/user-guide/daily-operations/),
[yadm overview](https://yadm.io/), [yadm alternates](https://yadm.io/docs/alternates),
[GNU Stow manual](https://www.gnu.org/software/stow/manual/stow.html),
[Git command options](https://git-scm.com/docs/git),
[Dotbot repository](https://github.com/anishathalye/dotbot),
[Home Manager project](https://github.com/nix-community/home-manager).

## Support and portability evidence

chezmoi's official release page showed v2.73.3, released 2026-10-20, and multiple preceding releases.
Its install documentation provides package and binary routes, verification instructions, and platform
guides. This supports choosing an actively maintained project with documented distribution, not a
promise of commercial support or proof that a specific NAS appliance can run it.
See [releases](https://github.com/twpayne/chezmoi/releases) and
[installation](https://www.chezmoi.io/install/). Check the NAS OS/CPU and WSL constraints before rollout.

Stow's documented 2.4.1 release and focused manual support its maturity; a slower release cadence alone
does not imply abandonment. yadm documents the core multi-machine capabilities required here. No
ranking is based on unverified star counts or an assertion that alternatives are unmaintained.

## Keep chezmoi simple

Use one source tree with ordinary files where possible. Add small templates only for genuine platform
or role differences. Prefer native application includes for private/local values. Do not create a
branch per machine or a second custom rendering framework. Keep machine-local identity out of Git.

Keep evidence/docs/scripts separate from the eventual managed home tree using chezmoi's supported
source-layout mechanisms when implementing the migration. No source layout has been activated yet.
Resolve ownership with `ai-config` before importing Git files or AI tool settings.

The intended daily workflow after setup is:

```sh
chezmoi status
chezmoi diff
chezmoi edit ~/.zshrc
chezmoi diff
chezmoi apply ~/.zshrc
```

Review/stage/commit the corresponding source change in Git. For edits made directly to live files,
inspect drift and reconcile the explicit file into source; do not blindly re-add every managed file,
especially templates. Keep automatic commit/push disabled initially. On another machine, fetch and
review before applying. These commands describe the proposal; they were not run against this Mac.

## Future AI maintenance skill contract

The skill should identify the active source repository and target profile, inspect Git status and
manager drift, classify the requested change, preserve local values, edit only the authoritative
source, render/validate affected profiles, show the deployment diff, and stage only reviewed portable
files. Record exceptions and pending machines explicitly. The skill should reuse the manager's
operations rather than implement a second synchronization system.

Write and install that skill after the first migration establishes the real workflow. For now,
`AGENTS.md` documents the evidence boundary and the intended maintenance sequence.
