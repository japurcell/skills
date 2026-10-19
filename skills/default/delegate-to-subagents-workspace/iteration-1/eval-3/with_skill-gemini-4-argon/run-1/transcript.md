# Copilot CLI Session

> [!NOTE]
> - **Session ID:** `af47eddc-1acf-4839-a2d6-9b98d03d0846`  
> - **Started:** 10/19/2026, 12:56:18 PM  
> - **Duration:** 8s  
> - **Exported:** 10/19/2026, 12:56:26 PM  

---

<sub>1s</sub>

### User

This is a read-only skill evaluation. Use only the exact skill snapshot below from /Users/adam/dev/skills/skills/default/delegate-to-subagents/SKILL.md. Ignore other installed copies of delegate-to-subagents. Answer the scenario without tools, file writes, or actual delegation.

\<skill>
---
name: delegate-to-subagents
description: Use subagents when parallel execution, specialized expertise, or context isolation is likely to improve results enough to justify coordination overhead. Also use when the user explicitly asks to delegate, create, spawn, dispatch, or fan out subagents.
---

# Delegate to Subagents

Delegate when parallel work, specialized expertise, or context isolation outweighs coordination overhead.

## 1. Define assignments

For each subtask, specify an identifier, objective, necessary context, constraints, deliverable, verification criteria, allowed resources, write ownership, dependencies, and runtime limit. Resolve applicable fields before dispatch; mark others `none` or `not applicable`.

Run independent work in parallel and dependent work in waves. Serialize edits to shared files. Give each shared canonical document one integration owner or an explicit serial dependency. Workers retain scoped evidence and promptly notify the owner of durable findings, including critical guidance. Exclusive area documentation remains worker-owned. The coordinator reconciles admitted findings and completes the final documentation pass after all tasks finish.

Ask only for essential missing task facts. Avoid duplicate reads and context gathering; consider one exploration worker when several workers need the same context. The coordinator may read files to plan, coordinate, resolve conflicts, and verify results.

## 2. Route

Activate the `subagent-model-router` skill for each materially different subtask. Supply its required task facts, existing user model/effort constraints (or `none`), and exact supported values discovered from runtime metadata or the dispatch interface. The router owns capability, cost, fallback, and route-reuse rules.

This workflow authorizes selecting and explicitly applying the router's model and reasoning effort without separate model-selection confirmation. Missing preferences are not ambiguity. Do not solicit a model or effort before routing. Configured defaults apply only when the user explicitly requests them; resolve and validate concrete values through the router.

Keep the complete router decision available for dispatch and verification. A separate route file or completion ledger is not required. Persist decisions only when requested or needed for recovery or an existing audit requirement; use one session artifact outside maintained source and reuse it for revisions and results.

Dispatch requires all of the following:

- `dispatchable: true` and exact runtime-supported `model` and `reasoning_effort` values;
- task facts, capabilities, and user constraints valid for the current routing attempt;
- explicit submission of both values outside the worker prompt;
- an explicit runtime limit and a mechanism to monitor it;
- satisfied dependencies and no pending required approval.

Omitted, null, inherited, placeholder, ranged, or runtime-selected values do not qualify. If no exact route is possible, inspect accepted values, reroute with new evidence, and report any unresolved limitation without dispatching. If an explicit user constraint blocks routing, explain the limitation before asking the user to revise it.

Reuse routes only under the router's reuse criteria; still apply and check every dispatch. Reroute when work class, stakes, security sensitivity, ambiguity, affected behavior, review history, context, verification requirements, user constraints, or runtime capabilities materially change. If a configuration becomes unavailable, exclude it and let the router choose a complete replacement without lowering the capability floor.

## 3. Announce and dispatch

Announce roles and scope in one concise sentence. Show raw routing or audit data only on request; explain blockers and material failures briefly.

Route before any approval. Pause only for preexisting user-requested or runtime-required approval, then dispatch the completed route after approval. A new model/effort constraint or changed runtime capability invalidates the route; begin a fresh attempt instead of modifying values to match an approval response.

If you improperly solicited a preference before routing, invalidate routes derived from it and disclose the sequencing error. Start again with the original constraints; include the solicited value only if the user clearly makes it a new requirement.

Give workers their assignment, required dependency results, and nested-delegation policy. Prohibit nested delegation unless intentionally authorized. Tell workers they share the codebase, must preserve others' edits, and must stay within their write ownership.

Keep workflow-generated routing and audit metadata out of worker prompts: model, effort, tier, rationale, fallback, escalation trigger, and instructions to identify or report execution settings or dispatch compliance. Task-relevant source material may mention these subjects. The coordinator owns configuration and verification.

Submit the exact routed model and effort through dispatch controls. Start every ready, independent, compliant assignment before waiting.

## 4. Verify and coordinate

Inspect actual dispatch arguments and runtime-control state. Compare submitted model/effort with the route and check runtime monitoring. Distinguish selected, submitted, and executed settings: only runtime metadata confirms executed values; otherwise they remain `unconfirmed`. Worker self-reports are not runtime confirmation.

If submitted values are missing or differ from the route, mark the dispatch noncompliant and do not describe it as router-selected. Cancel it if supported and safe; otherwise disclose the mismatch before relying on results. Redispatch at most once with corrected values when safe and useful.

Documented alias resolution is not a mismatch. If runtime metadata shows a material execution override, report routing failure and pause affected dependent work.

Treat runtime limits as warning thresholds. When overdue, send a non-interrupting warning and request status, completed work, blockers, and an updated ETA. Keep the worker running; lateness alone does not justify interruption, cancellation, or replacement.

If a compliant worker fails or the runtime terminates it on timeout:

1. Retain the error, submitted settings, runtime limit, completed work, findings, unresolved items, and artifacts before replacement.
2. Diagnose instructions, context, dependencies, permissions, tools, and environment; revise the assignment or limit as needed.
3. Reroute if requirements or demonstrated capability needs changed. A timeout, missing dependency, failing test, or environment problem alone does not justify a stronger tier.
4. Dispatch at most one replacement unless the user authorizes more retries.

Before completion, verify outputs against acceptance criteria and reconcile dependencies and documentation ownership. Mark dispatches that violate routing order, reporting, dispatch arguments, prompt isolation, approval, or audit requirements noncompliant. Report material failures; correct-looking output does not establish compliance.

\</skill>

Scenario:
Describe the dispatch/reporting procedure only; do not dispatch or write files. Two independent read-only reviewers have complete exact router decisions. No recovery or audit requirement calls for persistent records. The user requested neither approval nor routing details. Explain what must exist before dispatch, whether a route file is required, what goes in chat, how submitted and executed settings are checked, and how unavailable execution metadata is described.

---

<sub>1s</sub>

### Info

load-required-skills: pass; 1 skill file

---

<sub>1s</sub>

### Info

auto-ingest-source: pass; 0 pending sources

---

<sub>4s</sub>

### Copilot

**Before dispatch**
Each reviewer needs resolved assignment fields (`identifier`, `objective`, `context`, `constraints`, `deliverable`, `verification criteria`, `allowed resources`, `write ownership: none`, `dependencies: none`, `runtime limit`). Each route needs `dispatchable: true`, current valid task facts/capabilities/constraints, exact runtime-supported `model` and `reasoning_effort` (no omitted, null, inherited, placeholder, ranged, or runtime-selected values), an explicit runtime limit with monitoring, satisfied dependencies, and no pending approval. Keep complete router decisions in memory for dispatch and verification.

**Route file**
Not required. Do not write a route file or completion ledger since no user request, recovery need, or audit requirement applies.

**Chat reporting**
Announce both reviewers' roles and scope in one concise sentence. Do not ask for model/effort approval or show raw routing/audit data unless requested; report only blockers or material failures.

**Dispatch and verification**
Start both independent reviewers in parallel before waiting. Submit exact `model` and `reasoning_effort` through dispatch controls outside worker prompts. Keep workflow routing/audit metadata and self-reporting instructions out of prompts; prohibit nested delegation and state shared-codebase/read-only rules. Verify compliance by inspecting actual dispatch arguments and runtime-control state against routed values, plus runtime limit monitoring.

**Unavailable execution metadata**
Distinguish selected, submitted, and executed settings. Only runtime metadata confirms executed values; without it, record executed settings as `unconfirmed` (never rely on worker self-reports).

---

<sub>8s</sub>

### Info

scan-secrets status: not scanned; saved scope/time unavailable. Historical only; never authorizes publication.

---

<sub>8s</sub>

### Info

validate-stop: pass; 2 checks

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
