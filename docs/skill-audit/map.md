# Skill Authoring Audit

## Destination

Complete an evidence-backed audit of non-imported maintained skills in `skills/` and `.agents/skills/`, then author `docs/skill-audit/ExecPlan.md` to implement the accepted improvements. The final audit lives at `docs/skill-audit/audit.md`.

## Notes

- [Visual design overview](design-map.html) is a dated interactive view for discussion. The owning ticket resolutions remain authoritative; draft annotations do not change decisions or record approval.
- [Coverage](coverage.md), [the first batch report](reports/review-skill-authoring-and-repository-guidance.md), [the repository-local report](reports/review-repository-local-workflows.md), and [the single findings register](findings.md) hold live evidence and proposal status. Static investigation covers eleven skills; the first six have completed human review. The five repository-local skills await two live review answers. Five separate intended-behavior questions remain pending; the newest route is blocked by the current review.
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
- Follow the [repository subagent checkpoint rule](../../.agents/instructions/repo.md#subagent-checkpoints). Use status checks for missed checkpoints and keep runtime limits explicit.
- The batch decision grants `dotnet-upgrade` a narrow static paper-reading exception for this audit. Preserve all invocation, migration approval, execution, installation, packaging, validator, and live-evaluation restrictions; follow that ticket's exact scope.

## Decisions so far

<!-- Closed decision and research tickets are indexed here by title and a one-line gist. -->

- [Extract the Complete Authoring Checklist](tickets/extract-complete-authoring-checklist.md): The full source guidance is captured with conditional checks and distinctions between Claude requirements and authoring advice.
- [Establish Provider Compatibility Constraints](tickets/establish-provider-compatibility-constraints.md): Shared metadata does not imply shared invocation, permission, or loading behavior; model and client verification gaps are recorded.
- [Set Adoption Rules and Protected Behavior](tickets/set-adoption-rules-and-protected-behavior.md): Apply contextual dispositions, preserve intended contracts, document exceptions, and rank findings by consequence with explicit evidence.
- [Decide Skill Ownership and Import Handling](tickets/decide-skill-ownership-and-import-handling.md): Exclude 23 configured imports; review 37 remaining candidates across both roots with scoped dependency checks and no provenance-ledger work.
- [Set Audit Evidence and Model Coverage](tickets/set-audit-evidence-and-model-coverage.md): Use native Codex CLI, seven models at medium effort, three fresh runs per case, a small safe sample, and explicit trace-backed evidence gaps.
- [Choose Audit Batches and Evidence Format](tickets/choose-audit-batches-and-evidence-format.md): Review twelve bounded scopes with per-check coverage, one findings register, human review, shared-resource ownership, and static review before sample selection.
- [Set Audit Completion and Implementation Gates](tickets/set-audit-completion-and-implementation-gates.md): Separate audit completion, executable plan readiness, and implementation acceptance, with explicit deferrals and a visible route for every pending proposal.
- [Review Skill Authoring and Repository Guidance](tickets/review-skill-authoring-and-repository-guidance.md): Accept contract-preserving authoring and evaluation repairs for later planning; keep four separate decisions pending and visible.

## Not yet specified

<!-- FOG START -->
The selected skills and exact cases will determine concrete native baseline setup and run scopes, including discovery isolation, required dependencies, safe tools, grader compatibility, and the actual shipped file set. Those prerequisites remain unverified; selected-case work must resolve them or surface required evidence gaps. No baseline sample or launch recipe is selected yet.

Additional findings may expose behavior conflicts, missing safe fixtures, scope changes, or improvements to authoring and validation tools. Four precise first-batch questions and one repository-local prior-plan question already have decision tickets linked from the findings register; they are no longer fog. Create further decisions only when evidence makes a precise investigation or human choice possible. Existing batch and reconciliation tickets already own static coverage, shared-resource checks, and proposal accounting.

Actual accepted findings and baseline evidence will determine specific implementation targets, milestone order, matched candidate cases, provider checks, recovery steps, and final document authoring scopes. Remaining finding-specific behavior, missing-evidence, and acceptance questions become tickets when precise; the known policy for retaining pending proposals lives in the completion-gates decision.
<!-- FOG END -->

## Out of scope

- Auditing or improving imported skill bundles, maintaining their local derivatives, recovering their historical provenance, or building a lasting provenance ledger.
- Implementing, installing, or publishing the proposed skill improvements during this map.
- Expanding behavioral model tests beyond OpenAI models. Compatibility analysis still covers Codex, Copilot, and Gemini.
- Treating benchmark outputs, historical snapshots, or fixture skills as maintained entry points.
- Automatically redesigning unrelated provider hooks or knowledge management. Concrete findings may propose a separately scoped effort.
