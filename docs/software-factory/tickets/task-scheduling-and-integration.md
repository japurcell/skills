# Task scheduling and integration

> Continuation amendment, 2026-10-15: these scheduling and freshness policies apply within a live invocation. [SSSF-style continuation](workflow-versioning-and-run-changes.md#resolution) retains their history but does not restore the scheduler, ready queue, reservations, or completed-task position after exit.

**Type:** grilling
**Status:** closed
**Blocked By:** workflow-authoring-and-task-contract.md, operating-and-installation-model.md
**Research Dir:** not applicable

## Question

How do dependent and independent implementation tasks execute and combine without conflicting changes or invalid evidence?

Decide task workspace ownership, the revision supplied to a ready task, scheduling order, concurrency/resource limits, and integration policy. Include dependency failures, overlapping edits, merge conflicts, test-resource collisions, and a dependency revised after downstream work starts.

Define what task completion means before and after integration, when downstream work or checks become stale, and what combined-result verification is required.

Resolution should walk through a three-task graph with parallel siblings and a dependent task, plus conflicting changes and a late dependency repair. Keep scheduling and integration decisions in code.

---

## Decision record

Claimed and resolved on 2026-10-13 through five human answer rounds, including the requested comparisons and concrete examples. The exact prerequisites, `workflow-authoring-and-task-contract.md` and `operating-and-installation-model.md`, were verified closed. The confirmed answers below own the accepted policies; the resolution combines them into a walkthrough and acceptance obligations.

### Prior answers applied

- [Workflow authoring and task contract](workflow-authoring-and-task-contract.md) owns validated task graphs, code-defined scheduling and managed operations, acceptance criteria, and dynamically discovered scopes. Do not ask again whether workflows or task graphs are configurable.
- [Operating and installation model](operating-and-installation-model.md) owns per-repository installation, foreground invocations, a TypeScript runner with SQLite history, explicit script invocation, and interruption without durable resume. Scheduling must not silently restart old work.
- [Agent execution profiles](agent-execution-profiles.md) owns fresh task/review sessions, compatible repair-session reuse, explicit fallback, and bounded visible recovery attempts. Those session decisions did not select filesystem workspace ownership; round one below now settles that choice.
- [Session events and live progress](session-events-and-live-progress.md) owns durable live/history events, retained registered evidence, and the one-second display target. Retaining evidence does not decide its validity after integration or dependency changes.
- Per-task or aggregate review, optional interactive verification, and optional pre-PR human review are already requirements. This ticket must accommodate them; detailed verification and repair policy remains in [Verification and review policy](verification-and-review-policy.md).

### Confirmed answers, round one

The human explicitly accepted all four recommendations on 2026-10-13.

1. **Workspace ownership:** a separate Git worktree per implementation task and a separate workspace for combining the run's changes, leaving the user's checkout untouched. Workflows can choose stricter serial execution. Isolation separates managed working files; it does not introduce a mandatory security sandbox or isolate shared external resources.
2. **Starting code:** a selected commit by default, with an explicit option to capture selected uncommitted changes into the run's starting snapshot. Later checkout edits do not change the captured input. The snapshot must identify the actual selected content; it is not a live reference to the user's checkout.
3. **Failure isolation:** after a task exhausts its configured repair policy, block dependent tasks while independent branches finish. The run remains incomplete; workflow code can opt into stopping the whole run. This does not change the accepted recorder-failure or explicit Pause behavior. Exact repair limits remain with verification policy.
4. **Concurrency scope:** repository-wide limits shared across foreground runners, with lower per-run limits permitted and separate counts for agent sessions and command processes. Round two below settles initial counts; process ownership and crashed reservations require recovery design.

### Confirmed answers, round two

The human accepted integration, initial capacity, and dispatch order on 2026-10-13. After requesting the shared-resource comparison below, the human also accepted isolation where possible and named reservations for shared resources.

1. **Integration:** integrate each task after its configured task checks pass, one integration at a time per run. Check the combined candidate before accepting it. Dependents wait until prerequisites are accepted into the combined result. Exact checks remain configurable.
2. **Initial capacity:** two active agent sessions and two managed command steps per repository, independently configurable. Parallel reviewers share the agent allowance. The limits cover factory-managed launches, not every subprocess an agent can start. These are selected starting defaults, not measured capacity or proven performance limits.
3. **Dispatch order:** stable declared task order within each run and round-robin turns across active runs; skip tasks whose dependencies or resources are unavailable. Workflow code may assign explicit priorities; already running work is not preempted.
4. **Shared resources:** use isolated resources where possible and named reservations for resources that must be shared. Workflow code defines resource setup, configuration, and cleanup; the factory does not infer arbitrary application resource dependencies. The comparison below retains the alternatives. A built-in environment pool is not selected by this decision.

### Shared-resource comparison and accepted direction

The original recommendation was named resource reservations declared in code: a step waits when a required resource is occupied, even when a session slot is free. The human requested alternatives, then explicitly chose isolation where possible together with named reservations for shared resources. Coordination across repositories requires an explicitly shared reservation scope; the concrete coordination mechanism is not selected here.

The comparison considers these approaches, which can be combined:

| Approach | Example | Tradeoff |
| --- | --- | --- |
| Separate resources per attempt | Each test attempt gets its own test database or schema, temporary files, and server port. | Preserves parallelism and avoids shared mutable state where the application supports isolation; requires explicit setup, configuration, and cleanup. |
| Serialize all verification | One verification operation at a time across the repository, whether command-driven or agent-led. | Coarse and easy to reason about, but makes unrelated checks wait and cannot coordinate an external process outside that scope. |
| Named exclusive reservations | Operations needing a fixed test database declare the same resource name and take turns. | Allows unrelated work to proceed, but correctness depends on complete declarations, consistent scope, and resource ownership through its full lifetime. |
| Pool of isolated environments | Two prepared test environments, each with its own database and server, are assigned exclusively while in use. | Bounds expensive setup and supports limited parallelism; adds environment reset and health checks before reuse. |
| Repository-owned coordination | Existing test scripts manage ports, isolation, and locking themselves. | Can reuse a mature setup; the factory sees only the managed step unless the workflow exposes resource waiting and ownership. |

The accepted direction is a hybrid: separate per-attempt resources where the repository supports them, and explicit named reservations for resources that must be shared. A pool remains an alternative when isolated environments are expensive to create; it is not a required built-in feature. Repository workflow code supplies setup, configuration, and teardown.

Worktree isolation does not isolate a shared test database or fixed server port. Concurrency limits cap work but do not identify collisions between otherwise eligible steps. Reservations coordinate participating operations, not arbitrary external or manually launched processes. A reservation must cover the resource's actual usage, including a server surviving its launch command; after interruption, reconcile possible owners before reuse. Exact ownership and recovery mechanisms remain downstream design work.

### Confirmed answers, round three

The human accepted the task input revision and bounded agent conflict repair on 2026-10-13. After comparing integration queue policies, the human also selected ready-result order as the default.

1. **Task input revision:** start each ready task from a captured copy of the run's latest accepted combined revision, including its accepted prerequisites. That task keeps this starting revision while it works; later integrations do not silently alter its files. Derived evidence obligation: record all task versions present in the snapshot, not only declared dependencies. The dependency-only snapshot alternative was not selected.
2. **Integration conflicts:** use a visible, configured agent repair step in an isolated candidate workspace, bounded by the workflow's repair policy, then rerun the required checks. Unresolved intent or exhausted budget blocks the affected integration for human input; it does not choose one side silently. Exact repair counts and review rules remain with verification policy.
3. **Integration queue order:** ready-result order is the default. Integrate eligible results in the order they become ready, with recorded ordering and task ID as a tie-breaker. This does not change the accepted stable dispatch order for starting tasks, serial integration within a run, or the requirement that prerequisites integrate before their dependents become eligible. Custom workflows may choose another explicit ordering policy.

### Integration-order comparison and accepted direction

Ready-result order was accepted as the default after the comparison below. A slow task that is not yet ready does not hold up an independent ready result. This is distinct from the already accepted stable order for starting tasks. The alternative waits for declared task order even when later independent results are ready. Neither option changes the accepted rule of one integration at a time per run or preempts an integration already in progress.

Here, declared integration order means an order consistent with task dependencies. Literal source-list order must not create a deadlock by waiting for a task before integrating its prerequisite.

| Concern | Ready-result order | Declared integration order |
| --- | --- | --- |
| Progress | Finished independent work can integrate and unblock its dependents while a slower task continues. | An earlier unfinished task holds later ready results and their dependents behind it. |
| Predictability between fresh runs | Completion timing affects integration order and the combined revision later tasks receive. | A fixed dependency-respecting order makes integration sequence less sensitive to completion timing. It does not make agent outputs identical. |
| Historical inspection | Record the selected order, candidate base, and outcomes for observation. A later invocation does not restore the queue. | Record declared and actual order for observation; no crash-resume guarantee is selected. |
| Conflict precedence | Whichever eligible result integrates first establishes the combined revision later results must accommodate. | Authors choose a planned precedence, but concurrent results can still overlap or conflict. |
| Failure handling | Excluding a blocked result from eligibility can allow unrelated results to proceed. | Needs an explicit rule for failed or blocked earlier entries to preserve the already accepted independent-branch progress. Otherwise strict waiting can stall the run. |
| Verification work | Each candidate still needs its configured combined-result checks. Timing can vary the bases used by newly started tasks. | Each candidate still needs its configured checks; fixed order does not by itself reduce check count or repair work. |

Illustrative timing only: A and B are independent. A becomes ready after ten minutes and B after two. C depends only on B. With negligible integration time and a free slot, ready-result order allows B to integrate and C to start around minute two. Declared order A, B, C holds B and C until A is ready around minute ten. If C depends on both A and B, neither policy can start C before both prerequisites integrate.

The selected default fits parallel task execution and the accepted independent-branch failure policy. Workflow code makes the decision from recorded readiness and eligibility; an agent does not choose the queue. When correctness requires A before B, encode that dependency instead of relying on incidental integration order. A custom workflow can deliberately prefer a fixed integration order. The human has also accepted parking blocked integration candidates, as recorded below.

### Confirmed answers, round four

On 2026-10-13, the human accepted **park candidate; continue others**. When an integration candidate needs human input, park it and let other eligible independent results integrate. Release the integration slot only after its active work has stopped or otherwise been safely reconciled. Before the parked candidate can be accepted, rebuild it against the then-current combined revision and rerun required checks. Detailed stale human-answer handling remains with human control and publication.

### Stale-work decisions and example

After the concrete example below, the human explicitly accepted both remaining round-four recommendations on 2026-10-13: track dependencies and snapshots, and interrupt stale work while preserving changes for refresh.

1. **Stale-work scope:** when an accepted task's content is superseded, mark work based on that older version stale, using both declared dependencies and the actual recorded input snapshots, then propagate to consumers. Preserve the work and its evidence, but require refresh before treating it as current. Ordinary additions of unrelated task results do not automatically make every running task stale; combined-candidate checks still apply at integration. Tracking only declared dependencies was not selected.
2. **Running affected work:** request graceful interruption and preserve saved changes when a task's inputs become stale. Once updated prerequisites are accepted, reuse saved changes in a tracked refresh attempt with the configured checks and repair limits. This does not reset budgets, discard the old evidence, authorize automatic recovery after a crashed runner, or decide how changes to a live run are approved. Letting stale attempts finish first was not selected.

#### Concrete example for both choices

This is an illustrative design scenario, not an executed workflow or authorization for arbitrary live-run edits.

1. Task A adds a `getCurrentUser()` helper whose first accepted version returns a user object.
2. Task B builds an account page. Its plan does not declare a dependency on A, but B starts after A integrates, so its captured starting revision includes A's helper. B's agent discovers the helper and uses `user.name` in the page.
3. Later human feedback identifies the signed-out case. An authorized repair to A changes the helper to return either a user object or `null`.
4. B's isolated workspace still contains the original helper. Its tests can pass against that old behavior while its page would fail for signed-out users against the repaired helper. Declared graph edges alone miss this newly introduced dependency. Recorded starting snapshots show B worked with the superseded version.

Under the accepted scope policy, B is stale until its applicability to A's repaired version is checked. Stale means not yet established as current, not proven broken in every case. Snapshot inclusion is conservative evidence of possible dependence, not proof that the agent used every file: a documentation-only task based on the same snapshot could also be flagged despite needing no edits. That conservatism can cost extra checks.

If B is still writing the page when the change is identified, the accepted interruption policy stops further work on the outdated assumption while preserving B's partial diff, transcript, and evidence. After the updated prerequisite is accepted, a tracked refresh attempt reuses the saved layout and other changes, adds signed-out handling where needed, and runs the configured checks against the updated code. Compatible session reuse follows the already accepted profile policy; prior attempts remain historical and budgets do not reset. B's active worktree is not silently edited underneath its running agent.

The unselected alternative lets B finish using the old helper, then performs the same refresh before acceptance. This avoids disrupting a nearly finished attempt, but can spend tokens on additional code and tests that will need correction. If B has already finished, the interruption choice no longer applies; its result still needs the freshness check under the accepted scope policy. The factory identifies recorded revision changes in code; it need not ask an agent to guess whether two versions match.

### Confirmed answers, round five

The human explicitly accepted both remaining recommendations on 2026-10-13.

1. **Already integrated stale content:** if invalidated output is already part of the combined result, pause new ordinary task starts and ordinary integrations while a dedicated repair phase refreshes that result. Preserve all work; unaffected active attempts may finish and queue their outputs. Repair/check steps remain permitted under existing capacity and budget policies. Resume ordinary scheduling once required checks establish a current combined revision. Reconstructing a separate baseline to keep ordinary scheduling running was not selected. This concerns a stale combined input, not merely a parked unintegrated candidate; the accepted parking policy still applies when the combined input remains current.
2. **Review write ownership:** in the default review/refactor recipe, reviewers inspect a fixed revision and return findings. A separate repair step owns code edits, with one active writer per mutable workspace. Tools that generate files use separate attempt scratch space or a disposable checkout, preserving the reviewed revision. Custom workflows can deliberately compose review and repair through explicit managed operations. Reviewer-generated patches were not selected for the default recipe. This does not change the accepted fresh-review session policy or introduce a mandatory factory sandbox.

### Derived completion obligations

These distinctions follow from accepted task checks, serialized integration, retained evidence, and stale-work handling; they are not renewed policy questions:

- An agent finishing is an attempt outcome. A task result passing its configured task checks makes that result eligible for integration, subject to freshness and dependencies. A task is integrated only after its combined candidate meets the configured integration checks.
- Evidence records the exact content and inputs it checked. Historical evidence remains available after content changes, but cannot silently certify a changed candidate. Required combined-result checks apply to the actual accepted result; final review, check selection, and repair budgets retain their verification-policy owner.
- A parked, failed, or stale required task prevents overall successful completion. Optional pre-publication human review remains separately configurable. Task or integration success does not itself authorize publication.
- Preserve task output identity and its change relative to its captured input so integration or refresh cannot accidentally reintroduce superseded input content. Concrete Git representation, transactional publication of a revised combined result, and crash reconciliation remain downstream mechanisms.

## Resolution

Closed on 2026-10-13 after the human selected both round-five recommendations, completing this ticket's policy choices. The accepted answers above remain configurable workflow defaults where stated. Identity, ownership, truthful evidence, and recovery obligations apply to custom workflows as well. The following walkthrough derives from those answers; it does not introduce another pipeline or authorize implementation.

### Three-task walkthrough

Tasks A and B are independent; C depends on both. Begin with captured starting revision R0 and no other active runs consuming capacity.

1. **Parallel work:** A and B start in separate task worktrees from R0. C waits. Each task uses its configured profile; the default repository allowance permits two active agent sessions. Commands have their separate allowance. Resource reservations may reduce actual parallelism below those limits.
2. **First integration:** B finishes its configured task checks first. Its ready result enters the integration queue. Construct and check a candidate combining B's change with the current accepted revision; acceptance produces R1. A keeps its original worktree. Adding independent B does not itself make A stale.
3. **Second integration:** A becomes ready. Apply A's own change to R1 in the integration workspace, preserving A's original input and output provenance. If the changes combine and required checks pass, accept R2. If A and B conflict, use the configured bounded agent repair step, then recheck the combined candidate. Reviewers return findings against a fixed revision; the repair step is the writer.
4. **Human wait:** if A's conflict needs human input, park the candidate after active work is safely stopped. The accepted R1 remains current. Other eligible independent results may integrate, but C cannot start because A is not accepted. Rebuild and recheck the parked candidate against the current accepted revision before later acceptance; an old candidate or decision cannot silently certify newer content.
5. **Dependent work:** after A and B are both accepted, C starts from the then-current accepted combined revision, recording the actual versions it received. C follows the same task-check, ready-result, candidate-check, and acceptance path. Final workflow gates still decide whether the overall result may proceed to a configured human checkpoint, publication, or another custom stage.

### Late repair and refresh

Suppose C is running when an authorized repair supersedes A's accepted content. C becomes stale through its declared dependency and captured input. Interrupt C gracefully and retain its changes, transcript, evidence, and consumed budgets. Existing work is not deleted or silently relabeled as fresh.

Because the combined result contains A's now-invalidated output, enter the accepted repair phase: ordinary task starts and integrations pause. An unaffected active task may finish, but its ready result waits. Repair and verification operations continue subject to the same resource limits and explicit budgets. Once the repaired combined revision is current, C can refresh its saved changes against it and ordinary scheduling resumes.

If C had already integrated before A was superseded, C's integrated contribution also needs refresh within that repair phase. Refresh upstream changes before consumers that require them. A validated upstream repair result may feed a dependent repair step inside the phase; it does not by itself declare the whole combined result current. Ordinary scheduling resumes only after the affected combined result satisfies the configured checks. Prior accepted revisions remain identifiable historical records. Exact Git representation and safe acceptance of a refreshed combined result belong to the live runner lifecycle design.

This repair phase differs from parking an unintegrated candidate. Parking leaves the accepted combined input usable; invalidating content already in that input suspends its use for ordinary scheduling. Normal managed refresh applies only while the workflow invocation is live. After runner exit, further work requires a separate explicit script invocation; no refresh position is restored.

### Implementation acceptance obligations

These are required future checks, not evidence that an executor exists or passes them:

- Preserve the user's checkout while capturing a selected commit or explicit uncommitted snapshot. Later checkout edits cannot mutate a run's recorded input. Keep task changes distinguishable from their inherited baseline.
- Exercise A and B running concurrently with C blocked, B becoming ready first, and C receiving the actual accepted combined revision only after both prerequisites integrate. Save queue decisions for history; a later invocation starts its selected workflow anew rather than restoring that queue.
- Run multiple foreground runners for the same repository. By default their combined active usage cannot exceed two agent sessions and two managed command steps. Verify lower per-run limits, fair default turns, explicit priorities, and visible resource waits. Test the live-progress latency target under a documented workload including these concurrent operations; the chosen limits are not a performance measurement.
- Exercise isolated test resources and contention for named shared resources. Wait for every required reservation before dispatch. A stopped runner is not proof that a child server released its resource; uncertain ownership must be reconciled before reuse. The scheduler must avoid reservation deadlocks without reserving capacity indefinitely for work unable to proceed.
- Review a fixed revision in parallel without shared mutable output paths. Verify one writer per mutable workspace, retained findings, and a separately visible bounded repair attempt. Compatible session reuse must preserve attempt identity and budgets.
- Exercise conflicting task edits, a successful bounded repair, exhausted repair policy, human waiting, other eligible integration during parking, and revalidation when the parked candidate returns to a changed combined revision.
- Supersede a task version used through an explicit dependency and one present only in a recorded starting snapshot. Preserve stale outputs and evidence; interrupt active affected work and require refresh. Adding an unrelated new task must not trigger blanket staleness by itself.
- Invalidate content already integrated into the combined result. Check that ordinary dispatch/integration pauses, unaffected active work may finish, repair/check operations remain possible, and ordinary scheduling resumes only after the refreshed combined result is current. Include an already integrated affected descendant and an interrupted refresh left incomplete in history and a separately invoked follow-up workflow that explicitly consumes preserved work.
- Required failed, parked, or stale tasks cannot silently become overall success. An old passing check cannot certify different content. Disabled checks, exact evidence reuse rules, and optional final stages remain explicit verification/workflow policy.

### Downstream owners and limits

- [Verification and review policy](verification-and-review-policy.md) owns check selection, optional expensive verification, reviewer aggregation, assignment of repairs, exact rerun/reuse rules, and numerical retry/repair budgets. Findings followed by a separate writer, bounded visible conflict repair, and the freshness obligations above are settled inputs.
- [Human control and publication](human-control-and-publication.md) owns checkpoint decisions, stale and duplicate answers, revision-bound approval, and publication controls. Parking is settled; an integration result still does not grant publication authority.
- [Workflow versioning and run changes](workflow-versioning-and-run-changes.md) owns current-code invocation and history/context reuse. In-invocation repair/freshness checks do not create an arbitrary suspended-plan editing feature.
- [Invocation lifecycle and interrupted work](recovery-and-runtime-selection.md) owns process/workspace/reservation ownership, incomplete history after crashes, safe handling of preserved files, and uncertain effects. No scheduler replay, restored execution graph, or retained executable versions are required.
- [Swimlane interaction design](swimlane-interaction-design.md) owns presentation of waiting, parked, stale, refreshing, task-accepted, and integrated work using the accepted saved event contract. These terms describe distinguishable facts, not finalized database enum names.

No new ticket is needed: remaining mechanisms and proof obligations have existing owners. No runtime, scheduling, Git integration, native-platform, resource isolation, recovery, or latency behavior was implemented or tested. The examples are design walkthroughs only.

