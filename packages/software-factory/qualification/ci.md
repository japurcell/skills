# Foundation qualification evidence

## Definition and trust boundary

`.github/workflows/software-factory-qualification.yml` runs on relevant package/workflow/test-runner changes for `push` and `pull_request`, plus manual `workflow_dispatch`. A single `native-foundation` matrix job uses Ubuntu 24.04 x64, Windows 2025 x64 and macOS 15 arm64, `fail-fast: false`, and a 20-minute job limit. Each run retains uniquely named native artifacts for 14 days, including failure JSON/logs. Missing evidence is an upload error.

Permissions are only `contents: read`; checkout credentials are not persisted. There is no privileged pull-request trigger, reusable cache, provider authentication, account installer or desktop notification call. PR code is untrusted and executes on disposable hosted VMs without repository secrets. Node downloads happen only in the explicitly opted-in Actions bootstrap, never product startup. The manifest pins downloaded bytes; npm installs the committed lock with scripts disabled. Both Actions are immutable official release SHAs, verified 2026-10-21:

- [checkout v7.0.0](https://github.com/actions/checkout/releases/tag/v7.0.0): `9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0`.
- [upload-artifact v7.0.0](https://github.com/actions/upload-artifact/releases/tag/v7.0.0): `bbbca2ddaa5d8feaa63e36b76fdaad77386f024f`.

Prerequisites include runner-provided bootstrap Node with fetch support, HTTPS access to official Node/npm distribution, native tar extraction, Git, supported local persistent placement, Windows PowerShell/native volume APIs, and the existing POSIX Python resource fixture. Missing prerequisites produce a failed step. Exact downloaded Node 24.22.1, SQLite 3.53.4 and lockfile dependencies are checked before foundation tests. GitHub runner image metadata and actual bundled npm version are saved.

`bootstrap.json` records archive hash/native versions or the blocking error. `foundation.json` records every selected command/status/duration, image metadata and explicit foundation scope. Individual logs retain failures; `runtime.json` holds direct SQLite proof when that probe succeeds. The runner continues independent foundation checks after a test/build failure so other evidence survives, but any failed command makes the job fail. Dependency-install failure stops dependent checks.

## Observed local development evidence

On 2026-10-21, darwin-arm64 Darwin 25.6.0 APFS using Node v24.22.1 and SQLite 3.53.4: offline locked install, both strict typechecks, build, fixtures 6/6, store/capture/integration 27/27, placement 2/2, runtime 2/2, and direct native SQLite JSON passed. Two additional CI CLI contract tests pass and verify missing prerequisites retain structured failure evidence. Local job artifacts were written to `/tmp/factory-ci-local-evidence`; these are development evidence, not a hosted run.

Workflow YAML was parsed and its matrix, permissions, SHA pins, credential persistence and failure-upload contract checked. Official actionlint 1.7.12 was downloaded into `/tmp` and checked against its release checksum before workflow linting. No source-tree dependencies or global tools were installed.

## Open acceptance gates

There are no hosted run URLs yet. No push or provider call was performed. Linux and Windows runtime-manifest qualification remains `pending`; the PowerShell/native volume mechanism remains unverified until Windows execution. A workflow definition or local macOS pass must not promote those targets.

Parent integration must wire `assertLocalPlacement` into the store, register placement/CI contract tests in the maintained registry and merge the exact foundation commit. The original POSIX RLIMIT_FSIZE fixture is retained. Windows now selects a native shared WAL byte-range write lock after the committed-prefix barrier, using a separate owned PowerShell/C# process. The same assertions require actual recorder failure, blocked admission, one shutdown request, one fallback notice, the saved prefix and readable prior events. Native helper setup/cleanup errors fail the test; no platform is skipped. The helper has a ready handshake, bounded range/wait and explicit release before store close. Its PowerShell syntax and embedded C# compilation passed on macOS PowerShell; all 15 capture tests, including POSIX RLIMIT_FSIZE, passed locally after the change. Actual Windows lock/SQLite behavior remains pending the hosted job. This provides a candidate native I/O-failure case, not disk-full parity. [Windows byte-range locks](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-lockfileex) allow reads but deny writes for a shared range, including beyond EOF. [SQLite WAL](https://sqlite.org/wal.html) appends transaction records, but memory-mapped writes bypass byte locks, so documentation and syntax checks cannot establish native acceptance.

Once publishing the branch is authorized, push and collect each hosted matrix result, artifact hash/JSON and run URL against the exact commit. Fix every native failure and retain previous failure evidence. No authenticated-provider workflow is created without configured credentials and a useful harmless bounded contract. Extend this foundation workflow to later supported suites as they land; T17 requires complete supported acceptance. Live desktop visible-delivery notification checks run last in T17, outside this workflow.
