# Windows atomic replacement: established practice and M6 scope

Research date: 2026-09-30. This report evaluates the unfinished Windows writer in [the ExecPlan](ExecPlan.md), not native client loading. Research makes no implementation or contract change.

Decision update, 2026-09-30 20:24Z: The user subsequently approves ordinary-rights DACL and mandatory-integrity-label preservation and explicitly rejects additional Windows requirements. Comprehensive arbitrary audit-SACL preservation is not guaranteed and is not a universal support gate. Keep existing ownership, ancestor identity, conflict and authenticated recovery protections; refuse known unsupported metadata loss without elevation. Implementation resumes with one public install/update/recovery slice. This approval changes the execution policy, not the research evidence below.

Authority packet review, 2026-10-06: the corrected T002 decision packet in [ExecPlan.md](ExecPlan.md#checkpoint-6a-define-metadata-publication-and-recovery-authority) has actual independent parent approval in [progress.txt](progress.txt), bound to exact packet bytes and a preserved snapshot. T002 is `passes: true`; 6A is done/met/checked. Former unattributed approval remains withdrawn and its provenance unverified. The design defines creation/replacement/pruning authority, authenticated already-restored states, second-interruption rollback, whole-transaction read-only preflight with mutation-boundary rechecks, retained originals until durable transaction commit, and journal removal last. Its finite 15-point public plan overlaps lifecycle tasks T003-T014, not a literal 1:1 task mapping. No implementation, metadata experiment, product test or T003 work is authorized by design approval; future 6B empirical proof remains required.

## Conclusion

**The blanket audit-SACL preservation requirement appears over-scoped relative to the established implementations inspected.** CPython, Git, Rust, .NET and VS Code have practical Windows publication paths without wrapper-level inspection or verification of the displaced file's complete audit policy. None of the cited paths requests `SeSecurityPrivilege`. That supports reconsidering our requirement, not claiming that security metadata is irrelevant or that the underlying APIs never preserve it.

The important distinction is between ordinary atomic file publication and this installer's stronger ownership, ancestor-identity and recovery contract. Mature-project examples inform the first problem; they do not automatically solve the second. Keep existing race and recovery protections. Do not introduce elevation or silently discard a known integrity label.

## Established implementations

These are widely deployed runtimes or tools with long-maintained Windows code. Their adoption motivates selection, not a security verdict. Links pin the inspected files to immutable commits.

| Project and source | Actual implementation | What it establishes |
| --- | --- | --- |
| [CPython `os.replace`](https://github.com/python/cpython/blob/db3ffd065ca31e3c0c7c3a4f313102b3e3564fb9/Modules/posixmodule.c#L6370-L6411) | Windows calls `MoveFileExW` with `MOVEFILE_REPLACE_EXISTING`; POSIX uses `rename` or `renameat`. | A mainstream replacement primitive needs no bespoke complete-security-descriptor copying. This wrapper is path-based on Windows and lacks our ancestor-pinning guarantee. |
| [Git Windows rename](https://github.com/git/git/blob/bca240abc33443ea4bc62d02688725f9d2e2589a/compat/mingw.c#L2527-L2646) | Prefers `SetFileInformationByHandle(FileRenameInfoEx)` with replace/POSIX flags; falls back to `MoveFileExW` on unsupported systems. Opens the source leaf with `FILE_FLAG_OPEN_REPARSE_POINT`; retries sharing failures. | Handle-based publication is established practice. Protecting the source leaf is not equivalent to protecting every ancestor or a parent-relative destination. Git's copy-allowed fallback is not suitable for our single-volume transaction without separate justification. |
| [Git staged-file commit](https://github.com/git/git/blob/75e05f6bc3b3e04301d25327f54b2c9998471c1d/tempfile.c#L335-L356) | Closes the temporary file, calls `rename`, then releases temporary-file bookkeeping. | Staging followed by publication is ordinary application design. Git's lock-file protocol is not our authenticated preimage/postimage journal or automatic recovery. |
| [Rust `fs::rename`](https://github.com/rust-lang/rust/blob/4592a842b4c6455b3ab9f5afe20377719daf6537/library/std/src/sys/fs/windows.rs#L1306-L1350) | Calls `MoveFileExW`; on access denied, tries a DELETE-access source handle and `FileRenameInfoEx`. The comment describes bypassing the read-only attribute. | A practical native fallback addresses Windows compatibility without a complete ACL/SACL transfer layer. It does not establish our metadata-preservation or recovery contract. |
| [.NET Windows `File.Replace`](https://github.com/dotnet/runtime/blob/a064f10785a00344fbf863e9b9255a036167700c/src/libraries/System.Private.CoreLib/src/System/IO/FileSystem.Windows.cs#L88-L96) | Calls `ReplaceFileW`. Passes `REPLACEFILE_IGNORE_MERGE_ERRORS` only when `ignoreMetadataErrors` is true. The [public three-argument overload](https://github.com/dotnet/runtime/blob/185098c1bc77ae4d771a8dbc4f00ff8b2572fa68/src/libraries/System.Private.CoreLib/src/System/IO/File.cs#L1048-L1060) defaults it to false. | A respected implementation delegates metadata merging to the OS and normally surfaces merge errors. This is a useful design reference, not evidence of complete audit-SACL preservation. |
| [VS Code rename retries](https://github.com/microsoft/vscode/blob/e0bfcd60b41dbbc43bd0a29973f32887f6d77cd2/src/vs/base/node/pfs.ts#L497-L563) | Wraps Node rename with retry/backoff for transient Windows locking errors; includes copy/delete fallbacks. | Mature tools spend effort on real-world sharing and antivirus failures. These fallbacks do not provide our transaction atomicity, ancestor safety or authenticated recovery. |

CPython, Git publication, Rust and both .NET source locations above were additionally fetched and checked directly against their cited line ranges after the delegated survey. This report describes the inspected paths, not every write operation in those repositories.

## Metadata: what the evidence does and does not say

Microsoft's [ReplaceFileW reference](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-replacefilew) explicitly lists creation time, short filename, object identifier, DACLs, security resource attributes, encryption, compression and additional named streams as preserved. DACLs define access permissions. Security resource attributes are not synonymous with all audit policy.

The documented list does not explicitly promise owner-SID, arbitrary audit-SACL or mandatory-integrity-label preservation. An omitted guarantee is **not proof of loss**. Similarly, callers that do not copy metadata themselves might delegate preservation to the OS. This survey does not establish hidden audit-SACL behavior either way.

Microsoft documents that [full audit-SACL inspection](https://learn.microsoft.com/en-us/windows/win32/secauthz/sacl-access-right) requires `ACCESS_SYSTEM_SECURITY` and `SeSecurityPrivilege`. The failed attempt to require that privilege for every installer operation added a substantial compatibility barrier absent from the inspected publication paths.

Official error-semantics correction, 2026-10-06: a fresh fetch of the [ReplaceFileW reference](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-replacefilew) confirms 1175 retains both original names. For 1176, a supplied `lpBackupFileName` retains both names; without it, the replaced file no longer exists while replacement retains its original name. For 1177, the replacement retains its original name but has inherited streams/attributes, and the replaced file exists under a different name (the supplied backup name when present). Name retention does not establish untouched replacement metadata. These are documented outcomes, not new measured failures or transaction proof. `ReplaceFileW` remains rejected as the selected writer.

The isolated local candidate reportedly dropped an existing mandatory integrity label during replacement. That is a concrete regression, not merely a hypothetical audit-policy edge case. Ordinary-rights label handling was subsequently demonstrated experimentally, but the candidate remains disabled and unapproved. Proposed DACL/label preservation is our own policy informed by that counterexample; it is not a blanket guarantee shared by these projects or by the `ReplaceFileW` reference.

## Comparison with the accepted POSIX boundary

Our current POSIX writer stages an independent file, applies the intended mode, and replaces a directory entry. It does not explicitly copy the displaced inode's owner, ACL or extended attributes. Replacement retains the new inode's metadata; it is inaccurate to say that POSIX rename "preserves nothing."

Requiring Windows to authenticate and preserve every security-descriptor component therefore adds a stronger metadata contract than the existing POSIX code explicitly implements. Platform differences still matter: a Windows integrity label can enforce access independently of a DACL, so POSIX parity alone does not justify dropping a known label.

Likewise, none of this establishes equivalence for concurrent parent substitution. Retained parent authority, preimage checks, postimage checks, ownership validation and journal reconciliation remain separate requirements. A popular path-based API cannot substitute for those protections merely because other tools use it.

## Recommended decision and implementation direction

The approved owned-file metadata contract preserves DACLs and mandatory integrity labels at ordinary rights, or refuses their replacement; retain explicit refusal for known unsupported metadata loss such as named streams until preservation is implemented. Comprehensive arbitrary audit-SACL preservation is not guaranteed and is not an implicit universal gate. **The user approves this policy on 2026-09-30; no additional Windows requirements are introduced.**

Keep the staged-file publication design, ancestor/reparse protection, exact ownership and conflict checks, and authenticated interrupted-operation recovery. Preserve every existing regression. The historical recommendation for one public install/update/recovery slice does not renew an expired budget: the next implementation objective is T003 only after separate new bounded authorization. T002 design approval does not authorize an implementation experiment; do not build another disabled general-purpose security-descriptor facade.

Evaluate `ReplaceFileW` as a metadata-merging reference, not a drop-in safe writer. It takes paths and documents partial-mutation failures, including a missing or renamed original. Any use needs a justified namespace-safety composition and journal coverage of those states. Its ignore-metadata-error flags must not become a shortcut around preservation.

## Limits and research friction

The survey is evidence for a narrower practical requirement, not proof that our current contract is impossible or permission to redefine its threat model. Native build/filesystem coverage, ordinary-rights label round-tripping, complete audit-SACL behavior and any kernel-mediated replacement composition remain unproved.

GitHub CLI authentication returned 401. Public source verification used unauthenticated GitHub REST/raw fetches instead; no credentials or local/private source were transmitted. Initial findings overclaimed metadata behavior and conflated leaf-reparse handling with ancestor protection. This final report corrects those claims and distinguishes documented guarantees from observations and recommendations. No Gemini CLI specific task was executed. No product implementation is included in the research deliverable.
