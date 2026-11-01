# Sensitive snapshot history cleanup

The user authorized rewriting published history and resynchronizing the NAS checkout after the
Mac–NAS comparison revealed an unredacted service password in the earlier Mac evidence snapshot.

## Completed

- Enumerated the published refs: only `main` was present; no additional branches or tags were found.
- Used the official git-filter-repo v2.47.0 sensitive-data-removal workflow to remove the entire
  affected Mac snapshot path from local history. The corrected 352-file snapshot remains intact.
- Verified that the current Git tree was unchanged by the rewrite and that all 406 reachable
  historical blobs lacked the specific affected password. The affected old blob was also no longer
  readable from the local Git object database after cleanup.
- Published the rewritten branch using an explicit expected remote revision with force-with-lease.
- Verified the NAS had no uncommitted work, unexpected commits, or extra refs before resetting it to
  the cleaned remote branch. Expired its reflogs and pruned the affected old object.
- Verified all 2,247 existing Mac private workspace files and all 48 NAS private workspace files
  were unchanged. No raw captures or replacement values were transferred or committed.

The rewritten implementation/comparison commit is `6ab409b`; subsequent documentation commits record
this cleanup. The existing NAS evidence commit is now `d1a7e6b`.

## Remaining limitations and actions

Credential rotation is still required and was not performed. Rewriting Git history cannot invalidate
a password or remove copies outside the repositories we control. GitHub cached views, pull-request
references, backups, forks, and unknown clones may retain historical material. No claim is made that
GitHub's internal object storage or caches have been purged. GitHub documents contacting Support for
eligible cached-view/reference cleanup in its
[sensitive-data removal guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

Both known active checkouts are on the cleaned history. Any additional old clone must be cleaned or
recloned before use; merging an old branch into the cleaned branch can reintroduce removed history.

Private captures intentionally still contain original settings and remain excluded from Git. The
export workflow now rejects simple literal credential assignments independently of Gitleaks and has
a regression test using a synthetic punctuation-heavy password. Neither check is a complete privacy
or secret-detection guarantee.
