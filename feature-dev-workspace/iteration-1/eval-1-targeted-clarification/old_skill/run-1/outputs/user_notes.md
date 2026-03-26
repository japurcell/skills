## Uncertainties

- It is not yet clear whether `feature-dev` should stay a single end-to-end skill or become an orchestrator that hands off to `create-plan` and `implement-plan` for larger work.
- The repository shows strong planning-oriented patterns in neighboring skills, but there is no explicit repo-wide convention saying `feature-dev` must compose with them.
- The current eval prompt asks for recommendations before editing; it does not establish whether artifact creation is acceptable during normal usage.

## Trade-offs

- Making `feature-dev` more cautious will likely improve unfamiliar-repo behavior, but it may make the skill feel heavy for medium-sized work unless it gets a clear size-based fork.
- Reusing existing planning skills is lower risk and more consistent with this repo, but it can make the user experience feel fragmented unless handoff boundaries are explicit.
- Adding more clarifying questions helps quality, but without a prioritization rule it can easily regress into blocking behavior.

## Human review points

- Decide whether the desired end state is a better conversational discovery skill or a true orchestration skill.
- Decide whether the improved skill should create durable artifacts by default for large tasks.
- Confirm what counts as a "product-sized" task in this repo so scaling rules can be written and evaluated precisely.
