# Mac snapshot privacy review

Reviewed on 2026-10-31 (America/Los_Angeles).

Snapshot: `snapshots/mac/a6dfc5b4ee7e23d6/`.
Full reviewed digest: `a6dfc5b4ee7e23d6fbe338f2b02653c52aef382fde7dfe9b46a5246f008fe7c4`.

Correction: the earlier snapshot passed Gitleaks but retained a literal service password. The
comparison review caught it, added an explicit replacement, and rebuilt this snapshot. A new
independent literal-credential assignment check blocks that original snapshot. The prior version
has now been removed from the published branch history and both known clones through an authorized
rewrite. Credential rotation remains outstanding; cached server views and unknown copies are not
covered by the clone cleanup. See the [cleanup record](../docs/history-cleanup.md).

The snapshot preserves all 352 selected files as sanitized evidence, including application settings,
syntax definitions, plugins, and completion data. It is not intended for installation. Raw captures,
replacement values, backups, and scanner reports remain in the ignored private workspace.

Four credential replacements were established before this review. This review added 19 literal
replacements covering local identities, user-specific paths, nonstandard reference URLs, and a local
hostname. Some nonstandard references were conservatively masked without determining whether the
endpoint was public. Existing file selections and prior replacement rules were preserved.

Review used local identity matching, path and network-reference classification, credential scanning,
and structural checks. It did not execute captured configuration, verify credential validity, or
independently audit all third-party plugin code. Known upstream references and attribution were
retained except where a global replacement also matched them.

Final checks confirmed:

- All 352 selected file paths match the sanitized manifest, and each file matches its recorded hash.
- No configured original replacement value remains in exported contents or filenames.
- Additional checks found no literal user-home paths, RFC 1918 IPv4 addresses, or names ending in
  `.lan`, `.internal`, or `.corp`.
- Gitleaks completed successfully with zero findings; promotion rebuilt and rescanned the candidate
  and required the exact reviewed digest.

These checks reduce disclosure risk but do not prove the absence of every private detail. Placeholder
equality is not original-value equality. Compare this tree as configuration evidence, retaining the
private originals on their source machine for any later clarification.
