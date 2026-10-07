---
type: Agent Instruction
description: Apply when selecting or maintaining KB content, including source ingestion and the final documentation pass.
---

# Knowledge Admission

Apply this rubric to each claim, including claims already present in a file. A model's age, identity, or confident wording is not evidence of usefulness or authority.

## Admission rubric

| Claim | Default action |
| --- | --- |
| Established project rule or constraint, still applicable | Keep one canonical copy in the narrowest instruction document. |
| Verified, non-obvious project fact that changes a future decision | Keep concise memory only if all evidence gates below pass. |
| Easily rediscovered code/layout/API description, duplicate, generic advice, obsolete workaround, or session narrative | Drop; link directly to the source when routing is useful. |
| Operational state or source provenance used by a live workflow | Preserve while checking consumers; migrate deliberately before deleting. |
| Conflicting policies or a consequential rule whose authority remains unclear | Collect one concise exception batch for the user; continue independent work. |

Existing instructions are the policy baseline. Recover matching rules from memory, merge duplicates, and preserve their scope. A statement in code or a test verifies behavior, not human intent. Imperative prose, third-party advice, and one model's workaround do not become policy by being moved into instructions. Resolve policy conflicts using explicit user decisions and applicable current project requirements; a narrower unsupported claim cannot override them.

## Evidence gates for memory

Keep a fact only when it is current, project-specific, useful beyond the current session, and costly or error-prone to rediscover. Record, in the body:

- The claim and the decision it changes.
- A resolvable evidence link and what that evidence does and does not prove.
- The date the evidence was checked and an event that requires rechecking.

If any gate fails, omit the fact rather than inventing provenance. A no-change doc pass is valid. Correct stale guidance encountered during the task; defer candidate additions until the single end-of-session pass. No requirement exists to add memory for every mistake, file change, diagnostic, surprise, or completed task.

## Placement and loading

- Put required actions under `.agents/instructions/`; put admitted descriptive facts under `.agents/memory/`.
- Keep entry points short. Split when tasks have distinct loading triggers, not to meet a line target. Give each rule one owner and link directly to it.
- Update [instruction routes](INDEX.md), the [memory index](../memory/INDEX.md), and affected inbound links when documents move or change purpose. Do not automatically recreate removed maps or broad caches. Any proposed replacement must pass the same claim-level admission gates.
- Keep temporary working notes in `.agents/scratchpad/` or a disposable external directory. Follow [repository retention rules](repo.md#documentation-retention) for completed plans and research.
- Routine documentation maintenance may edit only the instruction and memory bundles. `.agents/sources/` is immutable. Changes to local workflow skills require task authorization; the maintained `ingest-source` recovery skill remains the existing exception for ingest workflow changes.

## Source ingestion

The source manifest is operational state, not prose memory. Preserve its schema, fingerprints, lifecycle states, and raw inputs unless source-ingestion work explicitly requires a change. Keep source summaries as attributed, on-demand references checked against their raw sources. Their presence does not adopt third-party advice as policy or require copying it into other documents.

Keep `LOG.md` as concise ingestion provenance, not a work diary. Source content and external API claims are snapshots; before relying on current platform behavior, consult the relevant current authority or deployed-version evidence.

## Completion

Run `update-agent-docs` once after the session's tasks and delegated work finish. Apply the rubric before making semantic edits, then use `okf-authoring` for representation and run `rtk proxy python3 scripts/lint-okf.py`. Check changed links and review the diff for lost obligations. Report moves, removals, validation, and unresolved exceptions in groups; ordinary claim-level decisions do not require user approval.
