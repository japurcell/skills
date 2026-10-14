# Actionable report for the personal skill maintainer

Prepared 2026-10-14 from the independent Astra, Sol, and Luna retrospectives of FSDP audit remediation at `25a63db4`. **Proposal only: no personal skill or global configuration was changed.** The user requested this report and a stop before implementation. This document has not been sent to another person or task.

The [repository ExecPlan](ExecPlan.md) owns FSDP verification, guidance routes, diagnostic CI, worktree readiness, and environment-owner coordination. This report owns reusable changes to `/Users/adam/.agents/skills` and clearly labeled referrals to other maintainers. The same recommendation is not a request to implement two independent systems.

## Evidence and boundaries

The completed session used private worktrees and serial integration successfully, but FILE_MAP and Web Components known-issue edits conflicted. Some retrieval batches exceeded their outer output envelope. Two historical route summaries incorrectly declared `fallback: none` despite eligible alternatives; submitted configurations still matched selected configurations. Review caught a proposed lifetime-cached query that changed per-connection template behavior. These are concrete improvement candidates, not proof that delegation, caching, or documentation duties should be removed.

Stable repository evidence: `docs/audit-remediation/Delegation.md`, `evidence/Q2.md`, `evidence/L2.md`, `evidence/R1.md`, and `evidence/I3.md`. Original retrospective artifacts were `/private/tmp/fsdp-retro-astra.md`, `/private/tmp/fsdp-retro-sol.md`, and `/private/tmp/fsdp-retro-luna.md`. Their necessary findings are repeated here so temporary-file removal does not block this report.

For primary-event investigation only, the retained transcript is `/Users/adam/.codex/sessions/2026/10/14/rollout-2026-10-14T07-14-40-01a13ac3-eae6-7ab2-8ba9-b85d161b9fb9.jsonl`. Physical JSONL lines 563 and 1734 contain shared-doc integration conflicts; lines 18/28, 32/42, and 59/70 pair large read batches with oversized results. Those line numbers refer to the retained session snapshot, not a portable API. Search exact event content if the transcript is reserialized. Do not copy unrelated session material or credentials into evaluations.

The personal directories were inspected for current entry points. Relevant packages have SKILL.md files and references, but no existing scripts/evaluation files were listed in those packages. New paths below are proposals, not claims that helpers already exist. Follow the skill repository's current authoring/evaluation conventions when implementing; use `skill-creator` rather than inventing a second evaluation framework.

## SM1 - Reserve shared canonical-document ownership before dispatch

Priority: medium. Sources: Astra R4, Sol recommendation 3, and the repository portion of Luna N1. Owner: delegation/implementation-workflow maintainer. Dependencies: none. Status: proposed.

Targets:

- `/Users/adam/.agents/skills/delegate-to-subagents/SKILL.md`, Plan and coordination steps.
- `/Users/adam/.agents/skills/execplan-implement/SKILL.md`, task assignment and serialized integration.

Both skills already require ownership and serialized shared state. The observed gap is that source-file partitioning did not identify shared maps and known-issue files as competing ownership. Extend the existing ownership check with shared canonical documentation, not another orchestration layer. At dispatch, each multiply touched canonical file must have one integration owner or an explicit serialized dependency. Workers retain scoped evidence and immediately notify that owner of new durable claims. Exclusively owned area documents can stay with their worker. The coordinator integrates admitted claims and performs the final session doc pass.

Keep one canonical statement in delegate-to-subagents and a short context-triggered reference from execplan-implement. Preserve fresh task owners, private worktrees, clean serial integration, immediate evidence recording, and final documentation duties. Do not impose FSDP filenames on other repositories or make all documentation coordinator-only.

Acceptance/evaluation: supply two independent component tasks that both affect one known-issues file and one file map. Before dispatch the workflow must name one owner or serialize those edits. Both workers' verified findings must survive final reconciliation. A control with disjoint docs must remain parallel. A critical guidance discovery must be recorded promptly, not deferred until the session ends. The current failure fixture is competing canonical rewrites despite disjoint source ownership.

Repository boundary: D2 in the ExecPlan handles FSDP's existing AGENTS/knowledge-base wording. Do not edit the repo-local `update-agent-docs` skill from this personal-skill task; it already says the final pass follows completion of session tasks.

## SM2 - Bound combined tool results while preserving full evidence

Priority: medium. Sources: Astra R6 and Sol recommendation 5. Owner: exploration/delegation workflow maintainer, with harness support only if needed. Dependencies: none. Status: proposed.

Targets:

- `/Users/adam/.agents/skills/explore/SKILL.md`, retrieval and synthesis steps.
- Proposed `/Users/adam/.agents/skills/explore/references/bounded-results.md`, shared retrieval guidance.
- `/Users/adam/.agents/skills/delegate-to-subagents/SKILL.md`, a conditional pointer for coordinating large result batches.

The current explore skill already asks for concise maps and reuse of relevant context. Add a specific completion check for a batch: total emitted content must fit the outer response envelope, every child result must be accounted for, and full evidence must remain recoverable. Per-command limits do not bound their sum. Keep independent execution parallel; summarize status and focused excerpts, retain full logs locally, and inspect omitted failure detail before drawing conclusions. Read mandatory skill/instruction content completely through bounded sections. Separate semantic source/manifests from cache-archive counts instead of dumping hundreds of archive filenames.

Use the runtime's actual output limits rather than a universal token budget. Do not truncate away a failed command, security finding, required instruction, or unknown status. Do not introduce a new FSDP wrapper or require a generic log service. Existing handoff guidance already says to preserve concise evidence and avoid whole-chat replay; link it only where useful rather than duplicating it.

Acceptance/evaluation: replay a multi-document startup batch and a dependency-diff fixture with large cache churn. Require zero unaccounted child results, no outer-envelope loss, accessible full text, and complete required-instruction reads. Compare emitted bytes and redundant retrievals before/after. Include a small hidden failing result among large successes and verify it remains visible. A narrow three-file task must not incur a new framework or extra delegation.

## SM3 - Validate routing records without inventing runtime identity

Priority: low. Source: Sol recommendation 5 and the retained L1/L2 metadata defect. Owner: delegation/router maintainer. Dependencies: none; reuse SM2's bounded reporting only if implemented. Status: proposed.

Targets:

- `/Users/adam/.agents/skills/delegate-to-subagents/SKILL.md`, dispatch gate and audit.
- `/Users/adam/.agents/skills/subagent-model-router/SKILL.md`, fallback eligibility semantics only if clarification is necessary.
- Proposed small `/Users/adam/.agents/skills/delegate-to-subagents/scripts/validate_dispatch.py` and focused tests, or an equivalent existing host validation seam discovered by the maintainer.

The instructions already require exact routes, matching submitted values, runtime-warning thresholds, and honest executed metadata. Avoid adding another prose checklist. Validate the finite record mechanically: exact selected/submitted model and effort; explicit threshold/mechanism; pending-approval state; fallback eligibility based on supplied runtime candidates and user constraints; and independent evidence before claiming executed identity. A `none` fallback is valid when constraints or availability leave no eligible same-tier alternative. Never hardcode today's model catalog into the validator or treat a cheaper below-floor model as eligible.

The helper should accept an explicit JSON record and return nonzero with a focused reason on an inconsistent record. It validates provided facts; it cannot prove runtime facts that the host never reports. Keep implementation small and dependency-light. If the host already exposes a route-validation hook, use that seam instead of building a second tool.

Acceptance/evaluation: reject the historical missing-fallback fixture when an eligible candidate is supplied; accept a single-family constraint with no alternative; reject route/submission mismatch, unresolved effort, or an omitted runtime-warning mechanism; preserve `executed: unconfirmed` when no host evidence exists. Reject inferred execution identity even if an agent self-identifies. A delayed agent must receive a non-interrupting warning, not cancellation solely for elapsed time. Use simulated dispatches; do not spawn billable agents for each mechanical schema case.

## SM4 - Evaluate lifecycle equivalence review before adding more prose

Priority: low. Source: Sol recommendation 4, qualified by Astra's finding that review already caught the defect. Owner: code-review skill maintainer. Dependencies: none. Status: evaluation proposed; wording change conditional.

Target: `/Users/adam/.agents/skills/addy-code-review-and-quality/SKILL.md`, Correctness and Step 5, plus package-scoped evaluation cases created using the skill repository's conventions.

The current skill already asks about edge cases, state consistency, and whether tests test the right behavior. First add retained evaluation cases rather than a new global rule. Case one replaces a per-connection DOM lookup with lifetime query caching: disconnected template replacement must still be observed after reconnect. Case two replaces a real timer-expiry assertion with a manually dispatched completion event: the test proves listener handling but no longer proves expiry. Include correct cached-query and manual-event controls so the reviewer does not ban valid techniques.

If existing guidance consistently distinguishes these cases, record that result and make no wording change. If it fails, add one scoped prompt to compare old/new resource or value lifetime when a refactor introduces caching, decorators, listeners, or timers. Place it in the existing review step. Keep mechanical imported-asset misuse in the repository's ESLint task V3. Do not create CODING_STANDARDS.md or add redundant always-loaded FSDP instructions.

Acceptance: reviewers identify the semantic regression and weakened behavioral proof in the failing cases, accept the valid controls, and request the smallest real browser/timer evidence. Record before/after results and remaining variance. Successful evaluation without a prose edit is a completed outcome.

## Adjacent-owner referrals, not personal-skill changes

### G1 - Disclose global RTK recipes without weakening policy

Priority: low. Source: Astra R7. Owner: the user/global instruction maintainer. Confirmed file: `/Users/adam/.codex/AGENTS.md`, RTK section. This is outside `/Users/adam/.agents/skills`.

Keep the mandatory RTK policy, installation verification, mutation exceptions, secret protection, and user preferences inline. Move only the long command reference to a clearly triggered existing reference or help path. Preserve a one-place obligation map and compare before/after decisions in startup, mutation, testing, and commit scenarios. No policy is a no-op merely because a model often follows it. Do not edit the global file as part of FSDP execution. D2 separately deduplicates repository instructions.

### H1 - Capture guardian false positives as negative test fixtures

Priority: low, pending primary-command evidence. Source: Sol's supplementary observation from the retrospective itself, not the earlier coding session. Owner: Tool Guardian/harness maintainer; the implementing file is not known from available evidence.

Sol reported read-only Python JSON-summary commands rejected as `database_destruction/critical [truncate_table]`. The exact classifier cause is unconfirmed, and the rejected command text is not retained in the report. Recover the exact command, rejection, and tool context from that review's own log before proposing a classifier change. Redact unrelated session data. If the command is truly read-only, add it as a negative classification fixture paired with a real destructive SQL positive fixture. Preserve the latter rejection. Do not whitelist Python, disable review, or use alternate execution to bypass a denied destructive action. A long prose-writing command also exceeded a configured segment limit; using the patch/file tool is sufficient and does not require raising that limit.

### E2/C2 - Permissions and remote visibility

The environment administrator owns scoped authorized doc writes and Docker capacity; the repository administrator owns remote workflow execution and required checks. These are already actionable nodes E2/C2 in the ExecPlan. They require no personal-skill permission bypass, broad credential grant, or duplicate implementation here.

## Maintainer execution and completion

This report authorizes no work by itself. When commissioned, use the current skill-authoring workflow, preserve existing explicit user constraints, and inspect package changes since this snapshot before editing. Each SM item is independently assignable. Serialize shared edits to delegate-to-subagents; prefer one canonical rule and a reference over copies. Preserve original fixtures so improvements can be compared.

For each item return: disposition (implemented, deferred, rejected, or evaluation passed without an edit), exact files changed, evaluation evidence, compatibility/behavior changes, and unresolved limits. A prose change without evidence is not completion. Send no external message or make global permission changes without the relevant user's authorization.

The FSDP coordinator records these dispositions under S1 in the ExecPlan. Local FSDP work does not need to wait for skill changes, and local test passes do not establish that these proposals were adopted.
