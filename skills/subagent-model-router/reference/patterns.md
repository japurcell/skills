# Routing Patterns

Use after `SKILL.md` when examples help.

## Reuse vs fresh routing

Reuse a prior route in the same launch group when work class, stakes, ambiguity, and model constraints are unchanged.

Do fresh routing when any of those change.

| Situation | Route |
|---|---|
| Five workers run the same deterministic fixture checks | route first as `task` + fast; reuse for rest |
| Three reviewers inspect similar diffs with same pinned model | route first; reuse while constraints match |
| Bounded tests change to architecture tradeoff analysis | fresh route |
| Standard review changes to high-stakes security audit | fresh route |

## Fast by default

Use fast tier for:

- tests, builds, lint, scripts
- repo search and candidate-file lists
- log or benchmark summaries
- deterministic checks and fixture comparisons
- small isolated transformations
- very small isolated edits, if no broad code context is needed

Examples:

- Run tests and summarize failures → `task` + fast.
- Search repo for token lifecycle code → `explore` + fast.
- Read huge logs and give short diagnosis → low input-cost model.

## Standard when reasoning dominates

Use standard tier for:

- debugging across files
- non-trivial code edits
- design revisions with tradeoffs
- large or context-dependent reviews
- judgment-heavy code review

Examples:

- Review a 40-file security-sensitive diff → review agent + standard.
- Edit connected files → standard.
- Debug routing/auth/cache interaction → standard.

## Premium only when defensible

Use premium tier for:

- repeated lower-tier failure
- high-stakes analysis
- broad or novel ambiguous tasks
- architecture/security analysis across systems
- explicit user request for best available reasoning

Examples:

- Standard agents failed on distributed consistency bug → premium may fit.
- Critical auth redesign with threat models → premium may fit.
- Run tests and summarize output → not premium.

## Availability fallbacks

When a model is unavailable:

1. Stay in the selected tier if possible.
2. Pick the next cheapest suitable model in that tier.
3. Change tiers only if the tier is unavailable or the task requires it.
4. Mention the availability-driven change briefly.

## Token-shape examples

| Request | Optimize for |
|---|---|
| Huge log bundle, short diagnosis | input cost |
| Long architecture proposal from short prompt | output cost |
| Same repo context across subagents | cached input cost |
| Anthropic with reusable cache | cache write + cached input |
