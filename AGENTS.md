# Repository workflow

This is an evidence and migration repository. Capture is read-only against source machines.
Never execute captured scripts, source their shell files, or auto-apply a dotfile manager.

- Treat `.private/` as sensitive local evidence. Never stage, force-add, publish, or quote its contents.
- Commit only reviewed generic evidence, gated sanitized snapshots, and sanitized intended configuration.
- Follow `docs/capture-workflow.md` for family rules, replacement maps, scanning, and snapshot review.
  Never bypass export gates or treat scanner success as proof that all private context was removed.
- Keep shared defaults, platform differences, role differences, and host-local values distinct.
- Mark unavailable evidence as pending; do not invent NAS, WSL, or Pi configuration.
- `ai-config` already owns AI guidance and some Git configuration. Resolve ownership before deployment.
- Preserve existing source repositories and user edits.
- Run `python3 -m unittest discover -s tests -v` after collector/comparator changes.
- A future AI maintenance skill should inspect drift, classify changes, edit explicit managed files,
  preview the target diff, validate it, and stage only reviewed portable changes.
