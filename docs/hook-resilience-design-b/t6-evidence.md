# T6 verified local LFS publication evidence

This is the scoped T6 delivery record for the private `codex/design-b-t6` branch, based on `65a48edb50cc98f8328d1e62c799f722cba5082a`. The primary owns plan reconciliation, integration, T7 installation, and the final K1 knowledge pass. No external push, real-home installation, global Git mutation, production repository gate installation, trust change, or enablement change occurred. Test pushes used disposable bare Git repositories and a recording loopback HTTP endpoint.

## Runtime boundary

`gate pre-push` remains inspection-only. It recognizes canonical v1 SHA256 LFS pointers smaller than 1024 bytes, rejects unsupported/invalid encodings, obtains the payload only from ordinary local common-Git-directory LFS storage, captures it through held no-follow ancestry, and verifies its declared byte size and SHA256 before canonical full-content matching. It never downloads a missing payload. Git and LFS distinct-object counts share the existing publication object limit. Pointer bytes, distinct payload bytes, and logical repeated path/payload bytes remain separate; no extension skip, diff suppression, ambient warning permission, or per-payload shortcut is introduced.

The new explicit production entry is:

```sh
scan-secrets dispatch pre-push --repo REPOSITORY --binding OWNER_BINDING -- REMOTE URL
```

The isolated source and installed `scan-secrets.py` use the same runtime closure. `scan_lfs.py` owns local payload capture; `scan_private.py` owns invocation-only files and held-inode cleanup; `scan_dispatch.py` owns request/result/handoff admission and ordered downstream work. Existing protected metadata and subprocess capture primitives are shared. The neutral closure is exactly 19 executable assets; provider runtime helper closure remains 8. New helpers are included by the existing neutral installer's literal `MODULES` inventory without changing generator/manifest implementation or inventing another installer.

A parent-owned invocation directory survives the scanner subprocess and is removed after downstream completion/failure/cancellation. Its request and handoff bind the exact transaction, destination, repository, build, policy, raw budget digest, binding digest and a fresh random nonce. Payload records contain only fixed-format OID, size and relative private path. The caller validates the complete scanner result and required-audit outcome, validates every handoff record and private payload, and makes another verified private copy for the controlled uploader. It rechecks handoff/payload/config/tool bytes after any prior hook before upload. The uploader sees an empty private Git repository, verified private LFS storage, and explicit configuration; it imports no source config/index/HEAD/.lfsconfig, global helper, custom agent, source LFS skip environment, or credentials.

Preserved hooks execute at their original paths with original arguments and the exact captured stdin once per listed step. The caller captures/pins their bytes before any downstream step and revalidates them through held ancestry before original-path invocation. This preserves `$0`/dirname/sibling-file behavior. It is not a claim that hostile same-owner modification after the final verification is atomically excluded or that arbitrary hook code cannot bypass local controls. T7 owns recognizing/refusing installed arrangements and replacing exactly the standard LFS pre-push step with `{ "kind": "lfs" }`; this task exposes production runtime composition through temporary fixture bindings, not installation recognition.

Empty transactions execute no downstream hook or uploader. A non-LFS binding has `lfs: null`, `endpoint: null`, and no LFS step, so it needs no LFS executable or endpoint. A successful LFS step may have transferred bytes before a later preserved hook fails; the runtime preserves the failure status and records the completed LFS object count. Already transmitted bytes cannot be recalled. No saved status, queue, receipt, background checkpoint or retry grants permission.

## Binding and limits for T7

The owner-only schema 1 JSON binding is bounded to 128 KiB and 32 ordered downstream steps and has exactly these fields: `schema_version`, `build`, `repository_identity`, `interpreter`, `data_directory`, `budget_file`, `downstream_seconds`, `remote`, `url`, `endpoint`, `lfs`, `steps`. `interpreter` is the current resolved absolute interpreter. `data_directory` is the absolute pinned scan-secrets data directory; ambient XDG redirection does not redirect the configured scanner audit. `budget_file` is null for built-in profiles or an absolute owner-selected file LOCATION. Each invocation captures that file's exact bytes once into its private directory, validates both profiles, and binds the raw digest. Editing the selected file within ranges and retrying works without reinstalling or canonicalizing its bytes.

An LFS tool record has exactly `path`, `sha256`, `version`; the admitted version is 3.8.0. Steps are ordered hook records (`kind`, original absolute `path`, `sha256`) or one LFS marker. Hook/tool hashes, exact destination and runtime build are binding inputs, not values borrowed from an untrusted response. Malformed bindings or budgets return invalid exit 3; required infrastructure, unsupported arrangements or invalid handoffs return 2; findings return 1; cancellation returns 130. Safe downstream nonzero exits propagate, including signal exits as 128 + signal. Safe JSON diagnostics/recovery never replay hook/uploader stdout or stderr, payload bytes, raw exceptions or credential-bearing URLs.

Inspection uses the unchanged admitted publication profile. Downstream steps share a separate explicit 1-600 second deadline. Their capture accounting continues the invocation aggregate; scanner captures are reconciled before any hook. Private payload/tool/config captures and repeated verification reads are charged. The dispatcher reports a conservative composed temporary reservation peak alongside the scanner's actual counters, accounting parent-resident state plus scanner peak rather than presenting them as an exact simultaneous measurement. Cleanup has an independent ten-second/finite-entry/depth bound and clears only the held invocation inode; replacing its pathname cannot redirect recursive deletion onto foreign contents. Finding a renamed owned root is limited to its held immediate parent.

The uploader uses documented `lfs.basictransfersonly=true`, one concurrent transfer, `lfs.allowincompletepush=false`, and `push --object-id --stdin` for the exact admitted OID set. Retry configuration uses the documented minimum `maxretries=1`, `maxretrydelay=0`, `maxretrytime=1`; zero retries is NOT claimed. The parent deadline/process-group cleanup remains authoritative over waits and server Retry-After responses. The old D0 `maxretries=0` behavior is historical feasibility evidence only.

## Observed support and prerequisites

Observed host: Darwin 25.6.0 arm64, Git 2.54.0 (Apple Git-157), Python 3.14.6. The pinned real executable is `/tmp/design-b-lfs-3.8.0/git-lfs-3.8.0/git-lfs`, Git LFS 3.8.0 (`aece9221`), 13255424 bytes, executable SHA256 `8cb21d1fa650af82a06eaa98c6078303bacf2f101199be3d77ab7370ec712bd0`. D0 retained the official archive/checksum provenance; this task rechecked executable bytes and version, not independent PGP provenance. The suite accepts `TEST_GIT_LFS` or a version 3.8.0 `git-lfs` on PATH; a missing/wrong executable is a failed prerequisite, never a passing skip.

Verified LFS acquisition/upload support is deliberately limited to native macOS ordinary local storage, canonical pointers without extension transforms, SHA1 Git for upload, and the pinned basic-HTTP implementation. HTTP is allowed only for loopback fixtures; HTTPS configuration is accepted, but authenticated hosting, native Windows/Linux LFS execution, SSH/custom transfer agents, alternate storage/includes/extension arrangements and universal server compatibility are not established here. Unsupported arrangements refuse explicitly. Non-LFS SHA256 Git behavior is preserved separately. Native Windows dispatch currently reports `dispatch_platform_unsupported`; its implementation/proof remains a T7/native obligation, not completed platform acceptance. Existing non-LFS scanner platform paths remain unchanged.

## Public red/green and activated controls

All credential controls are unmistakably fake and assembled at runtime. Tests use subprocess CLI boundaries, production dispatcher runtime, actual local Git pushes, and real Git LFS requests. The recording endpoint checks batch requests, payload objects AND received byte counts; unchanged Git refs alone are not transfer evidence.

Observed implementation reds and repairs:

- Re-encoding the last handoff check accepted a post-admission whitespace edit and performed a real upload. Hashing the exact raw bytes now rejects that change with zero transfer.
- Post-success cleanup faults retained phase `complete`; a cleanup KeyboardInterrupt also retained a clean outcome. One terminal-failure constructor now replaces outcome, exit, phase, reason, diagnostic and recovery together while retaining actual transmitted-object counts. The paired controls cover ScanFailure, generic failure, cancellation and override of a downstream 47 return.
- Dispatch initially labeled a complete-findings scanner result as incomplete. It now preserves the validated complete-findings/1 classification, safe original scan phase/recovery/counts and zero transfer.
- Persistent named payload files initially left scanner temporary accounting when graph resources closed. A real minimum-budget control could then create an over-budget private file before handoff. Named files remain charged through handoff emission; the same write is now rejected before creation.
- Private `budget.json` staging I/O was incorrectly called invalid configuration/3; it is now outside the narrow document-validation catch and remains infrastructure/2. Owner-selected current files with mode 0666 or a second hard link initially authorized upload; each invocation now validates uid, ordinary type, single link and absence of group/other write permission through its held source descriptor. Ordinary owner 0644/0600 edits still work.
- Historical pre-LFS publication reports were incorrectly marked corrupt after counter extension. The informational reader accepts exactly either complete known counter shape, while gate-result admission keeps the current strict shape.
- Missing dispatch arguments exposed a human-output KeyError traceback/1 although JSON mode returned3. Both modes now produce bounded safe invalid-argument exit 3 results.

- A clean local payload initially returned `lfs_unsupported`; local capture/full matching now verifies clean, secret, missing/corrupt, wrong size/digest, invalid pointer, symlink and late-failure cases.
- The first actual dispatcher push failed with `invalid_arguments`. After dispatch existed, one early human reporting branch failed after a successful upload; it was repaired and is not characterized as a zero-transfer rejection.
- Original-path sibling hooks produced empty output when invoked from copied paths; original-path invocation repaired the behavior. A semicolon endpoint was truncated from `/tenant;retained/objects/batch` to `/tenant/objects/batch`; consistently quoted Git config preserved it exactly.
- A valid selected budget followed by malformed bytes returned 2 instead of 3; the repaired same-binding sequence validates exact raw digests, returns3 for invalid configuration, then accepts repaired bytes without reinstalling.
- A normal root-owned `/var` TMPDIR alias failed at binding; both verified `/tmp` and `/var` aliases now pass through narrow root-owned alias handling.
- Whole invocation-root replacement initially caused cleanup to delete a foreign sentinel. Held-inode cleanup now preserves the replacement and removes the renamed owned original with zero transfer.
- Replacing the whole root before handoff initially wrote `handoff.json` into the foreign replacement. The scanner now keeps the original invocation handles through graph teardown, required audit, handoff and display persistence; the public replacement control leaves foreign inventory unchanged.
- A failed handoff initially saved a historical complete-clean report despite returning incomplete. Display persistence now follows final handoff classification; the resident-budget control queries public status and sees the final incomplete reason.
- Cancellation during scanner acquisition initially left the child's `scan-checkpoint-*` directory. The dispatcher-controlled scanner converts SIGTERM into stack unwinding; the public control requires both scanner and dispatcher private storage empty and child PID gone.
- A hook that made its stdout capture world-readable then exited 47 initially propagated 47. Final private-capture verification now rejects it as infrastructure failure 2; ordinary safe 47 still propagates.

Honest counterfactual controls (the repairs preceded these tests):

- Restoring raw-path payload creation in a disposable source variant writes the captured payload into a foreign directory after an ancestor swap. Current held-directory creation leaves foreign inventory/bytes unchanged, and both variants deny before transfer.
- Restoring charge-after-open leaves one live descriptor on a real temporary-budget failure. The current pre-open charge leaves descriptor inventory unchanged. The fixture uses the approved minimum budget, not mocked accounting.
- An exploratory 700-payload run stayed below 128 KiB and was not a valid metadata-cap red. The retained 900-payload actual-push pair activates the restored 128 KiB cap (zero-transfer denial) and then publishes every current-runtime payload under unchanged B4 budgets. The read bound is derived from admitted object count and fixed record shape; it is not an arbitrary smaller metadata cap.

Active-transfer cancellation observes positive bytes received before SIGINT, inventories native PID/PPID descendants, requires their disappearance and private cleanup before releasing the server stall, and does not claim that sent bytes were recalled. A separate before-upload cancellation requires zero requests/objects/bytes and no surviving hook child.

## Validation record

The complete reproducible suite is `rtk proxy python3 scripts/test-scan-secrets-lfs.py`. Frozen build: `baa8dc584d3c4e3edeadc787975b48e824c311b90aa80347f5a252b657b4dc3b`. Final 43-case full runs pass on Python 3.14.6 in 65.018 seconds and Python 3.13.14 in 64.877 seconds. Both use that exact build. The second command is `rtk proxy /Users/adam/.pyenv/versions/3.13.14/bin/python3 scripts/test-scan-secrets-lfs.py`. Affected final serial compatibility results are recorded below. Earlier 41-case full runs passed on Python 3.14.6 (66.324 seconds) and 3.13.14 (65.504 seconds); those runs preceded the final held-handoff lifetime, status and scanner-cancellation repairs. A 42-case Python 3.14.6 run passed in 64.362 seconds before the last two repairs. Meaningful failed observations are preserved above rather than replaced with passing repeats.

Final serial compatibility on the frozen build:

| Command | Observed result |
| --- | --- |
| `rtk proxy python3 scripts/test-scan-secrets-git-gates.py` | 62 pass, 47.675 seconds |
| `rtk proxy python3 scripts/test-scan-secrets-cli.py` | 35 pass, 17.780 seconds |
| `rtk proxy python3 scripts/test-scan-secrets-status.py` | 29 pass, 15.187 seconds |
| `rtk proxy python3 scripts/test-install-scan-secrets.py` | 21 pass, 39.925 seconds after canonical freshness repair |
| `rtk proxy python3 scripts/test-generate-hooks.py` | 26 pass, 17.765 seconds |
| `rtk proxy python3 scripts/test-hook-diagnostic-recovery.py` | 16 pass, 63.024 seconds |
| `rtk proxy python3 scripts/generate-hooks.py --check` | Current, 62 generated files |
| `rtk proxy python3 scripts/test_test_all.py` | 14 pass, 11.236 seconds; exact 58-suite inventory |

Previously observed compatibility checks during implementation: 62 gate cases, 35 CLI cases, 29 status cases and 21 neutral installed cases pass. An initial gate run failed on the new exact status count keys plus the old missing-payload reason expectation; those contracts were repaired. An initial installed run failed because generated assets were stale and its maximum-closure fixture still added 42 modules to the now 19-file closure. Canonical regeneration and 39/40 extra-module boundary fixtures preserve the exact 58-asset/64-entry maximum and its next-entry rejection; 21 installed cases then passed. One 33-case LFS run passed 32 cases and exposed a SHA256 fixture that supplied 40 zeroes instead of the actual OID width; the fixture now supplies its actual width.

Affected generated-provider checks were run serially before the final neutral-only CLI/status repairs: `bash scripts/test-codex-hooks-secrets-scanner.sh`, `env OBSERVABILITY_LOG_PATH=/tmp/design-b-t6-copilot-obs.jsonl bash scripts/test-hooks-secrets-scanner.sh`, and the equivalent Gemini scanner suite all passed. Each retained all four block/warn x clean/findings native-capture controls, native errno 35, retained/clamped hard-limit behavior, restored soft limit, capture-failure behavior and no-HEAD behavior. The shared source identities did not change afterward: `scan_git.py` SHA256 `477d20d49d0c148e0fc35a2db56d5ba4d48d5be752044e6b6fa230575e5c22aa`, `scan_types.py` SHA256 `57f6116d711302a3c106556caa4f6ed98aa60a7b2e5a8f6cd78081b914e6581e`. Later neutral entrypoint changes are outside that executable helper closure, while the canonical identity generator still hashes those sources as described below. The earlier tested provider scanner SHA256 identities were Codex `c8cf34ef6165a395af426beedb3092b3e1d742ea5fe733205a740445795267e0`, Copilot `0f17824d3ee98d6766225ade3c9b54d2d495e14e7a3e97976e2de4554c0d953d`, Gemini `84aa9933de5bceaec6f13d8e15c079e7e52c03d940c52e064541bd10d151eaf7`.

The first frozen installed run passed 20/21 cases and failed the real main-installer case because six generated scanner/diagnostic files were stale after neutral runtime changes. Canonical `python3 scripts/generate-hooks.py --write` refreshed those six metadata outputs. `hooks/families/reporting.py` intentionally includes every runtime source in the scanner REPORT_BUILD digest, so neutral-only changes also refresh embedded REPORT_BUILD and DIAG_BUILD/ASSETS. Shared scanner helper bytes above remain unchanged. Final generated scanner SHA256 identities are Codex `24f0d887bc499a473d58be61d4ec791d7ca8c738cbc55958ebc8f0e0c046f679`, Copilot `d1c24712f7de685edbd4cd1b3a574c916a598b974fca4abee26e87363100fa79`, Gemini `f63206b7e28f9b4fa20722ecc2708269f0593d2cfd000d39182b55bd1ade6798`. The final generator, freshness, main installer and diagnostic-recovery checks cover those refreshed active identities; unchanged long scanner/capture workloads are not falsely represented as rerun against these later metadata bytes.

Affected banner/reporting functional coverage passed: `test-security-banners.py` 14 cases (5.868 seconds) and `test-security-reporting.py` 14 cases (69.934 seconds). Those two disposable-fixture functional runs briefly overlapped; these are not characterized as isolated serial timing or performance proof. No later change touched their functional source/helper closures; final canonical metadata regeneration changed only embedded build/recovery identities as described above. The maintained test runner now lists exactly 58 suites, including the new `python3 scripts/test-scan-secrets-lfs.py`; registry coverage checks the complete set and exact list cardinality.

The primary must independently review/integrate this private delivery before T7. Native Windows, authenticated provider/server delivery, production repository installation and the coordinated K1 pass remain outside this T6 proof.

## Official sources used

- [Git LFS 3.8 pointer specification](https://raw.githubusercontent.com/git-lfs/git-lfs/v3.8.0/docs/spec.md): canonical pointer framing, SHA256 and size, 1024-byte limit.
- [Git LFS 3.8 push command](https://raw.githubusercontent.com/git-lfs/git-lfs/v3.8.0/docs/man/git-lfs-push.adoc): exact OID-only stdin upload.
- [Git LFS 3.8 configuration](https://raw.githubusercontent.com/git-lfs/git-lfs/v3.8.0/docs/man/git-lfs-config.adoc): source/.lfsconfig fallbacks, basic transport, storage, retries, deadlines, skip/incomplete settings and custom agents.
