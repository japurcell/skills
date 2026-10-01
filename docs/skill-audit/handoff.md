# Skill Authoring Audit Handoff

## Goal and Status

The destination is a completed audit of all maintained skills plus a self-contained implementation ExecPlan. The seven-ticket map contains two closed primary-source research tickets, one closed human decision ticket, and four open human decision tickets. No ticket remains claimed.

All planning artifacts are feature-scoped under `docs/skill-audit/`, as the user explicitly requested. Resume from [Skill Authoring Audit](map.md).

## Confirmed Constraints

- Review all 55 maintained entry points in `skills/` and all five in `.agents/skills/`. Exclude snapshots, generated benchmark outputs, and fixtures.
- Complete static review plus targeted safe OpenAI baselines. Define broader candidate validation in the implementation ExecPlan.
- Preserve intended behavior and approval rules. Present behavior redesigns separately.
- Cover the user's model set: 5.6, 6, and 6.1 Sol; 5.6 and 6 Luna; Astra; Terra. Exact IDs, effort values, and client availability need verification.
- The user waived `domain-modeling`. Continue with Wayfinder and Grilling.
- Keep the map, tickets, research, handoff, and final deliverables in `docs/skill-audit/`, not the scratchpad.
- Final deliverables are `docs/skill-audit/audit.md` and `docs/skill-audit/ExecPlan.md`. Skill implementation, installation, and publication follow this effort.

## Next Focus

Claim [Decide Skill Ownership and Import Handling](tickets/decide-skill-ownership-and-import-handling.md), the first open unblocked ticket in filename order. Verify that its exact blocker, `set-adoption-rules-and-protected-behavior.md`, is closed. Work the ownership/import decision with the human through Wayfinder and Grilling. Do not claim or resolve it in the session that closed the adoption ticket.

[Set Adoption Rules and Protected Behavior](tickets/set-adoption-rules-and-protected-behavior.md#resolution) holds the human-confirmed rubric, behavior contracts, exception policy, finding severities, and evidence fields. It was resolved in two rounds on 2026-10-01 and indexed in the map. [Set Audit Evidence and Model Coverage](tickets/set-audit-evidence-and-model-coverage.md) is also unblocked and may be worked by a separate session.

The resolved rubric makes [Set Audit Completion and Implementation Gates](tickets/set-audit-completion-and-implementation-gates.md) precise. This new ticket remains blocked by the adoption and batch/report decisions. The map's fog is updated; actual audit batches and finding-specific decisions still depend on later evidence.

Read the [authoring checklist](research/authoring-checklist/findings.md) and [provider comparison](research/provider-compatibility/findings.md) as needed. The latter distinguishes client contracts from model support and records unverified client execution and model aliases. Confirm the intended Terra target before selecting a concrete evaluation command.

## Verification

The seven-ticket graph passes a read-only Python check for metadata, exact dependencies, cycles, closed-ticket resolutions and map links, research findings, effort links, and fog delimiters. The frontier contains the ownership/import and evidence/model decisions. `rtk git diff --check` passes. No behavioral baseline, full skill audit, or implementation acceptance run has occurred.

The formal agent-document pass finds no new durable repository knowledge or routing changes. The existing `.agents/instructions/repo.md` location rule and `.agents/memory/FILE_MAP.md` map pointer cover the new ticket; canonical agent docs need no edits. The earlier charting pass ran `rtk proxy python3 scripts/lint-okf.py` successfully. This session changes only planning documents.

## Resolved Execution Friction

Tool Guardian rejected an oversized multi-file patch because its input exceeded the command-segment limit. Smaller patches succeeded. The protected scratchpad parent required an approved directory creation; files were subsequently moved into the user-requested docs location. Keep future patches bounded and use the docs location directly.

The resumed session's temporary commit-message replacement used delete and add operations for the same path in one patch. `apply_patch` rejected the duplicate target; a single update operation succeeded. Use one operation per path within a patch.

`rtk --version` reports 0.50.0, and the binary resolves to `/Users/adam/homebrew/bin/rtk`. `rtk gain` cannot open its tracking database in this sandbox; ordinary RTK commands work. This does not block planning.

The provider research reached its 600-second limit before writing findings. The parent interrupted it and resumed the same configured agent for a 180-second recovery limited to saving collected evidence. Findings and a closed resolution were written before the parent stopped the recovery at its next deadline check. Parent source checks corrected the Codex metadata-budget wording: 8,000 characters is the fallback for an unknown context window, not a cap compared with 2%. Preserve source conditions and units when translating numeric rules.

Both research tasks used explicitly submitted `gpt-6-luna` with `max` effort; executed runtime values remain unconfirmed. The parent verified the final artifacts against the tickets and checked key claims against Claude, OpenAI, GitHub, and Gemini primary documentation.
