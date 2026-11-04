# Darwin next observation contract

Historical design provenance: read-only design complete at the recorded source snapshots. Root subsequently selected implementation be2705fa and one changed native observation. Current evidence and release state are maintained in [ExecPlan](../ExecPlan.md) and [handoff](../handoff.md); proposed checks below are not historical run results. No repository file, build, test, process probe, native experiment, provider, auth, review, or desktop operation was performed for this packet. Only this `/tmp` packet was written. Initial main HEAD: `92c96edf46c1034baeca2a8abf9d9fc465c7c28b`. Final inspected-source recheck is recorded at the end.

## Decision

Observe the learning fixture's own lifecycle-host process first. Add a fixed, default-off test-host preload that uses the existing collector's process-own `worker-open`/`worker-close` accounting. Correlate it to the existing registered file/case and fresh opaque child binding. For the 35 synchronous hosts, add a **distinct synchronous-return closure receipt**, backed by the documented `spawnSync` return contract and a fresh private host PID receipt. Keep the existing asynchronous `spawn`/`exit`/`close` receipt semantics unchanged. The single asynchronous interrupt host uses that existing event contract.

This supplies the missing host-process CPU and post-preload wall interval alongside the existing test-worker source/learn span and persisted startup/build attempt interval. It does not measure compiler CPU, compiler subphases, process-birth time, or build-only host CPU. A killed host without a genuine self-close has unknown CPU even when a parent establishes its closure. A genuine self-close on graceful exit 143 may report only its measured emitter interval, labeled interrupted, without implying whole-process or invocation completion. No optimization follows from this design or from the retained A/B/C variation.

Do not add production instrumentation to `src/build.ts`, `src/workflow.ts`, `src/lifecycle.ts`, or `src/native/process.ts`. Do not add compiler arguments, a compiler preload, `NODE_OPTIONS`, a new public option, diagnostic output capture, guard caching, shared mutable toolchains, scheduling changes, or signal handlers.

## Why this is the minimum useful observation

The retained complete A/B/C exports use the same pinned Node v24.22.1 Darwin runtime but different source SHAs. Learning selector wall is 29.508/16.330/27.709 seconds. The startup/build attempt sums are 25.885/15.325/24.576 worker-seconds; copy sums are 4.518/2.275/3.024, and fake-agent sums are .829/.591/.864. These nested or concurrent sums cannot be added to explain selector wall. The original red `8f59d77b` has no complete old timing export.

The local copy-helper paired measurement (94.632 to 70.969 ms median) proves only that local copying operation. It does not isolate the observed native variation or establish a repair for the historical deadlines. The new observation must remain inside the original full 31-fixture context and retain all original 36 notification and 13 learning cases.

| Candidate observation | What it can establish | Decision |
| --- | --- | --- |
| Fixture-host own CPU and wall from collector initialization to its normal exit | Previously absent host-process work during module loading, lifecycle setup, managed-child waits, workflow execution and settlement; CPU remains current-process-only | Choose. Entirely test/qualification owned and no production build behavior changes |
| New compiler-command monotonic spawn/exit/close marks | A narrower command-process lifetime than persisted attempt timestamps; still no compiler CPU | Defer. Existing attempt wall already identifies a build-related interval. A new channel observer also needs a proven exact compiler classifier and private attempt correlation |
| Build setup/compiler/capture/load subphase spans | Separates the `buildWorkflow` and `CommandRunner` implementation phases | Defer. No existing public observation interface exposes these subphases without production edits, interposition, or new test-only instrumentation hooks |
| Parent `process.cpuUsage()` or `process.resourceUsage()` as compiler CPU | Neither inspected API attributes CPU to a child PID | Reject that interpretation. Compiler CPU remains unknown |

Pinned Node documents the experimental `child_process` diagnostics channel and spawn tracing channels, but their existence is not a compiler classifier, compiler CPU interface, or an attempt correlation contract. This proposal subscribes to none of them. It needs no undocumented/private Node interface.

## Actual source map and conventions

All paths below are relative to `packages/software-factory/` unless prefixed otherwise.

- `src/build.ts:7` validates the authoring/toolchain/configuration and builds once. Line 47 calls `runner.execute(startup/build/<invocation>, { argv: [process.execPath, compiler, '-p', config], env: {} }, true)`. The later module import is line 51. The build is not a set of existing public subphase events.
- `src/workflow.ts:109` funnels `execute` into tracked `perform` at line 131. Admission is line 148; context/output capture creation is lines 155-159; actual spawn is line 166; persisted started marking is line 178; scope result, output drain and recorder barrier are line 179; settlement is line 183. A persisted started-to-settled interval includes observation and settlement work around the child, not only compiler execution.
- `src/native/process.ts:46` owns managed child state. Separate exit/error and stdio-close observations are lines 61-64. `result` at line 90 also retains the existing process-group/cleanup uncertainty rules. None of this is a compiler CPU interface.
- `src/lifecycle.ts:40` exposes `invoke`; its existing production SIGINT/SIGTERM handling is lines 46-49. The build call is line 118. The new observer must add no signal handlers and must leave that behavior intact.
- `test/fixtures/learning-extraction-fixture.mjs:45` creates a fixed generated lifecycle host. Ordinary source/learn invocations use `spawnSync` at line 60, while `interruptSource` uses `spawn` at line 75 and awaits real close at line 95. The current host imports production modules, invokes the lifecycle, prints the original result, and explicitly exits with its original exit code. There are 35 synchronous launches and one asynchronous interrupt launch across the current original 13 cases, matching 36 retained startup/build attempts.
- `qualification/selector-timing.mjs:9` fixes 4096 records, 2 MiB per process, 128 collector files, 16 MiB aggregate and 4096 attempt rows. Its exact JSONL keys are line 15; validation is line 26. Collector open/close CPU accounting is lines 60-97. `ownedWorkerTiming` at line 142 requires successful actual spawn, matching exit and later stdio close. `validateWorkerClosure` at line 165 is shared with artifact staging. `telemetry` at line 209 installs only a synchronous exit callback, and `timingNodeArgs` at line 228 is default off.
- `qualification/selector-timing-attempts.mjs` reads only allowlisted persisted event metadata from a helper-owned disposable repository, remapping raw IDs to opaque UUIDs. Keep it unchanged.
- `qualification/selector-timing-driver.mjs:32` preserves the fixture exit, line 37 checks selected coverage, and lines 39-45 export exactly two files with source/runtime identity and the fixed `emitting-process-only` CPU label.
- `qualification/selector-timing-artifacts.mjs:10` implements bounded no-follow file reads, line 20 closed metadata validation, line 28 timeline/closure validation and line 42 exact two-file staging. Preserve those checks and use the same new closure validator in collection and staging.
- `scripts/ordered-tests.mjs` and `scripts/ordered-test-worker.mjs` already provide fresh opaque binding to a real asynchronous owned child. Their 1000 ms cancellation grace and event-based closure semantics remain unchanged.
- `src/release.ts:167` selects explicit runtime/web/template/toolchain/native inventories. Qualification and fixture files are not added to those inventories. No release inventory change is proposed.

The active T17 contract at `brain/plans/software-factory/ExecPlan.md:575` requires the original dispatcher/full-context route, unchanged bounds and all original assertions. This packet does not edit that plan or any private IR1 source.

## Exact future implementation map

1. **Modify `qualification/selector-timing.mjs`.** Advance the emitted timing schema and metadata agreement to schema 3 because synchronous-return closure has a different meaning. Retain the exact existing record keys. Add only these stage literals: `worker-bind-sync`, `worker-close-returned`, `fixture-host`. Keep existing async `worker-bind`/`worker-close-observed` semantics unchanged. Update the shared record/relationship validators and add the host coverage function described below. Do not change ordinary collector CPU accounting, bounds, async observations, or signal handling.
2. **Create `qualification/selector-timing-host.mjs`.** Own the narrowly scoped parent launch descriptor, fixture ownership revalidation, fresh opaque sync binding, private receipt verification and non-throwing incomplete marking. Reuse `telemetry`, `labels`, `fixtureIdentity`, and existing `ownedWorkerTiming` for async mode. This module is for the fixed learning fixture only; it is not a generic command observer.
3. **Create `qualification/selector-timing-host-preload.mjs`.** Fixed startup module, enabled only when the existing timing root is present and an exact descriptor is supplied by this fixture. Initialize the collector with the reserved worker ID; emit one fixed `fixture-host` mark carrying registered file/case labels; write the private receipt from its own `process.pid`. Let the existing synchronous exit callback write `worker-close` on normal/explicit exit. Add no begin span whose missing end would be synthesized on a signal, and add no signal handler.
4. **Modify `test/fixtures/learning-extraction-fixture.mjs`.** At each existing launch, obtain a descriptor only when timing is already enabled. Prefix the host argv with the exact fixed preload pair only in that mode. Put the exact descriptor under a reserved fixture-only `qualificationTiming` property in the already-existing JSON host argument, appended after `extra` so arbitrary fixture extras cannot replace it. In generated host source, destructure that property alongside `scenario` so it never reaches production `invoke`. Immediately after each synchronous return, verify and record its distinct returned-close receipt before existing result/error assertions. For the async interrupt path, attach the existing event observer immediately after `spawn`. Keep original spawn kind, stdio, encoding, timeout, shutdown grace, inputs, scenario, diagnostics, result bytes, exit code, original assertions and fixture disposal behavior unchanged. Default-off argv and environment must remain byte-for-byte equivalent to the current launch.
5. **Modify `qualification/selector-timing-driver.mjs` and `qualification/selector-timing-artifacts.mjs`.** Agree on schema 3, retain the exact metadata keys and `cpu=emitting-process-only`, and require the additional host coverage only when claiming a complete new full-context export. Incomplete valid exports remain exportable as incomplete. Historical schema-2 artifacts remain immutable and assessed by their historical schema-2 code; do not reinterpret them as schema 3.
6. **Create `qualification/selector-timing-host-checks.qualification.mjs`; extend `qualification/selector-timing-artifacts.test.mjs` and, only as needed for new schema literals, existing telemetry qualification checks.** Use the subprocess/staging interfaces below, without importing private production functions. Keep these extra tests outside the original 31-fixture registration. The existing CI timing push patterns already match the two new `selector-timing*.mjs` files. No dispatcher/selector/workflow/release inventory change is needed for the observation itself.

### Proposed qualification interfaces

In `qualification/selector-timing-host.mjs`:

    fixtureHostTiming(repository: string, kind: 'sync' | 'async')
      -> undefined | {
           kind: 'sync', nodeArgs: readonly string[], context: HostContext,
           returned(outcome: { pid: number | undefined,
                               status: number | null,
                               signal: string | null,
                               apiError: boolean }): void
         }
       | {
           kind: 'async', nodeArgs: readonly string[], context: HostContext,
           observe(child: ChildProcess): void
         }

`undefined` is the timing-off result and must do no fixture filesystem work. Both returned methods are one-shot and non-throwing: diagnostic failure marks evidence incomplete, without substituting the product/fixture result. At the existing `spawnSync` call site, project only its actual `pid`, `status`, `signal` and the sanitized boolean `apiError: result.error !== undefined` into `returned`; do not pass stdout, stderr, argv, environment or an Error object into this observer. Certification requires `apiError === false`, meaning the caller has established `result.error === undefined`. Any API error, including ENOBUFS, ETIMEDOUT or spawn failure, takes the conservative incomplete branch even if PID/status/signal appear plausible. Wrong mode, second use, malformed descriptor, unavailable identity or malformed receipt cannot create closure. The async method delegates real event receipt production to existing `ownedWorkerTiming().observe(child)`; it never invokes the synchronous-return recorder and must not read/copy child output.

`HostContext` has exactly `{ schema: 1, workerId: UUID, fileId: registered learning basename, caseId: registered one-based index }`. Do not include paths, PIDs, environment, raw invocation IDs, commands, inputs, error text, or captures. It travels only in the private fixture host JSON argument. The fixed preload locates this one reserved property; it must not inspect or export arbitrary argv fields. No new environment variable is needed.

`nodeArgs` is exactly `['--import', new URL('./selector-timing-host-preload.mjs', import.meta.url).href]`, with no configurable module, arbitrary extra argv, or propagated `process.execArgv`. The fixed host argv position and the already-owned canonical fixture repository determine the private receipt location. An invalid setup disables this observation for that launch and marks the parent's evidence incomplete while the original launch still proceeds.

In `qualification/selector-timing.mjs`:

    hasFixtureHostCoverage(records: readonly TimingRecord[]) -> boolean

This complements, and never replaces, existing 49-case/attempt-class coverage. Current expected host counts by registered file/case are: `learning.test.mjs` 2/4; `learning-extraction-sources.test.mjs` 2/9/3; `learning-extraction-paths.test.mjs` 5/2; `learning-extraction-evidence.test.mjs` 3/1/1/2/1/1. Total 36. There must be 35 distinct sync bindings and one async interrupt-host binding, each linked to exactly one `fixture-host` marker with the same file/case. Do not use generic case-count coverage to infer a host launch or closure. This count map is an observation-completeness assertion, not a change to original case registration, test names or assertions.

### Private synchronous identity receipt

The new producer is exactly the fixed preload running in the just-launched fixture host. It writes a fresh one-use file beneath that helper-owned disposable repository's `.git` directory, using a name derived solely from its reserved UUID (for example `selector-host-<workerId>.identity.json`). The parent computes the same name; no arbitrary path is accepted from payload data. One receipt per launched host, at most 36 creations across the original selected cases and at most 9 in any current fixture repository. Existing repository disposal owns removal. This is a separately accounted small private fixture artifact, not an exported collector file, extra helper process, new upload, or extra stdout/stderr capture. It never enters the timing root or either export. The existing 128 collector-file cap remains unchanged.

Receipt bytes are canonical UTF-8 `JSON.stringify({ schema: 1, workerId, pid: process.pid }) + '\n'`, at most 256 bytes, exclusive `wx` creation, mode 0600. The parent validates the already-owned canonical fixture identity before launch and again after return, the canonical non-symlink `.git` directory, the exact generated receipt basename, regular no-follow file type, nlink 1, private mode, size, exact keys/schema/UUID and positive safe-integer PID. Read from one held descriptor, check metadata before/after, reject noncanonical/duplicate-key/invalid UTF-8 bytes through exact byte round-trip, and verify the path still names the held identity. Do not log receipt contents or private paths.

A synchronous closure is admissible only after the actual `spawnSync` call has returned without any API error (`result.error === undefined`, sanitized `apiError === false`), its positive safe-integer `result.pid` equals the receipt's host-written PID, the fresh UUID equals the reserved subject identity, and returned status/signal form one legal outcome. ENOBUFS, ETIMEDOUT, spawn errors and any other API error cannot become closure proof from PID/status/signal alone; mark incomplete even where Node's full-close contract might support a less conservative interpretation. A returned status alone, a requested signal, timeout intent, self-close, stale receipt, PID mismatch, partial receipt, missing receipt, or synthesized event sequence is insufficient. Unknown becomes incomplete. The synchronous Node contract establishes process/stdio closure, not descendant-tree closure, product cleanup success, or CPU availability. Existing lifecycle cleanup guards continue to decide product cleanup.

The receipt binds only the fixed frozen test host under the existing owned-fixture trust model. It is not an authentication scheme for arbitrary hostile executable code or a general cross-process attestation facility.

### Exported record and closure rules

Keep exactly these keys: `schema, workerId, subjectWorkerId, sequence, monoMs, epochMs, stage, phase, fileId, caseId, spanId, invocationId, attemptId, operationClass, at, wallMs, cpuUserUs, cpuSystemUs, disposition, exitCode`.

- `worker-bind-sync`: parent emitter, mark phase, fresh distinct `subjectWorkerId`, current registered file/case, none disposition, null exit, no invented CPU/wall/span/attempt data. It reserves one actual future sync launch and does not prove birth or closure.
- `worker-close-returned`: the same parent, later mark phase, same subject, actual sync return outcome. Null exit requires one of the existing signal dispositions; normal integer exit 0..255 requires ok/failed as today. No host CPU is inserted into this parent record. Its measurement fields stay zero/default, meaning unavailable here.
- Existing `worker-bind` pairs only with existing `worker-close-observed`, after actual successful spawn, matching exit and later close. Never accept a returned-close record for an async binding or an observed-close record for a sync binding.
- The shared validator retains fresh unique subjects, one matching parent, no cycles/duplicate bindings/duplicate closure, sequence/monotonic ordering, worker-open after binding, closure after the subject's last record, and all existing span rules. The subject must actually have written worker-open. Unknown/forged/inconsistent relationships refuse even partial staging; missing closure stays incomplete.
- `fixture-host`: subject emitter's single mark, exact registered learning file/case, no private payload. Its parent binding carries the same registered labels. A genuine `worker-close` supplies only that emitter's measured post-collector CPU/wall interval. When the known graceful interrupt host exits 143, label that measured interval interrupted; it never certifies a complete invocation or whole-process interval. A signal-return or async closure without self-close proves only closure and supplies **unknown host CPU**, not zero CPU and not an inferred end.

Here `interrupted` is a reporting label derived from the existing known interrupt fixture/outcome, not a new JSON disposition literal or an invented OS signal. A normal returned code 143 with signal null retains the existing generic failed-exit encoding. Preserve that distinction from actual SIGTERM/SIGKILL termination.

Every record remains within the current 4096 records / 2 MiB per process, 128 collector files / 16 MiB total limits; persisted attempt paging remains 4096 rows and 128-row pages. No bound is increased. The prior full context has 51 collector writers; this design adds 36 host writers, for an expected 87, leaving the cap intact. A normally passing comparable context would be expected to have 84 self-closes, 11 async observed closures and 35 sync returned closures, with overlap between receipt classes. These are expected design-accounting numbers, not observed proof or universal counts for every future source revision.

All observer setup/receipt/I/O/limit failures must become fixed incomplete evidence without raw error text and without changing the original host launch, stdout/stderr, assertions, status or signal. Never close a host collector from a parent. No added SIGINT/SIGTERM/SIGKILL listeners, delay, polling, retry or timeout is permitted. Incomplete exports still preserve the original fixture exit, and a passing fixture with incomplete telemetry still fails the diagnostic guard.

## Data flow and interpretation

The existing selected case calls the same fixture helper. Timing-off returns no descriptor and launches exactly today's host. Timing-on creates the fresh opaque binding and fixed descriptor, then launches the same executable and host with the one fixed preload. The preload initializes its own bounded collector, emits its fixed role/case marker and private PID receipt, then the original host imports lifecycle modules and invokes unchanged production code. Production build still runs its exact current `[node, tsc, '-p', config]` argv with `{}` environment. Existing persisted attempt export remains the only build-attempt observation.

Normal host exit synchronously writes its own CPU/wall self receipt. The blocked parent resumes after actual sync return, verifies PID-to-writer identity and emits the distinct sync-returned closure; the async interrupt parent uses real child events. The driver collects both kinds through the shared strict validator and preserves its fixture exit. The staging guard publishes only validated `selector-timing.json` and `selector-timing.jsonl`.

Use the registered case labels, binding subject ID and within-run monotonic containment to relate a host to the existing source/learn/interrupt span. Multiple same-case synchronous invocations remain ordered and non-overlapping in that worker; never pair across runs or by subtracting unrelated monotonic origins. Existing persisted attempt `at` is UTC wall time and must remain labeled separately; relating it to host epochs does not turn it into monotonic compiler time. If the relation is ambiguous or a wall clock adjustment is suspected, report the interval unassigned rather than force an exact decomposition.

Report host CPU and host post-preload wall separately from test-worker CPU, compiler-attempt wall and copy wall. Host CPU excludes the compiler and other children and excludes Node/bootstrap/preload work before collector initialization. It includes observer receipt/mark work after initialization; do not subtract guessed observer cost or call the value pure production CPU. Compiler CPU, setup/compiler/capture/load subphases, scheduler waiting, filesystem/cache causes and historical cause remain unknown. Low host CPU with long wall only identifies time not consumed as CPU by this emitter; it does not identify which child, wait, native helper, contention or cache state caused it. CPU may exceed wall for multithreaded process work; do not enforce CPU <= wall.

## Proposed TDD sequence and proofs

The agreed seams for this proposed work are the existing Node subprocess launch/returned result, the fixed test-host preload, the collector export, and `stageSelectorTimingExports`. Root must approve implementation scope before a worker writes tests or code. This packet does not ask to run or approve a new experiment now.

1. Start with a tiny generated registered test/host at those seams, timing off/on, where the host explicitly exits 7 and writes a fixed original stdout/stderr payload. The new expected host writer/binding/returned-close evidence must be RED against current source while outcome and payload stay identical. Implement only that vertical slice and retain red/green evidence.
2. Prove a real synchronous host killed by SIGKILL after the fixed receipt is written has a validated `worker-close-returned` with signal SIGKILL, no self-close, and unknown CPU. No async receipt may appear. Also verify normal exit 0/7, explicit process.exit(23), default SIGTERM/SIGINT in tiny non-product hosts and original output/status/signal off/on parity. No new signal listeners are allowed in the observer.
3. Real/synthetic negative controls at the collector/staging seams: actual spawn API failure, controlled ETIMEDOUT and controlled ENOBUFS with a plausible PID/status/signal; absent/partial/stale receipt; UUID/PID mismatch; linked/nonprivate/oversized/noncanonical/duplicate-key/invalid-UTF-8 receipt; failure before preload; wrong observer mode; duplicate observer use; spoofed/unknown subject or parent; swapped async/sync receipt types; early closure; duplicate binding/closure; cycle; impossible exit/signal. Every API-error case must set the sanitized flag and remain incomplete, never emit returned closure. No invalid input may produce a returned closure or complete export. Keep raw Error objects, canary strings, PIDs and paths out of both exports and diagnostics.
4. Retain existing async resistant-cancellation, default-signal, no-early-receipt and exit-before-stdio-EOF controls unchanged. Add one fixed async host descriptor case using existing `observe(child)` to prove its actual event contract is still distinct. A synchronous signal intent while no return has occurred cannot count as closure; a controlled parent can inspect evidence only from a separate tiny controller, without altering the product fixture's launch style.
5. Verify complete schema-3 host coverage (the 36 count map), missing host writer/marker/closure, and unchanged original 49-case coverage. A self-closed host with no required returned or observed receipt does not substitute for its binding's closure. A valid SIGKILL closure never fabricates a CPU self receipt. A genuine graceful-143 self receipt remains labeled only as measured interrupted emitter interval, excluding pre-collector bootstrap and any invocation-completion claim. Test record/file/byte/row caps and invalid incomplete evidence using existing public collector/staging calls; do not add private production exports.
6. Extend exact-two-file staging tests for schema 3 while retaining all private-field, duplicate JSON, no-follow, source/runtime, red exit, oversized export and incomplete-status controls. Preserve old schema-2 artifacts byte-for-byte. Check default-off host argv/environment and production build argv plus release inventories through the existing fixture/packaging seams. Do not add original selector test cases merely to test this observer.

After each red/green slice, root may authorize the focused pinned-runtime command from `packages/software-factory/`:

    rtk proxy /private/tmp/factory-qualified-node-342t16a/node-v24.22.1-darwin-arm64/bin/node --test qualification/selector-timing-checks.qualification.mjs qualification/selector-timing-closure-checks.qualification.mjs qualification/selector-timing-host-checks.qualification.mjs qualification/selector-timing-artifacts.test.mjs

Then run the existing default-off ordered-runner checks and relevant CI/packaging guard selections with the same pinned environment under root coordination. Run syntax/whitespace checks for changed files. All counts, outcomes and commands here are proposed; none ran in this task. No independent review, local full-context proof or build is part of this packet.

## One future native experiment, after implementation is separately selected

Root owns source integration, proof/load pause, frozen build/receipt verification, push and the single changed native experiment. Use the existing dedicated Darwin timing workflow and its original serial foundation phase context. Pin Node v24.22.1/executable SHA, PATH, Python 3.13.14, exact copied offline dependency cache and current receipt preflight as already required. Record exact source SHA, runtime hash, OS/build/image and available parallelism; keep source immutable from the pinned build through final fixture exit and staging. Do not run while IR1 or other heavy writers/proofs are active.

Invoke the original full `scripts/test.mjs fixtures` route exactly once at the existing fixtures position through the timing driver. Preserve original FULL 31 fixtures, notifications 10 files/36 cases/concurrency 4/15 seconds, learning 4 files/13 cases/concurrency 2/30 seconds, 1000 ms cancellation grace, every original name/assertion, and required five-second uncertainty behavior. Do not replace this with a named learning case, copy-only benchmark, isolated selector pass, reordered phase, or unchanged rerun seeking green.

Acceptance for the **observation only**: preflight and exact-two-file staging pass; original exit and all original cases remain visible without skips; schema-3 source/runtime/context checks pass; complete evidence has all original 49 selected endings/attempt classes and all 36 correctly correlated hosts with their required true closure receipts; host CPU is attributed only to host self-close and stays unknown otherwise; all current caps/privacy checks remain enforced. Retain red/incomplete outcomes as such rather than retrying. If timeout/kill prevents required endings, the diagnostic can truthfully remain incomplete and still provide useful bounded records; it must not claim complete acceptance.

The one observation can guide the next seam selection. It cannot establish an old `8f59d77b` cause, a causal A/B speed comparison against different source revisions, a production bottleneck, compiler CPU, native deadline repair or platform acceptance. Any later optimization or deeper compiler observation requires a separate evidence-backed task.

## Primary Node v24.22.1 contracts consulted

- [process.cpuUsage](https://nodejs.org/download/release/v24.22.1/docs/api/process.html#processcpuusagepreviousvalue) and [process.resourceUsage](https://nodejs.org/download/release/v24.22.1/docs/api/process.html#processresourceusage): both refer to the current process; CPU values are microseconds. The CPU delta may exceed elapsed wall time when multiple cores work for that process.
- [spawnSync](https://nodejs.org/download/release/v24.22.1/docs/api/child_process.html#child_processspawnsynccommand-args-options): its documented return includes PID/status/signal, and it returns only after the child has fully closed, including after a timeout's kill signal. This supports a distinct returned-close receipt, not invented async events or descendant closure.
- [child close](https://nodejs.org/download/release/v24.22.1/docs/api/child_process.html#event-close): close follows process end and stdio closure; it is distinct from exit. Existing async observers must continue to require successful spawn and matching exit separately.
- [--import](https://nodejs.org/download/release/v24.22.1/docs/api/cli.html#--importmodule): preloads a module at startup and is experimental in this pinned release. This design adds it only to the fixed test host when qualification timing is enabled. It does not use `fork`, propagate execArgv or inject NODE_OPTIONS.
- [built-in process diagnostics channels](https://nodejs.org/download/release/v24.22.1/docs/api/diagnostics_channel.html#process): documented experimental process channels exist; none supplies compiler CPU or the application's persisted attempt identity. They are not used by this minimum proposal.

No claim here depends on a guessed diagnostics channel or a child-CPU interpretation of current-process APIs. Runtime proofs for the proposed new host/return mapping remain unperformed.

## Source snapshot and end check

Initial source blobs, in file order below, were read and recorded without modifying them. Before handback recheck the same blobs and HEAD; if any differ, report drift instead of silently treating this contract as validated against the new source.

| Inspected source | Git blob |
| --- | --- |
| `src/build.ts` | `ca9db6a6a89fb733bba740ee59efaf9bd8827179` |
| `src/workflow.ts` | `0b0ff644ed03d7097041fbe155b7f3323fb3801f` |
| `src/lifecycle.ts` | `bcf958cc7f8ae32d69048e2a2398639a0d06e8e0` |
| `src/native/process.ts` | `a38ce2876befdf88af644f2a9539c3c1fab4e202` |
| `test/fixtures/learning-extraction-fixture.mjs` | `a65524ece439fb7dd103b4c524eab5ecd72c4fdf` |
| `qualification/selector-timing.mjs` | `a0d954c07172526a6c731ba1fabf0e9c58f841cb` |
| `qualification/selector-timing-preload.mjs` | `0f81c56a19eb706b60de96b445c738716ec626aa` |
| `qualification/selector-timing-artifacts.mjs` | `7a37e76e7094424331ff88c5c5f42659515aa2ad` |
| `qualification/selector-timing-attempts.mjs` | `d4354f29b1a91dbbe1eb15e6b8a777fb1a49bd24` |
| `scripts/ordered-tests.mjs` | `35e62b14ea4e31284997b77fac8a85754814de2a` |
| `scripts/ordered-test-worker.mjs` | `73437411c41c65833a1993b64bff12faeea26855` |
| `qualification/selector-timing-driver.mjs` | `c9dc01d16455a7142c67d27ef861f3f4edbf81bb` |
| `scripts/test.mjs` | `bf97d2cb35814f682e4706150e1fb77f598733fa` |
| `scripts/build.mjs` | `74ecf1caa4983194e4b61da84b1da941b7a48305` |
| `scripts/package-release.mjs` | `85e3821cc38a7fa23f24b7f783bfdba86027e167` |
| `src/release.ts` | `e5e39666c24dac32907a5bad93804d0eb1126295` |
| `qualification/selector-timing-checks.qualification.mjs` | `59639e8705926b52b1b3f85909891351bfc4357c` |
| `qualification/selector-timing-closure-checks.qualification.mjs` | `22299c3926f25f3725f1be8392f97f8173565159` |
| `qualification/selector-timing-artifacts.test.mjs` | `d61a08cd14042c17f02bf385c58630a2e1493763` |
| `qualification/ci.test.mjs` | `6b2c0096f461a238621b3b023238532041141b23` |
| `test/learning.test.mjs` | `28b0ad08e57bcc8be4a7b9edfa4bc06bacab766d` |
| `test/learning-extraction-sources.test.mjs` | `671f40e8df8efee9c664ee7d5a57ef489c4cf66d` |
| `test/learning-extraction-paths.test.mjs` | `c4d4c15e9b143e721c9c985169938e344a45ad34` |
| `test/learning-extraction-evidence.test.mjs` | `34ff03119c41b50c3cee3aedfc8f01b643a7d0ff` |

End recheck at 2026-11-04 06:47 UTC: main HEAD advanced to `c0773effc31dbcd99c0ee2b8e0d2bccc93c1b945`. All inspected build/workflow/lifecycle/native-process/learning-host, timing/closure/driver, ordered-runner, and original learning-case source blobs remain identical to the table. Three integration surfaces changed: `scripts/test.mjs` is now `b79b7d464cac0a36dd9878b8c74c1327d69231dc`, `src/release.ts` is now `ab4e3205fce264e8cd67033cad88b4e73b4d9588`, and `qualification/ci.test.mjs` is now `9ac20c028588ab7fd6d76a14f069529a5af12193`. No changed content or private IR1 edits were inspected. The host/build observation seam is unchanged; root must reconcile registration, release-inventory and CI integration assertions against the new coordinated head before implementation. This packet does not claim an unchanged whole source tree or qualification of the new head.

Final handback recheck at 2026-11-04 06:50:54 UTC: HEAD is `523437121134b67f56d296c399f45afda9515fe3`; all 24 inspected blobs match the 06:47 recheck exactly. The same three explicitly recorded integration-surface differences are the only differences from the initial blob table. Root's API-error and graceful-143 CPU clarifications are incorporated; no task implementation or verification was executed.


## Accepted observation result

The ONE schema3 native observation41801476884/job126478025045 at exact5d843426d3a3e84e7a7a1556e3d32d2a60d838c2 passes08:47:01UTC. OriginalFULL31/31, zero fail/cancelled/skips/todo79.240682s; notifications13.192862s/15s and learning27.717300s/30s. Pinned preflight, exact-two guard/upload pass. Shared schema3 record/relationship/case/host validators and exact source/runtime reassessment confirm complete/exit0,2341 records,87 writers,84 self-closes,35 sync bindings/returned closures,11 async bindings/observed closures, all36 correlated hosts with genuine self-closes and original49 case endings. Observation-only acceptance MET. Historical schema2 exports stay immutable; no deadline/cause repair, compilerCPU, process-birth/descendant/invocation-completion or helper claim. Exports `/tmp/factory-host-observation-41801476884-artifacts/`; fulljob `/tmp/factory-host-observation-41801476884-job.log`.

All36 host CPU receipts are their own post-collector emitter intervals. The single async host has actual parent-observed exit143/failed, not an invented signal; its genuine self-close measures an interrupted interval only. CPU remains current-process-only and includes observer work; compiler/child and pre-collector work remain unknown.
