# Human control and publication

**Type:** grilling
**Status:** claimed by subagent-h6p9k2
**Blocked By:** task-scheduling-and-integration.md, verification-and-review-policy.md
**Research Dir:** not applicable

## Question

Where can a workflow request human input, and what must be true before it creates a PR or another external artifact?

Decide optional checkpoint semantics, approve/revise actions, timeouts, authorization, binding decisions to evidence and revisions, and rejection of stale or duplicate decisions. Apply the accepted Pause/Continue/Cancel controls below. Clarify workflow review versus a harness's native tool approval.

Apply the closed [Verification and review policy](verification-and-review-policy.md#resolution): unresolved blocking disputes reach human input after one clarification round; attempts, evidence, budgets, and timeouts remain recorded; Continue does not renew limits or satisfy a missing gate. Discuss authorization for deliberate changes and how the human responds, without re-asking accepted verification defaults. Attempt timeouts do not select human-checkpoint deadlines or make pre-PR human approval mandatory.

Apply the accepted resumable Pause/Ctrl+C policy in [Operating and installation model](operating-and-installation-model.md#resolution); do not re-ask whether Pause interrupts or drains active steps, or whether Cancel is terminal. Define steering actions, signal escalation, child-process and orphan handling, treatment of active runs during uninstall, and which changes require a new run or checkpoint.

Set publication identity and reconciliation rules for a crash after the remote action but before recording its result. PR creation, pushing, merging, and deployment are separate actions; do not infer authorization from one to another.

Resolution should specify the human interaction contract and acceptance cases for stale approvals and duplicate publication.

---

## Decision record

Claimed on 2026-10-14 after verifying both exact prerequisites, `task-scheduling-and-integration.md` and `verification-and-review-policy.md`, are closed. The user requested this ticket explicitly. This is planning only; no runtime implementation or external publication is authorized.

### Prior answers applied

- [Confirmed factory requirements](confirmed-factory-requirements.md#confirmed-requirements) already makes pre-PR human review configurable. Arbitrary code-defined workflows may place checkpoints where needed; the six-stage recipe is not a mandatory pipeline. Do not ask whether human pre-PR review is always required.
- [Operating and installation model](operating-and-installation-model.md#selected-executor-and-continuation) owns one foreground runner per invocation and explicit human-triggered Continue. Opening the repository, dashboard, or a new invocation does not automatically resume old work. Continue is not approval, a budget reset, or permission to blindly repeat effects.
- The [operating resolution](operating-and-installation-model.md#resolution) already selects resumable Pause/Ctrl+C, preserving work and history, and data-preserving uninstall with a separate purge. Pause stops new dispatch and requests graceful interruption rather than merely draining active steps. The control was originally named Stop; the accepted rename below changes its label, not its behavior. Its signal escalation and uncertain child-process handling remain mechanisms for this ticket and recovery.
- [Agent execution profiles](agent-execution-profiles.md#resolution) owns existing harness authentication and permission controls, with no mandatory factory sandbox. Native tool approvals stay distinct from workflow checkpoints and cannot be silently approved or bypassed. The initial trust model is local single-user operation in explicitly selected trusted repositories, with credentials outside repository settings and logs.
- [Session events and live progress](session-events-and-live-progress.md#resolution) owns the independent on-demand repository dashboard, saved-before-display events, SSE updates, separate HTTP controls, and immutable registered evidence. Closing the dashboard does not stop an independently running invocation. How a UI Continue starts or attaches to a foreground invocation is explicitly unresolved here.
- [Task scheduling and integration](task-scheduling-and-integration.md#resolution) owns independent-branch progress, parking unintegrated candidates awaiting input, and pausing ordinary scheduling when stale code is already integrated. A human response cannot bypass rebuilding/rechecking a parked candidate against changed combined inputs.
- [Verification and review policy](verification-and-review-policy.md#resolution) owns required/advisory gates, criterion-level evidence, bounded repair and correction, attempt timeouts, and one reviewer-clarification round before unresolved disputes reach a human. Missing required evidence and exhausted allowance do not become success through Continue. Attempt timeouts exclude recorded human waits but do not select checkpoint deadlines.
- Stale approvals and duplicate publication remain required acceptance scenarios from the user's earlier prototype request. Task/gate acceptance does not itself authorize publication. Exact approval identity, stale/duplicate response handling, and remote-effect reconciliation still need to be specified; do not treat prior illustrative methods as finalized interfaces.

### Confirmed answers, round one

On 2026-10-14, the human explicitly accepted the following four choices, requested a Cancel comparison, then accepted both controls with the rename recorded below:

1. **Checkpoint deadlines:** no deadline by default, with the request saved across runner exits. Workflow code may configure expiry and its outcome; expiry never implies approval. A twenty-four-hour default deadline was not selected.
2. **Request changes:** route human feedback to the recipe's configured repair step within existing budgets, then run required checks and create a new checkpoint for the changed candidate. Feedback does not silently expand scope. Waiting for manual edits was not selected as the default.
3. **Limit increases:** allow an explicit UI action showing consumed allowance and the proposed new total for the selected scope, recording the change without resetting counters. Continue alone adds nothing; checks and publication authorization remain separate. Requiring a new run merely to obtain more allowance was not selected.
4. **Initial publication hosts:** GitHub PRs first, behind a managed publication interface that can support later hosts. Adding GitLab or Azure DevOps to the initial built-in scope was not selected. This is product scope, not verified provider behavior.

These four choices are settled and must not be asked again.

### Accepted Pause and Cancel controls

On 2026-10-14, after the comparison, the human explicitly chose both controls and renamed **Stop** to **Pause**. This completes the first round's fifth choice. The product controls are Pause, Continue, and Cancel; there is no separate Stop control or newly selected drain-only Pause action.

- **Pause:** stop new dispatch, request graceful interruption of active work, and preserve the unfinished run for Continue. Saved state, pending checkpoints, consumed budgets, and applicable elapsed-time accounting remain intact. Ctrl+C keeps this same resumable behavior. Pause does not mean suspending every process in memory or letting all active steps finish first.
- **Continue:** resume the selected unfinished run under the already accepted reconciliation, version, evidence, and budget rules. It does not approve a checkpoint or add allowance.
- **Cancel:** end the run after active work and effects are reconciled. Retain history, evidence, and partial changes, but do not allow Continue on the cancelled run. Further work requires a new run, which may explicitly use preserved changes as inputs.

Pause fits "resume this run later"; Cancel fits "abandon this run." Both request interruption and preserve evidence. Neither deletes history, discards code, or automatically undoes a PR or push that already happened. Ended cancelled runs must remain distinguishable from resumable unfinished runs. Exact stopping/escalation behavior still follows the unresolved mechanism questions below.

The alternative of keeping only a resumable control was not selected. Do not ask the human to choose these controls or their names again. No subsequent question round was started while answering the naming question.

### Follow-on decisions

Use the answers to resolve checkpoint responses and lifecycle, approval/action identity and changed evidence, duplicate controls, limit-change authorization, and the interaction of checkpoint responses with a stopped runner. Set the UI Continue/foreground-launch interaction without replacing the settled operating model. Specify native harness approval routing, local control authorization, stop escalation, orphan uncertainty, and active-run uninstall behavior.

GitHub is selected for initial built-in publication. Settle launch-time publication authorization, default publication outcome, action granularity, stable publication intent, partial outcomes, and reconciliation of uncertain remote effects. If these decisions need current provider/API facts, create an assigned research ticket and delegate primary-source research rather than asking the human to supply facts. Leave authorized live workflow/profile/plan changes and their version mechanics with [Workflow versioning and run changes](workflow-versioning-and-run-changes.md), and durable ownership/transaction details with [Recovery guarantees and runtime selection](recovery-and-runtime-selection.md).

The first round requires policy choices, not new external capability claims. No runtime, control endpoint, native process behavior, provider integration, or recovery guarantee has been implemented or verified. The ticket remains claimed until its live decision exchange is complete.

