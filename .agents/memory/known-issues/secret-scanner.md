---
type: Known Issue
description: Scanner consistency limits; read when changing candidate reads or making claims about concurrent index/worktree edits.
---

# Secret Scanner Observation Consistency

The scanner does not establish an atomic snapshot of the Git index and working tree. Candidate enumeration uses multiple Git queries; index and worktree content are read afterward. Its scan-log lock does not lock repository content. A clean result therefore describes the versions observed during that scan, not a guarantee covering concurrent edits.

Evidence: the [canonical scanner](../../../hooks/families/scan_secrets.py) separates enumeration from `SnapshotSource` acquisition. All index reads, including singletons, use pinned object IDs. Worktree acquisition reads a checked descriptor into a private spool; classification and matching replay that captured content without reopening the path. These protections do not make enumeration, index metadata, worktree capture, and later diffs one atomic operation. In-place writes to the same inode during capture remain outside an atomic-snapshot guarantee.

The [public merge regressions](../../../scripts/test-scan-secrets-merge.py) verify singleton index pinning, conflicts, unsafe reads, and limits. The [streaming regressions](../../../scripts/test-scan-secrets-streaming.py) and [capture regressions](../../../scripts/test-scan-secrets-capture.py) cover snapshot replay, path replacement, growth, and bounded acquisition. These specific controls do not establish race freedom for arbitrary concurrent repository mutation.

Checked 2026-10-14 against current source and tests. Recheck when candidate enumeration, content reads, repository snapshot/locking behavior, or concurrency coverage changes. Keep race-freedom claims outside the verified contract until corresponding evidence exists.
