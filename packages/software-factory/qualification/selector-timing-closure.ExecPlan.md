# Preserve real closure receipts during selector cancellation

## Purpose / Big Picture

Repair test telemetry closure bookkeeping only. Native41769336098 atdafc1a20 passed all31original fixture cases, notification10.216s under15s and learning25.887s under30s, while its profiling guard truthfully failed:2121valid records,41worker-open/38worker-close. Exactly three unlabeled streams end in cancel/mark. Their identity is not proven by these records. This success does not explain the earlier8f59d77b deadlines. Preserve actual test/process cancellation, all guards and1000ms grace.

## Progress

- [x] (2026-11-04) [milestone-1] Inspect retained records and actual integration87ed5e7c source in a fresh private worktree.
- [x] (2026-11-04) [milestone-1] Controlled resistant cancellation first failed incomplete with status1/signalnull identical off/on; retained red log `/tmp/factory-selector-closure-red.log`.
- [x] (2026-11-04) [milestone-2] Add v2 bounded receipts tied only to a fresh owned child and actual spawn, matching exit and close observations; no closure is inferred from intent or labels.
- [x] (2026-11-04) [milestone-2] Verify normal exit, explicit process.exit, default SIGTERM/SIGINT and all3ordered cancellation paths off/on; prove signal intent and exit without EOF are insufficient.
- [x] (2026-11-04) [milestone-2] Merge latest integrationebbb82e2 without rebasing; final verification and scoped clean commit are retained at handback.
- [x] (2026-11-04) [milestone-3] Normally integrated at437839f8 over06ceae38; coordinator19/19 synthetic/artifact and unchanged default-off ordered-runner7/7 pass, plus syntax/actionlint.
- [x] (2026-11-04) [milestone-3] Exactb3d7cc77 native41773952580/job126389835263 passes original31fixtures, schema2complete/2161records,51workers/48selfcloses/10bound parent closes and all49selected endings. Preflight/guard/upload pass; baseline/timeline assessed, no oldcause/deadline repair claim.

## Context and Task Graph

The original collector wrote worker-close from a process exit listener. Ordered cancellation fixtures deliberately include a child that ignores SIGTERM. scripts/ordered-tests.mjs already force-closes only its owned tree after1000ms and observes its child close event. The controlled reproducer confirms that the killed worker cannot write its self receipt after forced SIGKILL. Its dequeue/cancel/complete/summary/cancel sequence matches the retained shape. The historical three unlabeled writers still lack a proven process/case assignment; they are not retrospectively relabeled or waived.

Tasks: reproduce has no dependency beyond retained evidence. Receipt-repair depends on reproduce. Synthetic-verification depends on receipt-repair. Native-experiment depends on synthetic-verification, coordinator integration, canonical pinned Node/Python/dependency/PATH receipt preflight and quiescent private load. Production code, workflow/CI, provider/auth and desktop execution are outside this author's ownership. General reviews stay deferred.

## Plan of Work

### Milestone1: real controlled reproduction

Status: done
Acceptance: met

Use tiny disposable Node test files and actual ordered cancellation. Compare status/signal/closure with telemetry disabled and enabled. No full fixtures, product work or native workload runs locally. Keep original failure evidence unchanged.

### Milestone2: closure-only packet

Status: done
Acceptance: met

Keep child self receipts distinct from parent-observed closure. Any observer must bind an opaque identity to its own newly spawned child and require actual exit plus stdio close, preserving the original result and cancellation path. Add no signal handlers, PID scans, process assertions, registrations or guard changes. Fixed-schema exports stay bounded and private; missing receipts remain incomplete, and case coverage never substitutes for closure. Use pinned Node24.22.1 synthetic checks and syntax/whitespace checks only.

### Milestone3: native diagnostic acceptance

Status: done
Acceptance: met

Coordinator owns integration, native rerun and exact two-file validated upload. The new native pass41773952580 atb3d7cc77 provides complete telemetry and assessed current baseline. Original31fixtures pass86.918248s; notifications14.193563s/15s and learning29.507626s/30s. No old deadline cause or repair is claimed; exact2sanitized exports and job log retained under `/tmp/factory-selector-closure-native-41773952580-artifacts/` and `-job.log`. Current3writers without selfclose each have actual parent SIGKILL closure; historical3writers remain unassigned.

## Validation and Acceptance

In packages/software-factory use `/Users/adam/homebrew/bin/rtk proxy env PATH=/private/tmp/factory-qualified-node-342t16a/node-v24.22.1-darwin-arm64/bin:/usr/bin:/bin:/usr/sbin:/sbin node --test qualification/selector-timing-checks.qualification.mjs qualification/selector-timing-closure-checks.qualification.mjs qualification/selector-timing-artifacts.test.mjs`. The19synthetic checks include real normal/explicit exits, default SIGTERM/SIGINT with zero added signal listeners, all3owned-tree cancellation controls off/on, no early receipt from signal intent, and exit without stdio EOF. Original status/signal results remain unchanged; queued cases remain unstarted, and forced cancellation still uses the existing1000ms grace.

The v2 artifact controls retain private-field, duplicate-key, no-follow, size, exact-two-file, original red fixture exit and source/runtime checks. They reject unknown/mismatched/duplicate/cyclic/early relations or impossible outcomes even when evidence is partial. A complete49case fixture with an unclosed writer still fails; adding the valid bound observed closure passes the same staging boundary. Pinned Node syntax and git whitespace checks pass. Native/full fixtures remain coordinator-only.

Final merged-source proof at integrationebbb82e2:19pass/0fail/0skip/0cancelled/0todo,7541.098ms; `/tmp/factory-selector-closure-final-green.log`. The initial red log retains the original incomplete assertion after2202.474792ms. These synthetic timings are not hosted performance evidence.

## Decision Log

-2026-11-04: do not reinterpret or waive the three historical missing writers. Repair receipt semantics and demonstrate the mechanism with new controlled children.
-2026-11-04: no signal handlers will be added. A parent observation is useful only after real owned-child exit/stdio closure and must have a distinct receipt type.
-2026-11-04: schema2 adds only subjectWorkerId. worker-bind reserves a new opaque ID before the exact owned spawn; it is not a process-birth receipt. The ID enters only that ordered worker's test config, not product arguments/environment. Parent observation requires the actual child spawn event, its exit event and its later matching close event. Self worker-close and parent worker-close-observed remain distinct.
-2026-11-04: driver collection and upload staging share validateWorkerClosure. Incomplete valid evidence stays incomplete; forged relationships are refused. Parent-observed records carry no inferred child CPU or invented case endings, and certify only the targeted child, not arbitrary descendants. Existing owned-tree guards remain separate and unchanged.

## Surprises & Discoveries

- Existing ordered cancellation can intentionally require forced termination after its test stream already emits a summary. A summary or disconnect is not a process-closure receipt.
- Node's normal and explicit process.exit paths execute exit listeners; default signal termination does not offer the same JS receipt. Adding SIGTERM/SIGINT listeners would change the behavior under test, so the repair adds none. The real subprocess parity controls encode this constraint.

## Concrete Steps / Recovery

Coordinator integrated and ran the sole changed remote experiment at immutableb3d7cc77, retaining canonical pinned Node24.22.1/Python3.13.14/PATH/dependency/cache receipt preflight. No broad local proof overlapped private backend load. Next: retain assessed baseline and await root's next bounded decision; no repeated experiment is selected. Use the existing dedicated workflow and exact two validated export paths. No workflow or production file changed here. New exports use schema2 and the updated guard; retained schema1 artifacts are unchanged and remain incomplete. Do not retry the old unchanged source or claim a causal repair for8f59d77b. Provider qualification stays blocked; independent reviews deferred; desktop notifications last.

Source recovery remains bounded: missing closure/unfinished spans/bounds/coverage keep diagnostics incomplete. Unknown, inconsistent or cyclic mappings fail the profiling/export guard. No generic process scan, signal interception or inferred closure is used.

## Primary sources

Pinned Node24.22.1 [process exit](https://nodejs.org/download/release/v24.22.1/docs/api/process.html#event-exit) and [signal events](https://nodejs.org/download/release/v24.22.1/docs/api/process.html#signal-events) establish the normal/explicit exit paths, unconditional SIGKILL and the behavior change caused by adding signal listeners. Its [child close event](https://nodejs.org/download/release/v24.22.1/docs/api/child_process.html#event-close) occurs after process exit and stdio closure, or after an error on spawn failure; the observer therefore requires a successful spawn and matching exit separately. Real pinned-runtime EOF and signal controls verify the implemented distinction.

## Outcomes & Retrospective

Controlled red reproduction and closure-only repair are complete. The three historical streams remain unattributed. Current native31/31 atdafc1a20 is retained as a successful original fixture result and a failed incomplete diagnostic; new schema2 native41773952580 atb3d7cc77 supplies complete assessed closure/timeline and original31/31fixtures, while the old deadline cause/repair remain unproved. Reflection: real off/on signal parity, intent/EOF negative controls and one shared strict relationship validator encode the durable lesson; no separate brain or skill change is needed.
