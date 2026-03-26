## Understanding

I’d treat this as a deep planning pass before any edits. In this repo, the main issue is not that the feature-dev workflow lacks structure. It’s that the snapshot skill is too rigid for product-sized work in unfamiliar repos: it always assumes a full multi-phase process, asks for every ambiguity, forces multiple architecture options, and blocks on explicit approval before implementation.

The repository already points to a better direction. The current feature-dev skill has calibration by task size and risk, asks only high-leverage questions, and leaves a reusable handoff artifact. Adjacent skills also reinforce the same pattern: create-spec limits clarifications to a small number of critical decisions, and create-plan turns unknowns into structured research and planning artifacts instead of leaving them as open loops.

## Relevant Findings

- The snapshot skill at /home/adam/.agents/skills/feature-dev-workspace/skill-snapshot/SKILL.md is broad and underscoped. Its description says only "guided feature development with codebase understanding and architecture focus," which does not signal medium-to-large work or unfamiliar repositories.
- The snapshot hard-codes heavy process in places that will slow product work: 2-3 exploration agents, "present all questions," 2-3 architecture approaches, and a blanket "DO NOT START WITHOUT USER APPROVAL."
- The current feature-dev skill at /home/adam/.agents/skills/feature-dev/SKILL.md already contains the missing primitives: Light/Standard/Deep tracks, "ask only high-leverage questions," forward progress when intent is clear, and a handoff artifact.
- The clarification strategy in /home/adam/.agents/skills/create-spec/SKILL.md is especially relevant. It caps clarifications at three critical items and prefers informed defaults for the rest. That is exactly the control the snapshot is missing.
- The planning structure in /home/adam/.agents/skills/create-plan/SKILL.md and /home/adam/.agents/skills/create-plan/references/plan-template.md shows how this repo handles unfamiliar technical context: capture unknowns, turn them into research, then leave a concrete implementation map.
- I would not change the feature-dev subagents first. The stronger problem is orchestration in the top-level skill, not the existence of code-explorer or code-architect prompts.

## Open Questions

1. Should product-sized work in an unfamiliar repo default to a deep track every time, or should the skill still allow a standard track when the request is clear and the affected area is reasonably bounded?

Why I’m asking: this determines whether broad exploration and multi-option architecture are mandatory or conditional.

2. Do you want feature-dev to stop after discovery, questions, and recommendation when the user explicitly asks for pre-edit planning, or should it still proceed into implementation automatically once blocking unknowns are resolved?

Why I’m asking: this sets the boundary between a planning-first skill and an execution-first skill.

3. Should clarifying questions have a hard cap, for example 3-5 prioritized questions, with everything else handled through stated assumptions?

Why I’m asking: this is the main control that prevents the skill from turning unfamiliar-repo work into a long interview.

4. For unfamiliar repositories, do you want a lightweight handoff brief in the chat response, or a stronger artifact patterned after the planning docs used elsewhere in this repo?

Why I’m asking: this affects whether the skill should leave a short recommendation or a reusable implementation brief with files, sequencing, and validation.

## Recommendation

I would evolve the snapshot toward the current feature-dev skill rather than inventing a new workflow.

The first change should be scope and calibration. Tighten the description so the skill clearly targets medium-to-large feature work, especially in unfamiliar or cross-cutting repos, and add an explicit track-selection step up front. For this use case, I’d keep Standard and Deep as the important modes: Standard for bounded multi-file work in unfamiliar code, Deep for broader product changes with unclear boundaries, integration risk, or major architectural trade-offs.

The second change should be clarification discipline. Replace the snapshot rule to present all questions with a rule to ask only high-leverage questions, capped to a small prioritized set. I’d borrow the create-spec pattern directly: prefer informed defaults, ask only when the answer materially changes scope, architecture, or user-facing behavior, and group the questions clearly.

The third change should be architecture and approval behavior. Product-sized work in unfamiliar repos does need design, but not always 2-3 full alternatives and a forced user choice. I’d change that to one recommended approach by default, with multiple options only when there is a real fork. I’d also remove the blanket implementation approval gate and replace it with a conditional stop: pause when the user explicitly asked for planning only, or when blocking unknowns remain.

The fourth change should be a required handoff artifact. That is the repo pattern most worth reusing here. Before editing anything, the skill should leave a concise implementation brief with goal, non-goals, relevant findings, assumptions, recommended design, likely file targets, and validation steps. That gives another agent or a later turn enough context to continue without repeating discovery, which matters a lot more in unfamiliar repos than in local one-file work.

## Approach Before Editing

1. Use /home/adam/.agents/skills/feature-dev/SKILL.md as the baseline for orchestration changes, because it already solves most of the calibration problem.
2. Backport the calibration, response shape, and handoff ideas into the snapshot workflow.
3. Borrow the clarification cap and assumption-first behavior from /home/adam/.agents/skills/create-spec/SKILL.md.
4. Borrow the artifact mindset from /home/adam/.agents/skills/create-plan/SKILL.md so the skill leaves a reusable implementation map before code changes.
5. Keep the existing feature-dev agents unless testing shows they are the bottleneck; the stronger bet is to fix when they are invoked and how their output is synthesized.

If your goal is specifically "better for product-sized work in unfamiliar repos before editing anything," this is the change set I’d recommend first.
