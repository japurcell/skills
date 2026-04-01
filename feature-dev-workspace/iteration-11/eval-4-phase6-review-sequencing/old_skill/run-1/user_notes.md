# Run Notes — Eval 4, Old Skill, Run 1

**Date**: 2026-04-01  
**Skill**: old-skill-snapshot/SKILL.md (baseline feature-dev)  
**Eval**: 4 — Phase 6 review sequencing

## What the old skill says about Phase 6

- Standard/Deep track: launch **multiple** `code-reviewer` agents **in parallel** with different focuses
- Mentioned focuses: simplicity, correctness, conventions
- Then consolidate → fix high-severity → surface remaining risks

## Key observation

The old skill is vague on the number of agents: it says "multiple" and gives three example focuses, but does not mandate exactly three. It also says "in parallel" — there is no explicit ordering constraint between the reviewers. The response reasonably interpreted this as three parallel agents.

## Potential weakness for eval scoring

- No agent count is hard-specified; "multiple" is left to interpreter discretion
- No guidance on what to do if agent findings conflict
- No instruction to read the files agents flag before acting (contrast with Phase 2 which explicitly says to read identified files)
