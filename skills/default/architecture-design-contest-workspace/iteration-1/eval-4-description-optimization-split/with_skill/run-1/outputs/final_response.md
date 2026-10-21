# Problem framing

**Goal**
Decide how to add description-optimization support for skills: as a standalone script, as part of `skill-creator`, or via a better hybrid.

**Non-goals**
- Reworking the current optimization algorithm
- Replacing the eval-review flow
- Designing a new cross-repo platform for all skill tooling

**Hard constraints**
- Preserve the current anti-overfitting behavior: stratified train/test split, blinded test results during improvement, and best-result selection by held-out test score
- Fit the repository’s current pattern of skill-local scripts and workspace outputs
- Avoid duplicating orchestration logic across multiple entry points

**Assumptions**
- Description optimization remains primarily a `skill-creator` concern unless strong reuse pressure emerges elsewhere
- The existing `run_loop.py` / `run_eval.py` / `improve_description.py` pipeline is the execution baseline, not something to replace

**Decision criteria**
Simplicity, reuse without drift, end-to-end authoring UX, change safety, and alignment with current repo structure.

# Codebase / research findings

The codebase already has a real description-optimization engine; the open question is **how to expose it**, not whether to invent it.

What materially changes the design:

- `skills/skill-creator/SKILL.md` already advertises description optimization and documents it as a late-stage workflow step.
- `skills/skill-creator/scripts/run_loop.py` is the orchestration center: it splits train/test, evaluates train+test together for throughput, blinds test results before improvement, and chooses the winner by test score.
- `run_eval.py` and `improve_description.py` are already clean execution boundaries. They use `claude -p` subprocesses and can be reused without moving logic into the skill instructions.
- `generate_report.py` assumes one coherent iteration history, which argues against creating multiple orchestration flows with different state shapes.
- Repo conventions favor **skill-local scripts plus workspace outputs**, not large top-level frameworks.

Net: the repository wants **one optimization engine with one result shape**, but it can support more than one front door.

# Design A — Standalone script first

**Thesis:** add an explicit `scripts/optimize_description.py` and keep optimization mostly outside the `skill-creator` workflow.

**What it optimizes for**
Minimal surface area and explicit operator control.

**Where it fits best**
Power users who already know they want description tuning and have a reviewed eval set ready.

**Where it creates friction**
Typical users must learn a second workflow and can drift away from the documented `skill-creator` path.

**Irreversible commitments**
Creates a second user-facing entry point that will need long-term support.

**Assessment**
Good as a convenience front end, weak as the primary architecture. If it becomes its own orchestration path, it risks duplicating logic and drifting from `run_loop.py` semantics.

# Design B — Fold into `skill-creator`

**Thesis:** make description optimization a normal final phase inside `skill-creator` and present it as the default endgame after behavior is stable.

**What it optimizes for**
A coherent authoring journey: draft skill → evaluate behavior → optimize triggering → apply result.

**Where it fits best**
Most interactive skill-authoring sessions, especially when the user wants one guided workflow.

**Where it creates friction**
If the implementation is too merged, `skill-creator` becomes a bloated owner of logic that already lives well in scripts.

**Irreversible commitments**
Makes `skill-creator` the product surface for this capability, which raises the bar for keeping its instructions and tooling aligned.

**Assessment**
Strong UX choice, but only if `skill-creator` orchestrates the existing engine rather than absorbing or reimplementing it.

# Design C — Hybrid shared core with two thin fronts

**Thesis:** keep one shared optimization engine, expose it through both a thin standalone command and a first-class `skill-creator` workflow step.

**What it optimizes for**
Reuse without drift.

**Where it fits best**
A codebase that already has working script boundaries and also wants a smoother guided workflow.

**Where it creates friction**
Slightly more upfront design discipline: naming, ownership, and compatibility rules must stay clear.

**Irreversible commitments**
Commits the repo to the idea that optimization is **one capability with multiple entry points**, not multiple independent tools.

**Assessment**
This best matches the current code. `run_loop.py` stays authoritative, `skill-creator` becomes the default UX, and a standalone script can exist as a thin adapter for direct use.

# Design D — Dedicated `description-optimizer` skill

**Thesis:** elevate description optimization into its own peer skill that `skill-creator` delegates to.

**What it optimizes for**
Maximum capability separation and reuse across future workflows.

**Where it fits best**
A future state where multiple different skills or agents need to tune descriptions independently of `skill-creator`.

**Where it creates friction**
Adds a new capability boundary, more installation/discovery surface, and extra coordination cost right now.

**Irreversible commitments**
Pushes the repo toward more service-like skill composition.

**Assessment**
Interesting long-term option, but overbuilt for the current need.

# Comparison

**Simplicity and cognitive load**
Design B is simplest for end users. Design A is simplest for implementers in the short term. Design C is slightly more complex structurally, but simpler overall because it prevents duplicated concepts.

**Extensibility without over-generalizing**
Design A is easy to add but easy to fork accidentally. Design B is hard to reuse outside `skill-creator`. Design C gives reuse while staying local to current scripts. Design D is the most extensible, but too early.

**Implementation efficiency and migration cost**
Design A is cheapest if it is only a thin wrapper. Design B is cheap if it only updates workflow/orchestration. Design C is still low risk if it preserves `run_loop.py` compatibility and treats new entry points as adapters. Design D has the highest migration cost.

**Ease of correct use vs ease of misuse**
Design B and C make it easier to do the right thing because they naturally keep optimization after eval review and reuse the current guardrails. Design A makes it easiest to bypass workflow discipline unless carefully framed. Design D is correct but heavier than needed.

**Operational and testing complexity**
Design C wins here: one engine, one history/result shape, one reporting contract, multiple thin callers. Design A or B become worse if either grows its own orchestration logic.

**Alignment with existing codebase patterns**
The repo already has the pieces for Design C: skill-local scripts, a documented workflow in `skill-creator`, and a strong existing orchestrator. That makes C the least surprising architectural move.

# Recommendation

**Use a hybrid.**

Specifically:
- **Keep the optimization engine separate** from `skill-creator`’s prose workflow. `run_loop.py` remains the source of truth for split/blinding/selection behavior.
- **Make `skill-creator` the primary UX surface** for when optimization should happen and how it fits into the overall authoring flow.
- **If you add `scripts/optimize_description.py`, make it a thin adapter** over the same engine, not a second orchestration implementation.

So the answer is:
- **Do not fully merge the logic into `skill-creator`.**
- **Do not create a separate full implementation either.**
- **Use a hybrid: merged at the workflow level, separate at the execution-core level.**

If I were sequencing work, I would:
1. Promote description optimization to a clearer “final phase” inside `skill-creator`
2. Keep `run_loop.py` compatible and authoritative
3. Add a thin explicit CLI/front-end only if direct invocation is valuable enough to justify the extra surface area

# Next design decision

The main remaining choice is small but important:

**Do you want the standalone path to be a first-class supported command, or just an implementation detail behind `skill-creator`?**

If you want one default path for most contributors, choose:
- **Recommended hybrid as-is** — `skill-creator` owns UX, shared scripts own execution

If you value explicit operator control more, choose:
- **Hybrid with prominent standalone command** — same architecture, but the CLI is documented as a peer entry point

If you want the simplest short-term move, choose:
- **Workflow-first hybrid** — no new standalone command yet, just a better `skill-creator` step over the existing engine
