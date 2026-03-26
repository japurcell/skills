Uncertainties and trade-offs for human review:

- The main design choice is whether `feature-dev` should always write both `plan.md` and `tasks.md`, or only require `plan.md` and generate `tasks.md` when delegation is explicit. I recommend `plan.md` always, `tasks.md` conditionally, to avoid over-processing medium-sized work.
- There is a second choice between reusing the existing `create-plan` and `create-tasks` templates by reference versus copying their structure into new feature-dev-specific templates. Reusing the existing structure reduces drift, but a lighter feature-dev template may be easier to keep concise.
- The current live `skills/feature-dev/SKILL.md` already contains a `Handoff Artifact` section. If the goal is to improve the old snapshot only, the work is a backport plus stronger file-backed output rules rather than a fully new concept.
- The old snapshot uses a strict approval gate before implementation. Changing that gate affects more than handoff quality; it also changes the skill’s overall interaction model. If maintainers want a minimal patch, keep the gate and only add the artifact. If they want a better end-to-end workflow, relax the gate conditionally as in the current live skill.
- I did not modify repository files. All proposed file changes are design recommendations only, per the benchmark constraints.
