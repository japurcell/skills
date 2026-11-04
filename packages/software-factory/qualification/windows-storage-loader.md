# Windows loader fixture source contract

This qualification-only route A prototype uses an independently trusted Python
3.13.14 controller before any candidate native code executes. It is excluded
from the ordinary registry and recursive native-test discovery. Source review
and portable tests establish no Windows ACL, sharing, loader, storage, installed
bootstrap, helper, descendant-closure or C1 acceptance. Original12 remains
unchanged and Windows RED. Providers remain blocked, reviews deferred and desktop
delivery last. Never run the held candidate/owned-image probe as this fixture.

The trusted controller, its interpreter/stdlib/_ctypes installation, cooperative
same-user actors, administrators, kernel/filesystem/filters, DOS namespace and
Windows system loader are prerequisites selected outside the candidate. The
canary cannot establish its own authority. The threat is an untrusted artifact,
selection substitution, unsafe ordinary-principal access, namespace drift,
unexpected dependency resolution, malformed protocol or incomplete teardown.
There is no universal hostile same-user race guarantee, historical privacy claim
or revocation of preexisting handles.

## Fixed invocation and external selection

The coordinator invokes its independently selected absolute Python executable:

```text
SELECTED_PYTHON -I -S qualification/windows-storage-loader-fixture.py --selection ROOT_OWNED_SELECTION --sha256 EXTERNALLY_FROZEN_SHA256 --case FIXED_CASE_ID
```

The selection and build receipt are authenticated outside the staged output.
They cannot be supplied by a product caller or derived from the candidate's
current hash. All executable, addon, script and receipt filenames are fixed by
the fixture. No runtime/path/helper/HANDLE/SID/API/flag/trust-boolean override is
exported. The script uses only isolated stdlib imports and fixed System32 WinDLL
exports with explicit signatures and pointer-sized handles. No pip, find_library,
Add-Type, SDK install, native download or runtime compiler is part of invocation.

The closed selection has exactly `schema` (integer1), `sourceCommit` (40 lowercase
hex), `sourceSha256` (all six exact package-relative paths to SHA256), `inputRoot`,
`stageParent`, `pythonSha256`, `buildReceiptSha256`, `artifactSha256`, and
`windowsBuild` (`10.0.BUILD`). Roots are distinct nonoverlapping absolute DOS
paths with unambiguous components. No UNC/device/ADS/reserved names, dot segments,
trailing spaces/dots, overlong path/component or additional fields are accepted.
The fixed `selection-only` case authenticates and parses this record, then
refuses with `native-required` before any WinDLL call on every platform. It is a
portable parser control and cannot yield a native receipt.

The externally prepared `inputRoot` has these fixed paths:

```text
control/build-receipt.json
runtime/node-v24.22.1-win-x64.zip
runtime/node.exe
build-input/node-v24.22.1-headers.tar.xz
build-input/win-x64/node.lib
output/windows-storage-loader-canary.node
output/windows-storage-loader-wrong-arch.node
output/windows-storage-loader-api-mismatch.node
```

The immutable selection must be outside `output` and the disposable stage parent.
The fixture derives its reviewed six-file source root from its own fixed script
location, never from candidate configuration. Source hashing corroborates an
independently trusted controller; it cannot establish trust in already executed
Python or JS. The selected interpreter and OS installation remain prerequisites.

The coordinator must freeze source commit and all six source digests, exact
Python image digest, trusted local NTFS stage parent, Windows build, selected
Node input, complete build receipt and artifact digests before native execution.
Missing or changed prerequisites hard-fail; they are never skips. A selected
Node input means the authenticated exact Windows archive, not a PATH lookup.

## Build recipe and provenance gate

Only the coordinator may authorize a later build with already installed trusted
x64 MSVC/Windows SDK tools. Exact absolute compiler/linker/dumpbin paths, bytes,
versions, complete include/library/SDK input digests, clean environment and fixed
commands must be recorded in an independently selected receipt before loading.
Discovering a tool with vswhere does not qualify it. Source contains one plain C
Node-API8 canary, no C++/V8/libuv/private Node/SQLite interface and no custom
DllMain or dynamic DLL load. A fixed negative API-version build is separate from
the positive canary. It must never replace the positive artifact.

Positive compilation policy is `/TC /W4 /WX /MT /LD /DNAPI_VERSION=8`, explicit
authenticated header/library directories, no `/GL`, CLR, delay-load flags or
private dependent DLL. `/MT` is a compiler selection, not dependency evidence.
The linker command must explicitly use `/MANIFEST:NO` so the no-manifest artifact
profile does not depend on compiler defaults; record the entire command.
The trusted builder must inspect actual `dumpbin /HEADERS /IMPORTS /EXPORTS`
output and the actual PE bytes: AMD64 DLL/PE32+, fixed registration/version
exports, complete ordinary import library/function list, zero delay imports and
no resource/manifest/redirection payload. Exact allowed import names remain
unknown until the coordinator freezes the actual receipt. Unexpected imports,
private CRT DLL, extra file, `.local` or manifest fail preflight. Review of the
fixed source plus actual PE inventory is necessary because PE imports do not
describe arbitrary runtime loading.

The complete build receipt has exactly `schema` (integer1), `sourceSha256` (the
reviewed canary source), `nodeArchiveSha256`, `headersArchiveSha256`,
`nodeImportLibrarySha256`, `toolchain`, and `artifacts`. Toolchain records are
mandatory external trusted-builder evidence, not claims that this loader has
qualified compiler/SDK installation ACLs or executed their programs.
`toolchain` has exactly `compiler`, `linker`, `inspector` (each absolute `path`,
`sha256`, bounded `version`), `sdkVersion`, nonempty `sdkInputs`, `headerInputs`,
`libraryInputs` (each entry exactly `path`, `sha256`, at most256 total tool/input
records), `environmentSha256`, complete `commands` (3-16, each4096 UTF-8 bytes),
and fixed positive compiler `flags` as written above. Root must assess the actual
commands, including negative x86/API999 builds and the explicit linker policy.

`artifacts` has exactly `positive`, `wrongArch`, `apiMismatch`. Each record has
exactly `file` (one fixed output basename above), `sha256`, `bytes` (1-4MiB),
`machine` (`amd64`, or `i386` for wrongArch), `pe` (`pe32+`, or `pe32`), `api` (8,
or999 for apiMismatch), sorted complete `imports` (exact `library`, sorted unique
`functions`), sorted exact `exports` (`napi_register_module_v1`,
`node_api_module_get_api_version_v1`), empty `delayImports`, and `resources:false`.
Node imports are exactly the four functions used by the C source. The fixture
parses each actual PE and compares machine/import/export facts with the external
receipt. Root must freeze and approve the specific system/API-set import list;
a receipt supplied by the output directory itself is never authority.

| Fixed input | SHA256 |
| --- | --- |
| Node v24.22.1 Windows x64 archive | d2046d28c2c3dcd211ac5145c0bf30e2047ef9dfb306693c8c6e2eccd8b95fa5 |
| node.exe | d702daa815eabbff763c7d3808e235cf031cf2ca70211b56847bc72f51e240e5 |
| v24.22.1 headers.tar.xz | 33bf331af1c9812d25f82efb53de793b36b54c23b8ad49652c4325bbe7f98216 |
| win-x64/node.lib | a0a84aa03917b578d286010b7521837e9ff1136ffb2e4a406c14316c33fd06f7 |

No build, download or native execution is established by this document.

## Native custody and lifetime invariants

Python obtains actual current TokenUser and rejects impersonation. It creates
each new fixture directory/file exclusively with explicit private security at
birth: current-user owner, protected non-NULL/nonempty DACL, exact one to three
trusted full-control entries, and directory inheritance. SYSTEM/Administrators
are optional trusted entries. Existing objects are inspected, never adopted or
silently repaired. Every path component rejects reparses; images must be disk,
regular, single-link and not delete-pending. Same-handle ACL, volume/FileId,
canonical GUID path and hash checks bind custody to objects, not strings.
Selected/staged/input code requires single-link identity and the stated principal
policy. Independently trusted OS dependencies are a separate prerequisite:
System32 module files may have one or more links, with actual opened identity,
canonical System32 parent and stable module observations required. They are not
represented as private candidate code or admitted by a mere path prefix.

Code roots/parents, node.exe, child JS, receipt and canary remain held with
FILE_GENERIC_READ and FILE_SHARE_READ only through actual loading and exact
Node closure. No write/delete share or temporarily released pin is permitted.
Bracketing fixed-name reopens compare actual identities before process creation,
at ready and after result. Parent sharing alone neither prohibits new children
nor locks WRITE_DAC/WRITE_OWNER; private ACL/inventory and trusted principals are
independent requirements. Actual Node loads the same fixed pinned pathname;
this is not a passed-HANDLE image-load claim.

CreateProcessW selects the exact full held node.exe, fixed quoted arguments,
empty held private CWD and clean environment. STARTUPINFOEX inherits exactly
three approved stdio handles; all other handles are noninheritable. A single
owner uses bounded PeekNamedPipe then reads only known available chunks, without
reader threads, global census, PSS, !htrace or Job Objects. The child reports
ready, receives load, calls the canary once, reports a closed result, receives
release and exits. K32 enumeration corroborates actual loaded module origins
using opened identities, never only path prefixes; HMODULEs are borrowed.

Each invocation has one 30-second eligibility budget including a five-second
cleanup reserve, 8192 captured/accepted bytes per output stream and 1024 bytes per
control/result record. Overflow irreversibly latches failure before any excess
is discarded. Root explicitly accepted this new prototype's separate cleanup
allowance: at most8192 further discard-only bytes per stream, using a1024-byte
scratch buffer inside the same deadline, never accumulated, parsed or exported.
Total observed reads are at most16384 bytes per stream; overflow can never become
success even if later EOF is established. Exhausted discard/time or an unknown
pipe observation enters inert refusal. Product and existing-test bounds remain
unchanged. Closed receipts expose only bounded numeric `capture` and `discard`
pairs so the qualifier can enforce both limits and failure retention.

Path caps are 64
components/4096 UTF-8 bytes; staged files 16, aggregate 256 MiB, node.exe128 MiB,
canary4 MiB, metadata1 MiB, descriptor256 KiB/ACL64 KiB/256 ACEs before the
tighter trustee profile. These caps do not promise cancellable OS-call latency.

On failure terminate only the exact owned process HANDLE, observe its actual
exit and both EOF within the remaining budget, then attempt every independently
owned release once. Preserve the first failure when cleanup also fails. An
unknown exit/EOF/identity/close fact retains the exclusively created stage and
prevents success. If exit or required EOF remains unknown at the eligibility
deadline, latch failure and keep the controller inert with its context and pins
owned. Do not return/unwind those pins or turn a late observation into success.
The fixed outer transport may eventually terminate that controller; OS teardown
then means UNKNOWN custody/closure, never proof. This is not a new successful
wait budget, and synchronous OS calls have no hard completion guarantee. Root
must confirm this concrete transport behavior before any native experiment.
Closing a HANDLE alone proves neither exit nor all-descendant
closure. Pins survive load failure because initialization may already have run.
Node owns module handles; never FreeLibrary, delete require cache, claim unload,
or reload in one process. Cleanup deletes only recorded still-identical owned
objects after exact-process closure. No raw exception/path/user/SID/env/PID/
HANDLE/Win32-error/module-list escapes the closed exported receipt.

Native receipts have exactly `scope`, `case`, `state`, `phase`, `reason`,
`selectionSha256`, `sourceCommit`, `nodeSha256`, `artifactSha256`,
`buildReceiptSha256`, `processStarted`, `processExit`, `stdoutEOF`, `stderrEOF`,
`ownedClose`, `capture`, `discard`, and `stage`. Digests identify independently
selected inputs, including the fixed negative variant for wrongArch/API999 cases.
An invocation that did not start Node reports false for process/EOF observations;
it cannot claim an exit merely from absence of a child. Successful fixtures need
actual started/exited/EOF/close facts, zero discarded bytes, no captured stderr,
and a removed owned stage. Every unknown stays failure with its stage retained.
`stage=retained` means removal was not established; cleanup failure can leave a
partially removed owned tree. It never authorizes deleting an unknown replacement.
The first fixed failure survives independent cleanup errors. A synthetic-close
case and synthetic-overflow-close combination are explicitly synthetic fault
controls; they never establish real CloseHandle failure behavior.

The portable receipt CLI is:

```text
SELECTED_NODE qualification/windows-storage-loader.qualification.mjs --validate-receipt EXTERNALLY_SELECTED_SELECTION_SHA256
```

It reads at most1025 stdin bytes to enforce the1024-byte record limit. Only the
canonical single closed record is accepted, with no duplicate/unknown fields,
extra records, unknown enums, forged closure or oversized counters. Its response
has explicit `windows-storage-loader-receipt-parser` scope. `state=validated`
means wire/schema/context validation only. Neither that output nor a caller-
authored successful record authenticates transport, custody, process exit or any
native artifact.

The later coordinator-only native entry is `SELECTED_NODE
qualification/windows-storage-loader.qualification.mjs --native`, with externally
selected `FACTORY_WINDOWS_LOADER_PYTHON`, `FACTORY_WINDOWS_LOADER_SELECTION`, and
`FACTORY_WINDOWS_LOADER_SELECTION_SHA256`. These belong to the independent trusted
disposable controller, not a product caller. Exact Windows/x64/Node/runtime/source/
receipt prerequisites hard-fail before the first child if absent. The39 fixed
cases run in source order with independent expected states/reasons and all six
groups required. Group2 sharing controls also run at both genuine positive
handshakes. No filtering, skips, retries or unselected runtime/helper are offered.

The proposed fixed outer transport has a35-second cutoff per Python invocation.
Thirty seconds remains the controller's complete eligibility budget. The outer
cutoff can terminate an inert controller, which is always an unexpected failure
with UNKNOWN custody after OS teardown, never a successful or expected closure.
Root must confirm this exact outer profile before a native release. Closed
failure output retains the fixed case/group and validated primary failure facts;
raw stderr, exceptions and payloads never escape. Final successful output is one
bounded matrix summary with case count, selected digests and transcript SHA256.
Selection, all six source files, selected runtime and independent build receipt
are checked before/after each invocation. No actual native result exists today.

## One future finite native experiment

The coordinator first freezes source, input/toolchain/PE receipt, actual module
origin policy, disposable host and complete ordered case list. The first missing
prerequisite or failed first positive stops the experiment. No retry or relaxed
runtime/share/search/bound/guard/count rule follows. Every group is required;
portable/synthetic controls never count as real native evidence.

1. Real user-only and optional SYSTEM/Administrators private-at-birth positive
   roots; actual API8 call under held custody, expected module identities,
   normal exactNode exit, both EOF, owned closes and same-object cleanup.
2. At ready and loaded handshakes, actual write-open, rename/delete and image/
   Node/parent replacement attempts must receive sharing refusal. Loading must
   still work. After closure/pin release, owned image rename/delete succeeds.
   A separate owned ACL-change control invalidates custody.
3. Before load: wrong digest/missing/replaced image or parent, final/intermediate
   reparse, hardlink, nonfile, broad child/private-looking parent, broad or
   unprotected root, denied metadata and sharing all refuse without load.
   Foreign owner remains an unmet separate storage control unless an already
   authorized genuinely foreign-owned disposable object exists.
4. Real wrong-architecture/unsupported metadata preflight refusal; fixed trusted
   API-version mismatch exercises real Node refusal. Fixture-owned extra DLL,
   conflicting import name, `.local` and manifest refuse before any execution.
   Actual successful dependency resolution remains required for the positive.
5. Real child success, throw before require, genuine require failure, throw after
   require, nonzero exit, stdout/stderr overflow, timeout and retained-owned-
   writer EOF negative. Require exact exit/both EOF where obtainable and every
   release attempt. Unknown closure preserves stage. Rare synthetic API/close
   faults are labelled synthetic and accompany real missing/access/share cases.
6. Selection/receipt extra, duplicate, wrong fields, candidate trust/path/hash,
   unknown reasons, forged success, path/file/output bounds, immutable-selection
   drift and foreign replacement prevent success. Cleanup preserves replacements;
   frozen source/runtime/receipt postflight and leak-free closed output required.

Native controls create and mutate only their exclusively created stage. Changed
image/parent and final/intermediate reparse controls happen before code pins are
acquired; no pin is temporarily released to manufacture a positive. The parent
replacement actor must first obtain a rename/delete right, which real retained
sharing must deny. Additional replacement-image fixtures live outside every
Node DLL search location. API999/wrongArch artifacts require separately frozen
trusted build provenance before even the first positive runs. Symbolic-link
creation must be available under the already accepted host profile; unavailable
reparse/control authority hard-fails, with no privilege change or synthetic pass.
Schema/path bytecaps remain public parser controls and do not pretend to be
native ACL/identity evidence. Real oversized files, real cap overflow and actual
closure observations remain separate native controls.
The `changed-selection` native case replaces the exclusively created staged
selection mirror before pinning, and must refuse its changed identity. The
independent external original stays read-only; genuine old-digest/new-byte refusal
is exercised through the public parser CLI, with the external file rehashed by
both controller and outer postflight. No external input is mutated by a fixture.

Full C1 storage acceptance still separately requires the public private
initializer, retained storage lease/read/close, unchanged original12 and every
storage proof group. Installed route B needs a qualified independent first-load
producer. ReFS, network filesystems, another architecture and product helper
support remain unqualified.

## Primary references

- [Python 3.13 ctypes](https://docs.python.org/3.13/library/ctypes.html)
- [CreateFile sharing](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew)
- [GetSecurityInfo ownership and races](https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-getsecurityinfo)
- [Explicit inherited handle list](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)
- [PeekNamedPipe caveat](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-peeknamedpipe)
- [Module snapshot limitations](https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-enumprocessmodulesex)
- [Pinned Node-API](https://nodejs.org/download/release/v24.22.1/docs/api/n-api.html)
- [Explicit no-manifest linker policy](https://learn.microsoft.com/en-us/cpp/build/reference/manifest-create-side-by-side-assembly-manifest?view=msvc-170)
- [Returned self-relative descriptors](https://learn.microsoft.com/en-us/windows/win32/secauthz/absolute-and-self-relative-security-descriptors)

## Source handback and portable proof

Only the six proposed qualification/test files belong to this source slice.
Canonical plans/notes/index, registry/workflow, build integration, inventories,
product source and shipped assets stay coordinator-owned. Portable command:

```text
FACTORY_WINDOWS_LOADER_TEST_PYTHON=SELECTED_PYTHON_3_13_14 SELECTED_NODE --test packages/software-factory/test/windows-storage-loader-contract.test.mjs
```

The actual CLI parser, real fixed child ready/load/missing-canary/result/release,
closed output/counter/closure controls, and real default discovery are exercised.
These tests use no private Win32-wrapper mocks and no JS Windows lifecycle model.
No native C compilation, header/SDK download, DLL load, Windows ACL/sharing or
storage proof occurred in the author session. Retained initial RED/GREEN logs:
`/tmp/factory-windows-loader-selection-child-{red,green}.log`,
`/tmp/factory-windows-loader-handshake-{red,green}.log`,
`/tmp/factory-windows-loader-receipt-context-{red,green}.log`.
Final scoped proof and preservation records are supplied in the source handback;
formal/independent review remains deferred by the user. Root owns next source
assessment and every host/toolchain/import/origin/share/closure prerequisite
before considering one genuine Windows experiment. Installed route B, actual
private storage, C1 acceptance and helper/descendant closure remain open.
