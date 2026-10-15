# Architecture contest: description-optimization support

## Inferred requirements (question + recommended answer)

1. **Should description optimization be usable outside the full skill-creation loop?** Recommended answer: **yes**. The current implementation is already script-centric (`run_loop.py`, `run_eval.py`, `improve_description.py`), so batch/headless use is a real requirement, not an edge case.
2. **Should skill-creator still present description optimization as part of its guided workflow?** Recommended answer: **yes**. `skill-creator/SKILL.md` already frames it as a first-class phase after drafting/improving the skill.
3. **Should there be one source of truth for optimization logic?** Recommended answer: **yes**. The codebase already decomposes the loop into reusable parts; duplicating that logic behind two separate products would create drift.
4. **Should the design harden headless/shared-environment behavior?** Recommended answer: **yes**. The documented flow and current scripts still lean on browser opening and temp-file assumptions (`SKILL.md` description-optimization step 2 and `run_loop.py` report handling), which is fragile in non-local environments.

## Codebase findings that matter

- `skill-creator/SKILL.md` already treats description optimization as part of the **skill-creator experience**, not as an unrelated utility. It defines four subproblems: generate trigger evals, review them, run the optimization loop, and apply `best_description`.
- The **execution model is already modular**. `run_loop.py` orchestrates; `run_eval.py` measures trigger behavior through `claude -p`; `improve_description.py` proposes rewrites; `generate_report.py` renders the report; `quick_validate.py` enforces frontmatter constraints.
- `assets/eval_review.html` is a distinct UX surface, which means the architecture already separates **engine work** from **review UI**.
- The current implementation contains an architectural smell: it is **integrated in the docs** but **separate in the code**. That mismatch is the real design problem.

## Design 1: Standalone `scripts/optimize_description.py`

This option productizes description optimization as its own user-facing CLI entry point. The script would own the whole flow: generate or load the eval set, launch the review UI, call the optimization loop, then optionally apply the winning description back to `SKILL.md`.

This design is attractive because it is easy to explain, easy to automate, and fits the repo’s existing script-first implementation style. It is also the cleanest path for CI, bulk optimization, or “optimize this one existing skill” use cases.

The downside is that it sharpens the existing split-brain: **skill-creator says optimization is part of the workflow, but users must remember a separate tool to do it**. Over time, the skill docs and the standalone command will drift unless there is very strong discipline. It also makes correct use easier for power users than for interactive users; the more flags the script gains, the more it becomes something you have to already know exists.

Where it wins most: operational simplicity for engineers and automation.
Where it loses most: guided UX and long-term discoverability.

## Design 2: Fold optimization into `skill-creator` as a native workflow state

This option makes description optimization a first-class skill-creator stage, alongside drafting, qualitative evals, and revision. Instead of teaching users a separate command, skill-creator would enter an “optimize description” state and drive the user through eval generation, review, loop execution, and application.

The best version of this design is not “jam more prose into `SKILL.md`”; it is a **stateful orchestration layer** that remembers where the user is, which eval set is active, and what the best score is so far. That produces the best interactive experience and matches the mental model already implied by `SKILL.md`.

Its weakness is architectural gravity. Once `skill-creator` owns the whole workflow, it starts absorbing concerns that are not intrinsically about skill authoring: resumability, run metadata, headless fallbacks, report lifecycle, maybe even locking. That makes the guided workflow easier to use, but it also makes `skill-creator` itself heavier and more failure-prone. The risk here is **misuse by omission** in the opposite direction: excellent for conversational sessions, awkward for scripts, CI, or one-off direct runs.

Where it wins most: end-to-end user experience.
Where it loses most: reuse outside the conversational workflow.

## Design 3: Hybrid shared engine with two thin front doors

This is the strongest option. The core description-optimization logic becomes a shared engine or package: one place that owns eval-set artifacts, loop execution, reporting, validation, and application. Then there are **two thin entry points** on top of it:

- a standalone `scripts/optimize_description.py` for direct/CI/batch/headless use
- a `skill-creator` workflow step that calls the same engine for guided use

This is not “keep both implementations.” It is **merge the logic, keep two front doors**.

Architecturally, this fits the repo best because the code already wants to be layered this way. `run_loop.py`, `run_eval.py`, and `improve_description.py` are already reusable primitives; the missing piece is a stable orchestration boundary. In this design, the engine owns canonical workspace artifacts, report generation, and safe apply/update behavior. The standalone script becomes a wrapper, and skill-creator becomes another wrapper.

This design also gives the cleanest answer to the headless/shared-environment problem. The engine can standardize on explicit workspace paths under the skill workspace instead of temp-file assumptions, always emit machine-readable JSON artifacts, and treat browser launching as optional.

Where it wins most: correctness, extensibility, and avoiding drift.
Where it loses most: it adds one more structural layer, so it is slightly more work up front than either pure option.

## Comparison

On **simplicity**, the standalone CLI is the simplest to ship in the short term because it mirrors the current script-based implementation. The integrated workflow is simpler for users but not for maintainers; it pushes orchestration complexity into skill-creator. The hybrid is slightly more structural work initially, but it keeps each layer simple: engine logic in one place, user-facing flows in thin wrappers.

On **general-purpose vs. specialized**, the integrated design is the most specialized: it assumes description optimization primarily happens inside the skill-authoring workflow. The standalone design is the most general-purpose operationally, but a little too specialized in UX because it privileges people who already know the command exists. The hybrid is the best-balanced design because it supports both the general-purpose operational cases and the specialized guided cases without duplicate logic.

On **implementation efficiency**, a pure standalone script is fastest to land, but only if you ignore future drift. A pure integration is efficient only if description optimization never needs to escape skill-creator. The hybrid is the most efficient over the life of the repo because it turns the existing scripts into a real subsystem instead of leaving them half-detached.

On **ease of correct use vs. ease of misuse**, the integrated workflow is best for correct use in interactive sessions because it naturally offers the next step. The standalone workflow is easiest to misuse by forgetting it exists or by growing too many flags. The hybrid reduces both failure modes: interactive users are led into optimization through skill-creator, while advanced users and automation still get a direct command.

The biggest divergence between the designs is this: **should “description optimization” be a product, a phase, or a capability?** Standalone treats it as a product. Integrated treats it as a phase. Hybrid treats it as a capability with multiple ways in.

## Recommendation

Use a **hybrid**.

More precisely: **merge the implementation, keep the entry points separate**.

That means:

1. Extract the current description-optimization flow into a shared engine/orchestrator layer.
2. Keep a thin `scripts/optimize_description.py` for direct use.
3. Make `skill-creator` call that same engine as a first-class workflow step.
4. Standardize artifacts and reporting in the engine so headless/browser behavior is a policy choice, not duplicated wrapper logic.

I would **not** keep the two ideas fully separate as independent implementations; that would institutionalize drift. I would also **not** merge everything into `skill-creator` alone; that would make the workflow nicer but the architecture worse.

If I had to summarize the decision in one sentence: **ship one optimization subsystem with two UX surfaces.**

## Migration sketch

Start by extracting current behavior rather than redesigning it from scratch:

- Move shared concerns out of `run_loop.py`, `run_eval.py`, and `improve_description.py` into a reusable internal module.
- Leave existing scripts as compatibility shims at first.
- Add the new thin `optimize_description.py` wrapper.
- Update `skill-creator/SKILL.md` so the guided workflow explicitly invokes the shared subsystem rather than describing a loosely coupled manual sequence.
- Normalize workspace/report paths under skill workspaces instead of temp-file/browser assumptions.

This gives you an incremental path where nothing breaks, while still converging on the cleaner architecture.

## Sources considered

### Repository files
- `skills/architecture-design-contest-workspace/skill-snapshot/SKILL.md`
- `skills/skill-creator/SKILL.md`
- `skills/skill-creator/scripts/run_loop.py`
- `skills/skill-creator/scripts/run_eval.py`
- `skills/skill-creator/scripts/improve_description.py`
- `skills/skill-creator/scripts/utils.py`
- `skills/skill-creator/scripts/generate_report.py`
- `skills/skill-creator/scripts/quick_validate.py`
- `skills/skill-creator/assets/eval_review.html`
- `skills/implement-plan-workspace/description-optimization/trigger_eval_set.json`
- `skills/implement-plan-workspace/description-optimization/manual_scorecard.md`

### External references
- Python `argparse` docs on command structure and subcommands: https://docs.python.org/3/library/argparse.html#sub-commands
- Python `pathlib` docs on explicit filesystem-path handling: https://docs.python.org/3/library/pathlib.html
- Python `tempfile` docs (useful here mainly as evidence that temp-file behavior is environmental and should be explicit): https://docs.python.org/3/library/tempfile.html
- SQLite application file format guidance (supports using a structured, queryable backing store for persistent workflow state when needed): https://www.sqlite.org/appfileformat.html
