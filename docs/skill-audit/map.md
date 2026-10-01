# Skill Authoring Audit

## Destination

Complete an evidence-backed audit of non-imported maintained skills in `skills/` and `.agents/skills/`, then author `docs/skill-audit/ExecPlan.md` to implement the accepted improvements. The final audit lives at `docs/skill-audit/audit.md`.

## Notes

- This effort starts from the SKILL audit idea preserved in [the effort brief](README.md).
- Apply Wayfinder and Grilling. The user explicitly waived the unavailable `domain-modeling` dependency on 2026-10-01.
- The user chose a completed audit plus an ExecPlan as the destination. Audit evidence gathering and final document authoring are allowed within this map. Implementing proposed skill changes is a later effort.
- Consider the complete Claude authoring guidance, including recommendations beyond the original examples. Apply it unless incompatible with Codex, Copilot, or Gemini; document adaptations and exclusions with evidence.
- The completed audit includes static review of every in-scope skill plus targeted OpenAI behavioral baselines where safe fixtures and existing evals support them. The ExecPlan defines broader validation.
- Planned authoring improvements preserve intended behavior and approval rules. Present behavior redesigns separately for human decision.
- The human-confirmed native Codex CLI matrix uses GPT-5.6, GPT-6, and GPT-6.1 Sol; GPT-5.6 and GPT-6 Luna; GPT-6 Astra; and GPT-5.6 Terra, all at explicit `medium` effort. Exact IDs and runtime evidence obligations live in the evidence ticket. The CLI catalog advertises the matrix; successful execution and account access remain untested. Do not silently substitute an unavailable model.
- The initial inventory contains 55 maintained entry points under `skills/` and five under `.agents/skills/`. Exclude benchmark snapshots, generated outputs, and fixture skills. [Inventory evidence](local-inventory.md) records the baseline and exceptions.
- On 2026-10-01 the user excluded imported skills from this effort. Current importer mappings identify 23 excluded entry points, leaving 32 published and five repository-local audit candidates. Remove any additional imports established by clear evidence. Check shared resources only as dependencies of included skills. Do not carry imported-derivative maintenance, historical provenance recovery, or a lasting provenance ledger into this effort.
- Research tickets use Research and Official Sources. For Codex-specific facts, use OpenAI Docs and current official OpenAI documentation. Grilling tickets require live human decisions; do not answer the human's side.
- Load Create Skill and Skill Creator when deciding authoring and evaluation changes. Load ExecPlans before authoring the implementation plan. Preserve invocation controls, approval rules, and the document-only constraints of `dotnet-upgrade` when assessing evidence.
- Keep the map, tickets, research, handoff, final audit, and self-contained ExecPlan under `docs/skill-audit/`. The user explicitly chose this version-controlled location instead of Wayfinder's scratchpad default.
- Charting resolves no human decision tickets. Research tickets may close during charting. Later sessions claim and resolve at most one non-research ticket, verify every exact blocking filename, and advance the map.

## Decisions so far

<!-- Closed decision and research tickets are indexed here by title and a one-line gist. -->

- [Extract the Complete Authoring Checklist](tickets/extract-complete-authoring-checklist.md): The full source guidance is captured with conditional checks and distinctions between Claude requirements and authoring advice.
- [Establish Provider Compatibility Constraints](tickets/establish-provider-compatibility-constraints.md): Shared metadata does not imply shared invocation, permission, or loading behavior; model and client verification gaps are recorded.
- [Set Adoption Rules and Protected Behavior](tickets/set-adoption-rules-and-protected-behavior.md): Apply contextual dispositions, preserve intended contracts, document exceptions, and rank findings by consequence with explicit evidence.
- [Decide Skill Ownership and Import Handling](tickets/decide-skill-ownership-and-import-handling.md): Exclude 23 configured imports; review 37 remaining candidates across both roots with scoped dependency checks and no provenance-ledger work.
- [Set Audit Evidence and Model Coverage](tickets/set-audit-evidence-and-model-coverage.md): Use native Codex CLI, seven models at medium effort, three fresh runs per case, a small safe sample, and explicit trace-backed evidence gaps.

## Not yet specified

<!-- FOG START -->
Specific review and baseline investigations will become tickets after the batch/report decision and content review identify their exact targets. Actual skill risk, fixture readiness, and additional clear import evidence may change those targets. Native discovery isolation, complete run setup, and existing grader suitability remain unverified; later bounded baseline work must resolve the selected prerequisites or surface them as required evidence gaps.

The findings may expose interactions between skills, shared reference changes, missing safe evaluation fixtures, or improvements to authoring and validation tools. Expand the map only when an investigation can be bounded around an actual finding.

The accepted improvements will determine implementation order, baseline and candidate comparisons, provider checks, rollback strategy, and the precise milestones of the final ExecPlan. Finding-specific behavior decisions, missing-evidence work, and additional acceptance decisions will become tickets when actual audit findings make them precise.
<!-- FOG END -->

## Out of scope

- Auditing or improving imported skill bundles, maintaining their local derivatives, recovering their historical provenance, or building a lasting provenance ledger.
- Implementing, installing, or publishing the proposed skill improvements during this map.
- Expanding behavioral model tests beyond OpenAI models. Compatibility analysis still covers Codex, Copilot, and Gemini.
- Treating benchmark outputs, historical snapshots, or fixture skills as maintained entry points.
- Automatically redesigning unrelated provider hooks or knowledge management. Concrete findings may propose a separately scoped effort.
