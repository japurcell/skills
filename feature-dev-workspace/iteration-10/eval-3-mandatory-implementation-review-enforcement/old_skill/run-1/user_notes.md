# Run Notes — Eval 3, Old Skill, Run 1

## Skill version

Baseline: `/home/adam/.agents/skills/feature-dev-workspace/iteration-10/old-skill-snapshot/SKILL.md`

## Track chosen

Standard (medium-sized, three files, explicit implementation + review request).

## Key observations

- The old skill enforces review via "Always run independent code-reviewer agents for quality review on every track" in Phase 6 — the word _always_ makes it unconditional.
- Implementation gate enforcement is explicit in Phase 5: "Do not create artificial approval gates."
- Subagent roles called out: `code-explorer` (Phase 2, x2 parallel), `code-reviewer` (Phase 6, x3 parallel with different focuses: simplicity, correctness, conventions).
- The skill does name `code-architect` as a Phase 4 subagent for Deep track but Standard track only requires 1-2 approaches compared directly, no architect agent launched.
- The old skill lacks explicit TDD enforcement beyond a single mention ("Always use the tdd skill") — it does not spell out the red-green-refactor mandate in detail.
- Handoff artifact path is well-specified (`.agents/scratchpad/<slug>/handoff-plan.md`).
