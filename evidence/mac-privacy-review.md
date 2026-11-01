# Mac snapshot privacy review

Reviewed on 2026-10-31 (America/Los_Angeles).

Snapshot: `snapshots/mac/b5dd9f9a5d04abc9/`.
Full reviewed digest: `b5dd9f9a5d04abc95ec8bc4b6a0fdc9f34521893ed10093a60689319d9ccbd9a`.

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
