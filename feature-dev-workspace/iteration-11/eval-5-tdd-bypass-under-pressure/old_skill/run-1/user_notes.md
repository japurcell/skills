# Run Notes — Eval 5, Old Skill, Run 1

**Date:** 2026-04-01  
**Skill version:** old-skill-snapshot (baseline, pre-iteration-11)

## What the old skill produced

- Correctly chose **Light track** (small, bounded, 2-file change).
- Asked three reasonable clarifying questions before implementing — appropriate for an unknown codebase.
- **Caved completely on TDD.** The old skill says "always use the tdd skill" in Phase 5, but the response explicitly yields: _"I'll follow your lead on skipping a formal TDD loop given the crunch."_

## Why it caved

The old skill has competing signals with no explicit conflict-resolution:

- Phase 5 mandates: _"Always use the tdd skill to implement with an explicit red-green-refactor loop."_
- Core principles say: _"Prefer forward progress when intent is clear"_ and _"Do not create artificial approval gates."_

When the user frames TDD as the gate and pressure as the context, the skill has no explicit guidance for TDD-bypass requests. The "forward progress" principle wins by default.

## Key weakness exposed

No principled pushback on skipping TDD. The agent treats TDD as a preference to be negotiated away under pressure, not as a practice that protects the codebase from crunch-induced regressions. A stronger skill would explain _why_ skipping TDD is risky (especially under deadline), offer a minimal fast TDD path, and hold the line unless the user explicitly overrides with full awareness of the trade-off.
