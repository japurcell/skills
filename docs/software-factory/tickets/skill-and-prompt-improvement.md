# Skill and prompt improvement

**Type:** grilling
**Status:** closed
**Blocked By:** agent-execution-profiles.md, verification-and-review-policy.md, session-events-and-live-progress.md, workflow-versioning-and-run-changes.md
**Research Dir:** not applicable

## Question

How do session and trace logs produce useful skill or prompt improvements, and who decides to apply them?

Decide extraction inputs from successful and failed runs, scope and ownership of proposals, evidence and counterexamples, evaluation cases, acceptance criteria, human versus automatic promotion, versioning, rollback, and visibility in the factory UI.

Apply [SSSF-style continuation](workflow-versioning-and-run-changes.md#resolution): promoted settings/prompt/skill inputs are consumed under [step-start input resolution](workflow-versioning-and-run-changes.md#step-start-input-resolution), potentially by later steps in the same invocation. The accepted evaluation and adoption section below now settles promotion authority and evaluation requirements. Do not design migration of suspended workflows or retain executable environments for old runs. Improvement revision/rollback history is ordinary authoring history, separate from workflow resume.

Distinguish extracting a proposal from changing an installed skill or prompt. Define how evaluation avoids treating lower token use or a single passing run as sufficient proof of improvement.

Resolution should describe one complete proposal/evaluation/promotion example and the allowed automation level. Do not edit skills or prompts while resolving this planning question.

---

## Accepted history and traceability constraints

Claimed by `subagent-root` on 2026-10-15 after verifying all four exact prerequisites were closed. Apply [accepted history preservation for learning](recovery-and-runtime-selection.md#accepted-history-preservation-for-learning): keep full captured source history by default, record examined source invocations/attempts and extracted proposals, link evaluation/adoption evidence when available, and never treat extraction as permission to discard the sources. This records the user's accepted history constraint; the subsequent evaluation and adoption section settles promotion authority.

## Accepted explicit learning invocations

On 2026-10-15 the human accepted explicit learning invocations that produce evidence-linked proposals without automatically changing active configuration. This section owns the extraction entry-point contract; the subsequent accepted evaluation and adoption section owns those separate actions. No implementation is authorized.

Use an explicitly invoked learning workflow over user-selected ended invocations, using the existing foreground runner and non-interactive harness model. A run may contain further invocations later, so identify the exact invocation/attempt sources examined rather than labeling an entire evolving run permanently reviewed. Ended sources can include success, failure, interruption, and needs-input; missing/partial capture is disclosed and never treated as complete evidence. The existing storage/permission and exclusive worktree rules still apply to the new learning invocation. No special background learner, scheduler, or mandatory post-run extraction hook is proposed.

The invocation produces evidence-linked candidate improvements: the observed problem or successful pattern, the proposed change and its target, supporting and contrary examples when present, and suggested evaluation cases. Record examined sources even when no proposal is justified. It does not automatically edit or install active prompts, skills, harness profiles, or factory code. Reports and extraction records are outputs of the learning invocation, not instructions that silently change later steps. Evaluation and promotion remain separate actions under the accepted contract below; a candidate is not an adopted improvement.

Example: the user selects three ended invocations containing repeated test-discovery failures. A learning invocation compares their prompts and tool results, references the relevant attempts, and proposes a clearer test-discovery instruction with evaluation cases. A successful contrasting run can challenge the proposal. The original history remains intact. No new prompt becomes active from this extraction alone.

Automatic extraction after every invocation or on a schedule was not selected. It could find lessons sooner, but adds automatic agent calls, trigger/duplicate handling, and unsolicited proposals. The accepted explicit model uses the existing runner without an always-running feedback loop.

Acceptance must cover explicit source selection, source-linked candidate reports and evaluation suggestions, recorded examined sources even when no proposal is justified, disclosed partial/missing evidence, preserved source history, and no automatic edits or installation of active configuration. Learning invocations retain the existing managed execution, permissions, accounting, and worktree contracts. No learning workflow has been implemented or tested.

## Accepted evaluation and human adoption

On 2026-10-15 the human accepted both recommendations: explicit evaluation using existing workflows and human approval before adoption. The following contract governs evaluation and adoption without authorizing implementation or changes to any actual skill, prompt, profile, or runtime during this planning session.

1. **Explicit, bounded comparison using existing workflow machinery.** A separately requested evaluation prepares an exact candidate revision in the factory-owned isolated worktree, without modifying active prompts, skills, harness profiles, or installed runtime files. Compare the current baseline and candidate on the same relevant cases with explicit success criteria. Include the motivating failure, representative successful behavior that should remain intact, and independent or counterexamples where available. Use appropriate objective checks plus recorded review judgments; label unavailable tests, changed model/environment conditions, and inconclusive evidence honestly. Repeat nondeterministic cases where needed to distinguish a plausible improvement from a lucky result; do not impose a universal trial count or accept lower token use or one passing run as sufficient proof. Record the actual supplied baseline/candidate inputs, source proposal, case inputs, settings, results, tradeoffs, and limitations. Use existing managed attempts, limits, traces, and checks rather than building a separate experiment platform or automatic optimization loop. Historical traces inform cases; evaluation launches new work and does not replay or resume an old invocation.
2. **Explicit human adoption through ordinary authoring/install paths.** Evaluation produces a report and reviewable candidate diff, but does not activate it. A human explicitly selects and approves the exact change and target scope before adoption. A changed candidate or target requires a fresh review of the change and relevant evaluation; passing evidence for a different revision is not automatically transferable. Keep revision and revert history in ordinary version control, with proposal/evaluation/adoption references in factory history. No mandatory PR publication, live approval callback, dedicated promotion service, or saved executable environment is required. Reverting is an explicit authoring action, not an automatic rollback service. Repository-local changes stay local; broader/shared harness or skill changes need their own explicit target and authorization. Editable inputs follow the accepted step-start resolution rule after adoption; already-started calls do not change, and later steps may see the edit. Managed runtime/code installation changes still follow idle-only upgrades, so adopting a prompt is not permission to bypass installation rules. This human choice concerns changing future behavior, not adding routine human gates to ordinary application workflows.

Example: extraction proposes a clearer test-discovery instruction. An explicitly launched evaluation compares the old and candidate instruction on the original failure and normal cases. If results are mixed, the report remains inconclusive and nothing changes automatically. If evidence supports the change, a human can accept the exact repository-local diff, recording its revision and evaluation link. The full source and evaluation history remain available, and an ordinary explicit revert can restore the prior text later.

Informal adoption without comparative evaluation and automatic promotion after passing configured checks were not selected. The accepted approach uses evidence plus one explicit adoption decision, reusing existing execution and version-control tools. No generic benchmark registry or promotion infrastructure is selected.

## Resolution

Closed on 2026-10-15 following the human's acceptance of explicit extraction, explicit comparative evaluation, and human approval before adoption. The accepted sections above own the policy. This completes the learning-policy decision; it does not claim an implemented or fully validated factory.

The minimum semantic record consists of the examined invocation/attempt references and capture limitations; the candidate proposal and target scope; exact baseline/candidate input identities; evaluation cases, success criteria, settings, results, and limitations; and, if adopted, the human decision, actual applied revision, and target. Reference source/evaluation history rather than duplicating whole transcripts. Keep extraction with no justified proposal, inconclusive evaluation, rejection, adoption, and later revert distinguishable; these are recorded facts, not a durable execution state machine. Do not report adoption merely because approval exists: the applied change must be identified, and a failed or uncertain apply must be shown honestly. A later explicit action rechecks current files and the approved change; there is no automatic apply retry or workflow replay.

UI inspection links sources, proposals, evaluation reports, and adoption/revert records without adding browser execution/approval controls. [Detailed observability UI design](detailed-observability-ui-design.md) owns visual treatment. [Invocation lifecycle and interrupted work](recovery-and-runtime-selection.md) owns record persistence and execution mechanics; [Specification readiness and acceptance](specification-readiness-and-acceptance.md) must verify concrete record/command shapes and target/revision checks against this contract before declaring implementation readiness. Exact names and serialization are specification details, not additional product authority.

Acceptance must cover explicit source selection and no-proposal findings; unchanged active configuration during extraction/evaluation; baseline/candidate evidence and honest inconclusive results; no automatic promotion; exact-change and target approval; refusal to silently apply to a changed target; actual adoption/revert provenance; separate authorization for shared scope; retained source/evaluation history; step-start visibility of adopted editable inputs; idle-only managed installation changes; and unchanged ordinary workflow automation. No learning workflow, evaluation, adoption, or rollback was executed during planning.
