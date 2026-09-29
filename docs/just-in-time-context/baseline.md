# Current Context Lifecycle

Read-only source inspection on 2026-09-29. These are repository facts, not verified platform guarantees.

- Root AGENTS.md directs agents to INDEX.md, architecture, conventions, and area-scoped guidance before edits. It requires an end-of-work-session update-agent-docs pass. This broader workflow relies on agent compliance.
- .agents/skills/update-agent-docs/SKILL.md refreshes semantic knowledge and permits no changes when no durable knowledge changes. .agents/skills/clean-agent-docs/SKILL.md provides a separate manual audit and cleanup workflow.
- Source auto-ingest automates source-change detection, manifest reconciliation, scaffolding, pending-work injection, and completion gates. Semantic source reading and integration remain agent work: .agents/skills/ingest-source/SKILL.md:15.
- Canonical source reconciliation is in hooks/families/auto_ingest_engine.py:371. Copilot project wiring is in .github/hooks/hooks.json:4. Gemini project wiring is in .gemini/settings.json:3.
- Codex's current project hooks contain an OKF Stop gate: .codex/hooks.json:1. Its installed global template contains required-skill startup injection: .codex/global-hooks.json:3. Source auto-ingest is not currently wired for Codex in this repository.
- Required-skill injection is distinct from source auto-ingest. Examples include .codex/hooks/load-required-skills.py:157 and .gemini/hooks/scripts/skill-context-injector.py:86.
- Gemini global configuration loads AGENTS.md and GEMINI.md and disables native autoMemory: .gemini/global-settings.json:2.
- The existing knowledge base reports Copilot first-prompt ordering differences and a Gemini AfterAgent deployed-version issue. Official research must distinguish documented support from live behavior before either becomes a guarantee.

Inspect .agents/memory/known-issues/hooks-auto-ingest.md, .agents/memory/known-issues/hooks.md, and .agents/instructions/hooks.md for existing compatibility findings and official reference pointers. Source anchors identify this checkout's baseline; future sessions must recheck changed files.
