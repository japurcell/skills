---
type: Known Issue
description: Scanner consistency limits; read when changing candidate reads or making claims about concurrent index/worktree edits.
---

# Secret Scanner Observation Consistency

The scanner does not establish an atomic snapshot of the Git index and working tree. Candidate enumeration uses multiple Git queries; index and worktree content are read afterward. Its scan-log lock does not lock repository content. A clean result therefore describes the versions observed during that scan, not a guarantee covering concurrent edits.

Evidence: the [canonical scanner](../../../hooks/families/scan_secrets.py) separates `collect_unmerged_files` and `collect_files` from `read_candidate_bytes`; its locking protects log writes. The [public merge regressions](../../../scripts/test-scan-secrets-merge.py) verify stable conflict fixtures, deletion resolution, findings, unsafe reads, and limits. They do not establish behavior under concurrent repository mutation.

Checked 2026-10-07 against current source and tests. Recheck when candidate enumeration, content reads, repository snapshot/locking behavior, or concurrency coverage changes. Keep race-freedom claims outside the verified contract until corresponding evidence exists.
