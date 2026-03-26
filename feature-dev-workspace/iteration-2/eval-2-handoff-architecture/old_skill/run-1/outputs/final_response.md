The cleanest improvement is to make `feature-dev` produce a reusable file-backed implementation plan instead of stopping at a chat-only architecture recommendation. This repo already has the right pattern for handoff: `create-plan` produces a durable `plan.md`, `create-tasks` turns that into executable `tasks.md`, and `implement-plan` assumes those artifacts exist. I would reuse that contract inside `feature-dev` so the skill can finish discovery and design work in a form another agent can implement directly.

The reusable planning artifact should be `.agents/scratchpad/<feature-name>/plan.md`. That should be the primary handoff artifact. When the next step is immediate delegation to an implementation agent, `feature-dev` should also generate `.agents/scratchpad/<feature-name>/tasks.md` in the same checklist format used by `create-tasks`. This keeps the handoff compatible with the rest of the repo instead of inventing a separate one-off brief.

The `plan.md` artifact should stay lighter than the full `create-plan` workflow, but it should reuse the same core sections from `skills/create-plan/references/plan-template.md`: summary, technical context, AGENTS.md or repo constraints, project structure, and a file-by-file implementation map. For `feature-dev`, I would add two handoff-specific sections: `Open Questions / Assumptions` and `Validation Plan`. That gives the implementing agent the missing context that the old snapshot currently leaves implicit.

This is a good fit for the repo because the old `feature-dev` snapshot has a gap between design and implementation. It asks architecture agents for options, then waits for approval before Phase 5, but it does not define a durable artifact another agent can pick up. By contrast, the repo’s planning skills already prefer persistent artifacts under `.agents/scratchpad/<feature-name>/`, and the current live `skills/feature-dev/SKILL.md` has already started moving in this direction with `Leave reusable artifacts` and a short `Handoff Artifact` section. The improvement here is to make that artifact explicit, file-backed, and structurally compatible with the existing planning pipeline.

Concrete implementation map:

1. Update `skills/feature-dev/SKILL.md`.
   - Extend the description so the skill triggers for feature work that may require a reusable planning artifact or agent handoff.
   - Add a `Handoff Mode` or equivalent rule near process selection: if the user wants design only, another agent will implement, or the work pauses before coding, write `.agents/scratchpad/<feature-name>/plan.md` before stopping.
   - In the architecture phase, require the final recommendation to be converted into the artifact rather than ending at a comparison of approaches.
   - In the implementation phase, replace the hard approval gate with a conditional: implement if the user asked for implementation and blockers are resolved; otherwise stop after writing the handoff artifact.
   - Expand the current brief `Handoff Artifact` section into an explicit output contract naming the artifact path and required sections.

2. Add `skills/feature-dev/references/handoff-plan-template.md`.
   - Base it on `skills/create-plan/references/plan-template.md`, but trim it for feature-dev use.
   - Keep these sections: Goal, Non-goals, Relevant Findings, Technical Context, Project Structure, Recommended Design, File-by-file Implementation Map, Validation Plan, Open Questions / Assumptions, Next Step.
   - The `Next Step` section should explicitly say whether the artifact is ready for direct implementation or whether `tasks.md` still needs to be generated.

3. Update `skills/feature-dev/agents/code-architect.md`.
   - Require outputs that map cleanly into the handoff artifact: recommended design, trade-offs, concrete file changes, sequencing, validation, and unresolved assumptions.
   - Add a short requirement to call out which findings belong in `plan.md` versus which are just supporting rationale.

4. Update `skills/feature-dev/agents/code-explorer.md`.
   - Require a tighter handoff-oriented summary: key files to reread, integration points, relevant constraints, and risks.
   - This keeps the artifact grounded in source evidence instead of becoming a generic architecture memo.

5. Optionally update `skills/feature-dev/SKILL.md` again to define when `tasks.md` should be emitted.
   - For medium or larger delegated work, write `tasks.md` using the same checklist format as `skills/create-tasks/SKILL.md`.
   - For smaller or still-ambiguous work, stop at `plan.md` and list the missing information needed before task generation.

I would not duplicate the entire `create-spec` -> `create-plan` -> `create-tasks` pipeline inside `feature-dev`. That would make the skill too heavy for medium-sized work. The better trade-off is a lightweight `plan.md` artifact that reuses the repo’s structure, plus optional `tasks.md` generation only when the handoff is immediate and the design is stable enough to decompose into executable tasks.

If implemented this way, the handoff becomes clean for both humans and agents: discovery findings stay attached to source files, the recommended design is preserved in a standard location, and the next agent can either implement from `plan.md` directly or continue with `tasks.md` generation without redoing exploration.
