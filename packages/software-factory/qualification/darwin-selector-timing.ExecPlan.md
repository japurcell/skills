# Darwin selector timing qualification

## Purpose / Big Picture

Collect bounded, sanitized test-only timing evidence for the unchanged public fixtures command. This does not repair or qualify either deadline. The retained Darwin run41761716711 failed the complete notification15s and learning30s selectors; the isolated3833ms replay was one learning case only. Production changes, workflow changes, native execution and source acceptance belong to the integration coordinator.

## Progress

- [x] [milestone-1] Read decisive diagnosis and verify integration base fc0aabce.
- [x] (2026-11-04) [milestone-1] Implement collector, driver, fixed registry/schema and narrow default-off test hooks.
- [x] (2026-11-04) [milestone-1] Prove bounded schema, real Node case/ordered-worker receipts, preflight refusal and read-only paging with pinned Node24.22.1:9/9 synthetic cases pass,434ms.
- [x] (2026-11-04) [milestone-1] Commit packet81d920cb, merge latest integrationce314373 without rebasing as9a407ce3, and reverify9/9synthetic checks under frozen pinned PATH,455.633792ms; clean scoped diff and syntax checks pass.
- [x] (2026-11-04) [milestone-2] Coordinator ran exactdafc1a20 native41769336098:original31/31 fixtures pass, two validated sanitized exports retained, fixtureExitCode0/statusincomplete truthfully preserved.
- [ ] [milestone-2] Assess41worker-open/38close and complete/partial evidence before any timeline causality or deadline qualification claim.

## Context and seams

The ordered worker uses node:test run() and the learning selector uses the ordinary CLI runner. Immediate dequeue/complete events or direct fixture markers establish execution timing; buffered TAP start/pass do not. The authorized synthetic seams are the qualification collector/driver artifact boundary and its read-only attempt timing adapter. No full fixtures or product workload may run locally while the other private proof is active.

Task graph: telemetry-packet has no implementation prerequisite beyond the decisive diagnosis and completes milestone1. Native-experiment depends on telemetry-packet, coordinator-owned frozen canonical preflight and all other private load being quiescent; it completes milestone2 only when the retained complete fixture result and sanitized timeline have been assessed.

## Plan of Work

### Milestone1: test telemetry packet

Status: done
Acceptance: met

Add fixed-schema JSONL with per-run opaque worker/invocation/attempt IDs, monotonic markers, process CPU deltas, fixed registered file/case labels, fixture setup/copy/commit/invoke/dispose markers and paged persisted attempt events. Default is off. Bound process records, process files, bytes and database rows; invalid or incomplete collection must never claim complete. Only helper-owned disposable stores are readable. Never export argv, environment, raw errors, inputs, captures, raw paths, database IDs or PIDs.

### Milestone2: one native experiment

Status: in progress
Acceptance: not met

Coordinator owns fixed dependency/Python/Node/PATH receipt preflight, source freeze, remote launch and artifact staging. Run all existing fixtures, preserving notification10files/36cases/concurrency4 and learning4files/13cases/concurrency2, original15/30s wrappers and1000ms cancellation grace. Keep original test exit even when red. Inspect the timeline before choosing any optimization or scheduling candidate. No unchanged retry is authorized by this packet.

## Validation and Acceptance

From packages/software-factory run `/Users/adam/homebrew/bin/rtk proxy env PATH=/private/tmp/factory-qualified-node-342t16a/node-v24.22.1-darwin-arm64/bin:/usr/bin:/bin:/usr/sbin:/sbin node --test qualification/selector-timing-checks.qualification.mjs` with loginfalse. After integration merge9a407ce3 observed9pass/0fail/0skip/0cancelled/0todo,455.633792ms; retained log `/tmp/factory-darwin-selector-timing-synthetic.log`. The synthetic files run only tiny test callbacks, preflight rejection and a newly created minimal SQLite database. All ten changed JavaScript modules pass pinned Node syntax checks, and `git diff --check ce314373` passes. No product fixtures, builds, providers or desktop delivery ran. Native acceptance remains open.

## Decision Log

-2026-11-04: telemetry only. Existing evidence shows progressing cumulative work and does not establish contention, deadlock or a production bottleneck.
-2026-11-04: direct read-only paged SQL exports only event at/kind plus allowlisted operation classification; readHistory is unsuitable because it reads capture text.

## Surprises & Discoveries

- Learning extraction currently uses the ordinary Node CLI runner, not the ordered worker. Both need immediate direct case receipts.
- Disposable temporary paths can have a platform alias. The fixture ownership receipt is keyed by realpath, verified by the actual subprocess paging test.

## Concrete Steps / Recovery

Telemetry is normally integrated at20091003 within7de6bce8. Coordinator next: run the dedicated `.github/workflows/darwin-selector-timing.yml` from the stable merged head; its explicit `--selector-timing-export` option replaces only the original fixtures phase with the driver, leaving ordinary foundation unchanged. Preserve the existing pinned Node24.22.1, Python3.13.14, dependency/cache/PATH and receipt preflight; wait for all private proof/load to be quiescent and freeze the exact composed source. In packages/software-factory run `rtk proxy node qualification/selector-timing-driver.mjs "$RUNNER_TEMP/selector-timing-export"` using a destination that does not exist. The driver launches the original `node scripts/test.mjs fixtures` exactly once, with the two diagnostic activation variables inherited only as inert metadata by product children and a fixed `--import` added only to test workers. No NODE_OPTIONS or product arguments are added. Author implementation, scoped commit, latest-integration merge and permitted local verification are complete.

Coordinator guard `selector-timing-artifacts.mjs` validates canonical no-follow bounded regular files, exact schema/source/runtime, timeline coverage/partial status and stages an absent private upload directory containing exactly two files. Dedicated workflow uploads only those staged files, including valid incomplete evidence while preserving original red status; never private root. Profiling preflight verifies receipt/Python/child PATH and fresh copied offline toolchain cache. Official Node24.22.1 [parseArgs](https://nodejs.org/download/release/v24.22.1/docs/api/util.html#utilparseargsconfig) and [filesystem](https://nodejs.org/download/release/v24.22.1/docs/api/fs.html) contracts inform this CI boundary. New head includes backup code; do not claim same-source causality against8f59d77b without comparison.

Stage only the two exact files `selector-timing-export/selector-timing.json` and `selector-timing-export/selector-timing.jsonl`. The driver creates its private evidence root exclusively with mode0700, never publishes its owner token/path, never scans processes and never removes a caller destination. Do not stage its private root or disposable stores. The driver preserves a red fixture exit; if fixtures pass but diagnostic coverage is incomplete its profiling guard exits1. On invalid evidence it emits only a fixed incomplete diagnostic. Missing worker closures/open spans, bounds, or missing any of the49selected case endings or managed git/build/fake-agent classes prevents complete status. A deadline failure can therefore produce a valid useful partial timeline labeled incomplete; this is not a missing-product-assertion waiver.

The collector uses128exclusive numbered file slots, at most4096records/2MiB per process,16MiB total, and4096attempt rows per helper-owned fixture. Exceeding a bound is incomplete, never a truncated complete export. On I/O loss it stops emitting and leaves closure incomplete while fixture cleanup behavior continues. Invalid persisted metadata produces an incomplete export marker and does not replace the fixture result. Reusing an export destination fails before fixtures begin. Preserve all original output and the metadata fixtureExitCode on red; do not retry unchanged.

Provider qualification remains blocked; general reviews deferred; desktop notifications last.

## Fixed schema and interpretation

Every JSONL record has exactly schema,workerId,sequence,monoMs,epochMs,stage,phase,fileId,caseId,spanId,invocationId,attemptId,operationClass,at,wallMs,cpuUserUs,cpuSystemUs,disposition,exitCode. IDs are fresh opaque UUIDs; fileId is a fixed registered basename and caseId is a1based index into selector-timing-registry.json. Unknown names/paths are omitted. Stages and dispositions are enumerated in selector-timing.mjs. Span begin/end pairs share spanId. Result spans link to the same opaque invocationId as persisted attempt records. No raw errors, argv, captures, environment, database IDs, raw paths or PIDs are exported.

monoMs is host monotonic time; epochMs is the emission wall-clock anchor. Persisted attempt at is the original UTC event time, not its later export emission time. Started-to-settled duration is managed-attempt wall time, not compiler CPU. cpuUserUs/cpuSystemUs are the emitting process's own CPU only; spawned Git/compiler/agent CPU is not measured. Spans nest, so their durations and worker sums must not be added into selector wall time. worker-open means collector initialization, not an OS process-birth receipt. Ordered dequeue/complete and direct tracing-channel case begin/end establish actual execution boundaries; buffered TAP reporting does not.

Metadata contains source SHA, runtime executable SHA256, pinned Node version, runtime OS release, platform/architecture, runner image/version, availableParallelism, original fixture exit and fixed clock/CPU labels. It does not establish a causal bottleneck. The timing driver does not replace canonical receipt preflight or native acceptance.

## Primary references

Pinned Node24.22.1 [event lifecycle](https://nodejs.org/download/release/v24.22.1/docs/api/test.html#event-lifecycle), [test tracing channels](https://nodejs.org/download/release/v24.22.1/docs/api/test.html#test-instrumentation-and-opentelemetry) and [getTestContext](https://nodejs.org/download/release/v24.22.1/docs/api/test.html#gettestcontext) establish immediate receipts and direct fixture context. Real pinned-runtime subprocess tests verify these APIs. The versioned SQLite documentation was unavailable through the browsing tool; the adapter uses the same readOnly DatabaseSync option as existing store source and the synthetic test verifies byte-identical database content after paged reads.

## Outcomes & Retrospective

Telemetry packet and final merged9synthetic checks are complete. Native experiment41769336098 ran atdafc1a20:fixtures31/31,74.635s; notification10.216s/learning25.887s pass original wrappers, but metadata fixtureExitCode0/statusincomplete remains a failed diagnostic (2121records,41opens/38closes,all49selected endings). Two-export guard/upload pass. Root still assesses closure gaps and baseline; no deadline repair or complete-timeline claim. Retained exports `/tmp/factory-darwin-selector-timing-41769336098/`, log `/tmp/factory-darwin-selector-timing-41769336098-failed.log`. No deadline repair, native pass or bottleneck attribution is claimed. Reflection: the temporary-path alias issue is prevented structurally by canonical ownership keys and a real subprocess check; no separate durable brain or skill change is needed. No skill improvements identified.
