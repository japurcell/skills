The current [skills/feature-dev/SKILL.md](skills/feature-dev/SKILL.md) has the right high-level instinct for feature work: explore the codebase, ask clarifying questions, design before implementation, then review. The problem is that it is still tuned more like a direct implementation workflow than a product-sized discovery workflow.

In this repo, the gaps show up pretty clearly:

- [skills/feature-dev/SKILL.md](skills/feature-dev/SKILL.md) only does a light discovery pass, then moves straight from exploration to questions to architecture. There is no explicit repo-triage step, no artifact for capturing unknowns, and no gate for "this repo is too unfamiliar to edit safely yet."
- [skills/feature-dev/agents/code-explorer.md](skills/feature-dev/agents/code-explorer.md) is good at tracing code, but it does not explicitly ask for repo shape, package boundaries, build/test commands, ownership seams, or safe extension points. Those are the things that matter most in unfamiliar repos.
- Nearby skills in this repo already have stronger patterns for larger work. [skills/research/SKILL.md](skills/research/SKILL.md) explicitly turns unknowns into research tasks. [skills/create-plan/SKILL.md](skills/create-plan/SKILL.md) uses a technical-context section with `NEEDS CLARIFICATION` markers. [skills/implement-plan/SKILL.md](skills/implement-plan/SKILL.md) assumes there is already a reusable planning artifact before coding starts.

What I would change before touching implementation behavior is this:

## What should change

1. Make `feature-dev` an orchestrator for larger work, not just a code-writing workflow.
   For product-sized work in unfamiliar repos, the default outcome should be a repo-aware plan and a clarified problem statement, not immediate code edits.

2. Add an explicit `Repo Triage` phase before normal discovery.
   That phase should answer: what kind of repo is this, what instructions govern it, what are the main modules, where are the likely extension points, how do you validate changes, and what unknowns block safe implementation.

3. Add a required `Problem Framing` artifact.
   The current skill summarizes findings conversationally, but larger work needs a durable handoff artifact. At minimum it should capture scope, affected areas, assumptions, risks, open questions, validation strategy, and recommended next phase.

4. Replace generic clarifying questions with batched, risk-ranked questions.
   The current Phase 3 says to identify ambiguities, but it does not force prioritization. In unfamiliar repos, the skill should ask only the questions that change architecture, scope, sequencing, or validation. Everything else should be treated as an assumption and called out explicitly.

5. Add a size-based fork in the workflow.
   Small or well-bounded work can stay close to the current path. Medium-to-large or cross-cutting work should branch into a planning path that borrows from [skills/create-plan/SKILL.md](skills/create-plan/SKILL.md) and [skills/research/SKILL.md](skills/research/SKILL.md).

6. Tighten the subagent prompts.
   The current explorer/architect prompts are strong on analysis, but they need repo-onboarding concerns: package boundaries, integration seams, migration risk, testing surface, operational constraints, and what must be confirmed before editing.

7. Add an explicit stop condition before implementation.
   Right now the skill says "DO NOT START WITHOUT USER APPROVAL," which is good, but it still assumes approval is the main gate. For unfamiliar repos, there should also be a readiness gate: unresolved scope ambiguity, no safe validation path, unclear ownership boundaries, or missing architecture decision means stop and clarify.

## Questions I’d ask you before editing the skill

1. When you say `product-sized`, what behavior do you actually want the skill to change: more questions, better repo mapping, a reusable plan artifact, stronger handoff to implementation, or all of the above?
2. Should `feature-dev` remain an end-to-end skill, or should it become a front door that hands off to planning-oriented skills once the work is large or the repo is unfamiliar?
3. Do you want the skill to create files such as `spec.md`, `research.md`, or `plan.md`, or do you want it to stay conversational until you explicitly approve artifact creation?
4. In unfamiliar repos, how cautious should it be by default: ask more up front and avoid premature edits, or stay fast and make reasonable assumptions unless risk is high?
5. What are the strongest signals that a repo is "unfamiliar enough" to require the heavier workflow: monorepo shape, multiple packages, missing docs, no obvious entry points, broad cross-cutting changes, or something else?
6. Do you want a hard cap on clarification questions, with the skill forced to prioritize the top few that materially affect design?
7. Should architecture mode still present multiple approaches for user choice, or should it present one recommended path plus a fallback for larger tasks?
8. Do you want the improved skill to stop before editing when it cannot identify a credible validation strategy, even if the user is otherwise ready to proceed?

## Recommended approach before editing anything

I would not start by tweaking wording inside [skills/feature-dev/SKILL.md](skills/feature-dev/SKILL.md) in place. I’d first align on the operating model, because the repo already suggests a better composition pattern than trying to make one giant skill do everything.

My recommendation is:

1. Reframe `feature-dev` as a staged router.
   Stage A: qualify the task and triage the repo.
   Stage B: explore and produce a problem-framing artifact.
   Stage C: either continue with a lightweight implementation path or hand off to planning/implementation skills.

2. Reuse patterns that already exist here instead of inventing new ones.
   Borrow `unknowns -> research tasks` from [skills/research/SKILL.md](skills/research/SKILL.md), `NEEDS CLARIFICATION` and technical-context discipline from [skills/create-plan/SKILL.md](skills/create-plan/SKILL.md), and the pre-implementation gate from [skills/implement-plan/SKILL.md](skills/implement-plan/SKILL.md).

3. Update the supporting agent prompts at the same time.
   Improving only the top-level skill will not be enough. The biggest repo-unfamiliarity gap is in what the explorer and architect agents are asked to return.

4. Add explicit scaling rules.
   The current skill over-prescribes a full multi-phase process even when a task is modest, and under-specifies the planning layer when a task is large. The fix is a decision point: small tasks stay lightweight, large or unfamiliar tasks must produce a plan before any edits.

5. Validate the rewrite against the evals, especially this one and the handoff-oriented eval in [skills/feature-dev/evals/evals.json](skills/feature-dev/evals/evals.json).
   That will tell us whether the new version is actually asking better questions and producing a better pre-edit recommendation, rather than just becoming more verbose.

If you want, the next step after you answer the questions above is for me to propose a concrete rewrite plan for [skills/feature-dev/SKILL.md](skills/feature-dev/SKILL.md) and its supporting agent prompts without editing them yet.
