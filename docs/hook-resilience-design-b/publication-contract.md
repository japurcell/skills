# Publication feasibility contract

This is the retained D0 decision record for [the Design B plan](ExecPlan.md). It covers disposable source experiments, not a deployed gate. The laboratory prototype must never be installed into a user repository. Production implementation, installation, provider migration, and native platform acceptance retain their own plan gates.

## Decision and support boundary

The tested macOS/SHA-1/basic-HTTP path is feasible: exact delivery binding, complete late-secret detection, measured capacity headroom, and cancellation cleanup all have retained proof. Promote these constraints into T3 and T5-T7; the prototype remains a laboratory artifact. The tested design uses immutable Git OIDs, a parent-owned temporary directory, a separate scanner process, and a real pinned Git LFS uploader reading a private verified store. No saved result authorizes another invocation. There is no background checkpoint or real-service publication.

Observed platform: macOS 26.7.1 (25G241) / Darwin 25.6.0, arm64; Git 2.54.0 (Apple Git-157); Python 3.14.6; Git LFS 3.8.0 (`aece9221`, darwin arm64, Go 1.27.0). The prototype parses SHA-1 Git repositories only. SHA-256 Git repositories, Linux, native Windows, HTTPS authentication, SSH Git transport, pure SSH LFS, alternate LFS transfer agents, submodules, hook managers, and custom LFS upload scripts have no acceptance evidence here. They must be explicitly refused or receive their missing proof before being advertised as supported. This does not remove their requirements from the main plan.

The Git LFS binary is disposable at `/tmp/design-b-lfs-3.8.0/git-lfs-3.8.0/git-lfs`. Its [official release](https://github.com/git-lfs/git-lfs/releases/tag/v3.8.0) archive SHA-256 is `caff76a7d070d8160c89bc39b6e85d98f24135b6fed038a3b4de2590d25102d8`, matching the official release checksum file. The PGP signature was not independently verified. No global installation occurred. The [versioned Git LFS configuration source](https://github.com/git-lfs/git-lfs/blob/v3.8.0/docs/man/git-lfs-config.adoc) documents the storage override used in the experiment; its Git source blob is `61936ed207bbb737e7ebccf0176ad9f23dd6e4f9`.

## Baseline failure

[baseline.json](d0/baseline.json) records 24 native JSON source responses: read, attempted repair command, completion, and repeated completion for three providers and two workloads. Complete provider-local bundles were copied into disposable homes. Every result was incomplete with enforcement `deny`; the index and all worktree file bytes were fingerprinted unchanged after every call. These commands were proposed in provider envelopes and were not executed after denial.

Both historical merge commits were available locally. An isolated shared-object clone checked out `e5c2be2095ba30626559adae7fb2c49ba691734e` and merged `5f3948c92e5037fb066321e9c9e5b03419410671` with hooks disabled only inside that fixture. The replay produced 223 pending snapshots totaling 9,453,698 bytes. The scanner reported `total_bytes_limit/git_index`, measured 8,403,665 bytes, limit 8,388,608 bytes. The original incident state/log was not recovered; this is a repeatable reconstruction from the named commits.

The binary workload uses six synthetic binary files with the six reported PNG sizes, totaling 20,026,474 bytes, plus 19 bytes of text. It is not a copy of the original PNGs. Its seven snapshots trigger `total_bytes_limit/candidate_read` at 9,238,768 bytes against 8,388,608. Candidate ordering differs from the historical report's 9,264,664-byte observation.

Codex `Stop` is the completion enforcement baseline. Copilot `sessionEnd` and Gemini `SessionEnd` are the existing registered lifecycle routes, whose source adapters also return failure responses. Their session-end events are advisory under the saved provider contracts; these subprocess results do not establish that either deployed host can enforce turn completion there. They must not be relabeled as live `agentStop` or `AfterAgent` delivery proof. No installed home hook or trust setting was changed.

## Transaction and delivery binding

[transaction.json](d0/transaction.json) records actual local Git pushes through the disposable dispatcher. The scanner receives Git's original four-field tuples, including destination arguments, and computes a digest over those exact inputs. The dispatcher verifies the returned transaction identity and gives each preserved hook the original arguments and a fresh stdin copy. Two preserved hooks ran in order `1,2`, with identical stdin and arguments.

The real push checks cover a non-HEAD branch, explicit OID, three refs in one transaction, new refs, deletion, forced update, and an annotated tag. Remote refs were inspected with Git. A preserved hook moved a local branch after inspection; the bare remote still received the original OID from the checked tuple. A fake credential introduced in an intermediate commit and removed from the latest tree still caused rejection and no corresponding remote ref. A replacement object masking that blob did not hide it because inspection and fixture verification used `--no-replace-objects` and `GIT_NO_REPLACE_OBJECTS=1`. This agrees with the [Git pre-push interface](https://git-scm.com/docs/githooks#_pre_push) and [replacement-object behavior](https://git-scm.com/docs/git-replace).

The production collector must preserve B5: subtract only complete locally available remote-old graphs from the same transaction; otherwise traverse all local reachable objects without fetching. It must include intermediate blobs, commit/tag messages, and all relevant path occurrences. Unsupported graft/shallow substitutions and missing local objects are incomplete. [path-control.json](d0/path-control.json) additionally proves that an incremental update cannot reuse an already-published safe blob under a new `credentials` filename: the path rule rejects and the remote ref remains unchanged. [failed-path-before.json](d0/failed-path-before.json) retains the pre-fix false allow. Filename policy now runs before byte-deduplication skips; remote-old graph verification uses protected, bounded capture and contributes to enumeration, capture, and temporary accounting.

The prototype's functional binding proof does not replace T5's complete malformed-input, missing-history, partial-clone, SHA-256, audit, and ambient-configuration matrix.

## LFS handoff

[lfs.json](d0/lfs.json) records a real Git LFS uploader using a loopback HTTP batch/upload endpoint. The dispatcher creates a mode-0700 invocation directory, invokes the scanner as a separate process, keeps ownership until upload completes, validates the transaction-bound handoff, and removes that directory on success or rejection. The handoff is a mode-0600 JSON file containing the transaction digest and exact payload OID/size pairs. Payload files are private, hash-verified copies made read-only before delivery.

The scanner uses the maintained `SnapshotSource` to acquire LFS payloads and the maintained streaming matcher to inspect their full bytes. The dispatcher validates the handoff identity and payload digest/size again, then invokes the real uploader with `-c lfs.storage=ABSOLUTE_PRIVATE_STORE`, a controlled loopback LFS URL, basic HTTP transfer, one transfer worker, and bounded network waits. A deliberately overwritten original `.git/lfs/objects` file did not change the uploaded bytes. The server received exactly the original 106,496-byte verified payload once.

The experiment first ran `git lfs install --local --force` inside the fixture, captured its standard pre-push hook, and replaced that standard uploader with the controlled invocation. The standard hook SHA-256 was `a52d0510d0f8c75e27852156ec6f7791f0d8ed65fc58fcc368dd1de0a60a1d74`. It was not also preserved as an ordinary downstream hook. Installation must recognize exact supported standard forms, retain their user-visible upload behavior, and reject custom/ambiguous upload arrangements. T7 must implement that recognition and refusal; the prototype is not an installer.

A secret-bearing payload, missing/corrupt original payload, and missing/corrupt private handoff each rejected before upload. Rejections made zero additional batch requests and transferred zero payload objects. Ctrl-C at the acquired-handoff boundary returned failure, left no canceled remote ref, and removed private temporary content in 0.0062 seconds. Cancellation during active transfer and native Windows descendant cleanup remain production acceptance cases; no claim is made that already transmitted bytes could be recalled.

## Capacity policy

The following schema-1 profile is the decision input for production validation. Counts and bytes are integers; seconds must be finite positive numbers. Boolean, missing, unknown, duplicate, non-finite, and out-of-range settings are invalid configuration. Configuration comes from the explicitly selected owner file pinned by installation, never automatic repository discovery or ambient skip/warn settings.

| Setting | Checkpoint default | Publication default | Allowed checkpoint range | Allowed publication range |
| --- | ---: | ---: | --- | --- |
| `max_objects` | 4,096 snapshots | 20,000 Git/LFS objects | 1-16,384 | 1-100,000 |
| `max_candidate_bytes` | 67,108,864 | 268,435,456 | 1,048,576-536,870,912 | 1,048,576-1,073,741,824 |
| `max_seconds` | 30 | 120 | 1-120 | 1-600 |
| `max_capture_bytes` | 134,217,728 | 536,870,912 | 1,048,576-1,073,741,824 | 1,048,576-2,147,483,648 |
| `max_temp_bytes` | 268,435,456 | 805,306,368 | 1,048,576-2,147,483,648 | 1,048,576-3,221,225,472 |

Publication transaction input separately has a 1,048,576-byte cap, 4,096-record cap, and two-second absolute acquisition/parse deadline. A terminal is invalid stdin. Empty completed stdin is a valid empty transaction and runs no upload-capable hook. The laboratory dispatcher assumes Git's completed pipe; T5 must implement and publicly test the adversarial open-pipe/terminal/deadline parser before activation.

`max_candidate_bytes` charges full logical candidate volume, including repeated relevant blob/path occurrences and LFS payloads, rather than only storage deduplication. `max_capture_bytes` bounds aggregate inspected Git capture; `max_temp_bytes` bounds concurrent private material. A single file has the same finite aggregate protection, with no extension exemption or truncation. Limits are independent: being below one does not guarantee completion if another is reached. The allowed override intervals are finite admission limits, not promises that every combination completes within its time or machine resources. Their extrema have not all been benchmarked.

The defaults provide substantially more than the incident volumes, permit first publication and history inspection, and retain headroom for captures plus the private LFS handoff. The largest measured objects are 64 MiB, and the long-history fixture is deliberately larger in logical scan volume than its acquired storage. The prototype materializes individual Git objects with `read_bytes()` before feeding bounded chunks into the real matcher. Its RSS measurements belong to that implementation and do not prove a streaming production memory bound. The supported recovery is to inspect the reported bound, increase that explicit setting within the admitted range if appropriate, or repair history/storage, then rerun. It never suggests skipping, warning-only enforcement, binary exclusions, or a prior clean status.

[capacity.json](d0/capacity.json) is the final passed frozen run. Each publication row below had a complete-clean actual push and a first-publication late-secret rejection. Bytes are decimal counts. Object counts are distinct Git objects; the LFS row additionally acquired one payload. `Temp` is conservative private logical-byte high-water accounting from protected capture sizes, private copies, and invocation files, not filesystem allocation blocks. RSS is the scanner process high-water; dispatcher and Git-child RSS, split phase times, and output byte counts remain separately recorded in the JSON.

| Publication workload | Logical bytes | Acquired bytes | Git objects / paths | Capture bytes | Temp bytes | Scan seconds | Scanner RSS bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| first-publication | 20,026,653 | 20,026,887 | 8 / 6 | 20,027,647 | 24,155,367 | 0.249 | 60,325,888 |
| merge-sized | 9,453,877 | 9,462,797 | 225 / 223 | 9,487,867 | 9,505,190 | 2.839 | 44,236,800 |
| repeated-blobs | 33,554,611 | 267,187 | 3 / 128 | 275,519 | 529,331 | 0.048 | 44,335,104 |
| multi-ref | 12,585,828 | 12,586,570 | 39 / 25 | 12,589,902 | 13,635,114 | 0.579 | 44,957,696 |
| long-history | 135,181,482 | 999,116 | 1,539 / 1,025 | 1,132,948 | 1,000,234 | 19.213 | 44,793,856 |
| large-blob | 67,109,043 | 67,109,080 | 3 / 1 | 67,109,283 | 134,217,944 | 0.580 | 111,050,752 |
| large-lfs | 67,109,176 | 67,109,213 | 3 / 1 | 552 | 134,218,868 | 0.585 | 44,138,496 |

The largest logical volume was 135,181,482 bytes across 513 commits, leaving 1.99 times headroom against the 256 MiB publication byte default. Its 19.213-second inspection leaves 6.25 times time headroom against 120 seconds, and its 1,539 Git objects leave approximately 13 times count headroom. The largest private logical high-water was 134,218,868 bytes, leaving approximately six times headroom against the 768 MiB temporary default. The largest ordinary Git capture volume was 67,109,283 bytes, leaving approximately eight times headroom against 512 MiB. These are single controlled workload observations, not p95/throughput claims or guarantees for every permitted budget combination.

The 64 MiB ordinary blob consumed 111,050,752 bytes scanner RSS. The 64 MiB LFS case consumed 44,138,496 bytes scanner RSS and 99,450,880 bytes dispatcher RSS; its endpoint received exactly 67,108,864 verified bytes in one payload. The dispatcher includes private-store re-verification and the real uploader. Per-process high-water values are not a sum or a simultaneous process-tree RSS measurement.

Supplemental checkpoint controls called the copied generated entrypoint with only disposable constant changes: the six-image volume scanned clean in 0.333 seconds at 34,144,256 bytes native maximum RSS, and 223 synthetic snapshots totaling 9,453,698 bytes scanned clean in 0.250 seconds at 34,193,408 bytes RSS. Both emitted three stdout bytes and detected a final added credential control. The 64 MiB byte default leaves 3.35 times headroom for the image volume. The merge-sized checkpoint control reproduces snapshot count/volume, not the exact unresolved merge topology; the baseline above retains that separate topology proof. These supplemental external-process checks do not expose the publication prototype's internal phase/capture/temp counters.

[capacity-control.json](d0/capacity-control.json) proves repeated contents are charged logically (24 MiB plus commit content) despite approximately 1 MiB acquired content, and that a 24 MiB explicit bound rejects as incomplete. [large-control.json](d0/large-control.json) proves an embedded credential after 64 MiB in the same binary yields findings rather than incomplete. No truncation or extension exclusions were used.

## Evidence and reproducibility

Run from the repository root. The LFS binary is required; a missing binary is a failed prerequisite. These scripts create and clean disposable repositories. The loopback endpoint needs local socket permission. The capacity command must run with other hook tests and benchmarks paused.

```sh
rtk proxy python3 docs/hook-resilience-design-b/d0/d0-baseline.py --source "$PWD" --output /tmp/d0-baseline.json
rtk proxy env D0_SOURCE="$PWD" D0_LFS=/tmp/design-b-lfs-3.8.0/git-lfs-3.8.0/git-lfs D0_EVIDENCE=/tmp/d0-functional python3 docs/hook-resilience-design-b/d0/d0-test.py
rtk proxy python3 docs/hook-resilience-design-b/d0/d0-capacity.py --source "$PWD" --lfs /tmp/design-b-lfs-3.8.0/git-lfs-3.8.0/git-lfs --output /tmp/d0-capacity.json
```

The five public-process checks passed in 10.843 seconds after the final fixture-only maintenance isolation. Their tests were added in vertical red/green slices through actual CLI and Git/LFS process boundaries. [failed-large-before.json](d0/failed-large-before.json) retains the original 64 MiB rejection and old prototype fingerprint: the prototype changed a context-manager wrapper's globals instead of the scanner's globals, so the maintained 8 MiB Git capture cap remained active. A >8 MiB clean/embedded-late-secret test reproduced the failure before the binding correction, then passed. No runtime hook source or production limits were changed. Earlier pipe-based exploratory timings are not capacity acceptance.

[history-setup-failure.json](d0/history-setup-failure.json) preserves a separate fixture failure: native Git stopped at version commit 263 with an invalid HEAD/ref/reflog object, four packs, and a multi-pack index. The repository had not explicitly requested packing. Automatic maintenance racing rapid commit construction is a hypothesis, not an established cause. Fixture-local `gc.auto=0` and `maintenance.auto=false` removed that uncontrolled setup activity; a new 513-commit repository completed construction and `git fsck --full` returned zero before measurement. No user configuration was changed. [capacity-attempt-2.json](d0/capacity-attempt-2.json) keeps the preceding partial observations; they are not promoted as a completed capacity run. [capacity-before-review.json](d0/capacity-before-review.json) retains the earlier completed candidate before the path-policy review; it is superseded by the remeasured source in `capacity.json`. Every paired control in the final run asserts logical candidate volume at least as large as its clean workload; the multi-ref control republishes all twelve branch histories to fresh refs alongside its credential control.

[installation-scope.json](d0/installation-scope.json) records Git's effective hook paths and configuration origins for relative/absolute local `core.hooksPath`, common-local inheritance in a linked worktree, and a worktree-specific override. A common-local binding affects linked worktrees; an enabled `extensions.worktreeConfig` override does not change the primary worktree's effective path. T7 must determine and explain that scope before mutation, keep its dispatcher in a repository-owned directory, and preserve the original path/origin for exact restoration. No global configuration or shared hook directory was mutated.

No production CLI, gate installation/uninstallation, audit/status contract, provider retirement, home deployment, host event delivery, remote service, native Windows, Linux, or CI acceptance is established by these artifacts. The maintained scanner does raw supported text matching and binary ASCII projection, without image OCR or archive extraction. Arbitrary malicious local hooks, intentional bypass, and unrelated network tools remain outside the configured-workflow guarantee.
