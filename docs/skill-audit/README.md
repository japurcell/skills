# Skill Authoring Audit

## Destination

Complete an evidence-backed audit of non-imported maintained skills under `skills/` and `.agents/skills/`, then write a self-contained ExecPlan for accepted improvements. Final artifacts will be `docs/skill-audit/audit.md` and `docs/skill-audit/ExecPlan.md`.

The current phase charts decisions and gathers source evidence with Wayfinder. Start at [Skill Authoring Audit](map.md). Its map, tickets, research, and handoff all live in this version-controlled directory, as explicitly requested by the user.

## Original Inbox Idea

Claude released updates to skill authoring best practices in its [official documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices). Incorporate those practices into all skills in [the repository-local root](../../.agents/skills/) and [the published root](../../skills/) unless incompatible with Codex, Copilot, or Gemini. Cover the full guidance, not just the examples below. Model testing is limited to OpenAI models.

Highlighted practices from the idea are:

- [Structure longer reference files with a table of contents](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#structure-longer-reference-files-with-table-of-contents).
- [Workflows and feedback loops](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#workflows-and-feedback-loops).
- [Conditional workflows](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#conditional-workflow-pattern).
- [Concision](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#concise-is-key).
- [Appropriate degrees of freedom](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#set-appropriate-degrees-of-freedom).
- [Testing with every intended model](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#test-with-all-models-you-plan-to-use), limited here to OpenAI models.
- [Effective descriptions](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#writing-effective-descriptions).
- [Progressive disclosure](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#progressive-disclosure-patterns).

## Confirmed Effort Constraints

The user selected static review plus targeted safe OpenAI baselines, followed by an implementation ExecPlan. On 2026-10-01 the user narrowed this effort to exclude imported skills, superseding the original all-skills breadth. Current import mappings exclude 23 entry points from the 60-entry inventory, leaving 37 audit candidates across both roots. Imported-derivative maintenance and a lasting provenance ledger are outside this effort.

Planned authoring improvements preserve intended behavior and approval rules; behavior redesigns are presented separately. The source idea above remains historical context; use the map and resolved tickets for current scope.

The [evidence decision](tickets/set-audit-evidence-and-model-coverage.md#resolution) defines the exact native Codex CLI matrix: GPT-5.6, GPT-6, and GPT-6.1 Sol; GPT-5.6 and GPT-6 Luna; GPT-6 Astra; and GPT-5.6 Terra, all at explicit `medium` effort. The CLI catalog advertises these configurations; account execution remains untested. The unavailable `domain-modeling` dependency is explicitly waived.

Policy detail and its evidence live in the tickets until incorporated into the final audit and ExecPlan. Implementation, installation, and publication of improvements follow this planning effort.
