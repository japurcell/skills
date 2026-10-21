# Completed todos

## Forest Service skills

10. [x] Create `skills/forest-service/accomplishment-report` for completed ExecPlans, with sibling reports, agency alignment, and evidence-based AI-assisted versus human-only time and cost estimates - completed 2026-10-21. Added completion checks, oversight and AI spend accounting, uncertainty and negative-savings handling; validated bundle metadata and three synthetic reporting scenarios. [Skill](../../skills/forest-service/accomplishment-report/SKILL.md)

## Repository maintenance

1. [x] Replace the legacy agent knowledge system with brain notes and portable maintenance hooks - completed 2026-10-21 after native CI and live Copilot/Codex verification; Gemini CLI verification waived by user. [Execution plan](plans/01-brain-migration/ExecPlan.md)
9. [x] Convert Obsidian-style note links to standard relative Markdown links - completed 2026-10-21; converted notes, generated indexes and authoring guidance, with process/generator and CommonMark validation. [Execution plan](plans/09-markdown-links/ExecPlan.md)

## Investigations

5. [x] Investigate whether nested AGENTS.md maps complement the root brain index for local context; evaluate [harness-engineering](https://github.com/lopopolo/harness-engineering) - superseded by #12 `agents-md-install` skill.

## Skills

1. [x] Create `skills/default/agents-md-install` to install or update root and nested `AGENTS.md` files plus progressive-disclosure reference docs in a target project (excluding tool-specific compatibility bridges like `CLAUDE.md` or `.github/copilot-instructions.md`). While authoring the skill, research these sources in priority order and use `grilling` to resolve conflicting guidance before baking the rules into the skill: (1) [harness-engineering](https://github.com/lopopolo/harness-engineering), (2) [A Complete Guide to AGENTS.md](https://www.aihero.dev/a-complete-guide-to-agents-md), (3) `~/.agents/skill/agents-md-improver/SKILL.md`, (4) [agents.md](https://agents.md/), (5) [Addy Osmani - AGENTS.md](https://addyosmani.com/agents/15-agents-md/), (6) [GitHub Blog - How to write a great agents.md](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/), and (7) [AAIF - Writing an effective AGENTS.md](https://aaif.io/blog/writing-an-effective-agents-md). Require nested `AGENTS.md` files when appropriate for per-scope progressive disclosure, and progressive disclosure for conditional content so agents read only what a task requires. This skill will replace both `skills/default/agents-md-improver` and `skills/default/create-agentsmd` skills. - Completed 2026-10-21; replaced both predecessor bundles, verified scoped creation/update/audit fixtures, and retained explicit invocation. [Execution plan](plans/01-agents-md-install/ExecPlan.md)
