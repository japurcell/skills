# Routing Patterns

Use these examples after applying the core process in `SKILL.md`.

## Cheap by Default

Use the fast tier for:

- running tests, builds, lint, or scripts and reporting results
- searching the codebase and listing candidate files
- summarizing logs, command output, or benchmark artifacts
- deterministic checks, grading, or fixture comparisons
- small isolated non-code-editing transformations
- small isolated edits only when compatible with the code editing exception

Examples:

| Request | Route |
| --- | --- |
| “Have a subagent run the test suite and summarize the failures.” | `task` agent, fast-tier model |
| “Spawn three agents to search the repo for where auth tokens are created, refreshed, and revoked.” | focused `explore` agents, fast-tier model |
| “Have a subagent read a very large log bundle and produce a short diagnosis.” | model with low input cost |
| “Have a subagent compare generated fixtures against expected outputs.” | `task` agent, fast-tier model |

## Standard When Reasoning Dominates

Use the standard tier for:

- debugging across multiple files
- writing or revising a design with meaningful tradeoffs
- implementing a non-trivial change across connected files
- reviewing a large diff that depends on architectural context
- code review where judgment matters more than simple collection
- code editing beyond a very small isolated change

Examples:

| Request | Route |
| --- | --- |
| “Launch a reviewer to inspect this 40-file security-sensitive diff for auth and data exposure bugs.” | review-focused agent, standard-tier model; escalate only if deep cross-system reasoning is needed |
| “Launch a reviewer to inspect a medium-sized diff, and `gpt-4.1` is unavailable.” | keep standard tier; choose another available standard-tier model |
| “Have a subagent edit code across several files.” | standard-tier model |
| “Debug this failure that appears to involve request routing, auth middleware, and caching.” | standard-tier model, possibly general-purpose if no specialized debugger exists |

## Premium Only When Defensible

Reserve the premium tier for:

- repeated lower-tier failure for a clear capability reason
- unusually high-stakes analysis where subtle reasoning errors are costly
- very broad or novel tasks where the user explicitly wants best-available reasoning despite expense
- architecture or security analysis spanning many systems with ambiguous constraints

Examples:

| Request | Route |
| --- | --- |
| “Previous standard-tier agents failed to identify the root cause of this distributed consistency bug.” | premium may be justified |
| “Do a best-available review of a critical authentication redesign with multiple threat models.” | premium may be justified |
| “Run the tests and summarize output.” | not premium |

## Availability Fallbacks

When a model is unavailable:

1. stay in the selected tier if possible
2. choose the next cheapest suitable model in that tier
3. only change tiers if the whole tier is unavailable or task needs force escalation
4. mention the availability-driven change briefly

Examples:

| Situation | Better fallback |
| --- | --- |
| Standard-tier model unavailable for code review | another standard-tier model |
| Fast-tier model unavailable for test execution | another fast-tier model |
| Premium unavailable for high-stakes analysis | strongest suitable standard-tier model, noting the fallback |
| Standard tier unavailable for bounded log summarization | fast-tier model may be acceptable |

## Token-Shape Examples

| Request | Cost emphasis |
| --- | --- |
| “Read this huge log bundle and produce a short diagnosis.” | input cost |
| “Draft a long architecture proposal from a short prompt.” | output cost |
| “Analyze the same large repository context across several subagents.” | cached input cost |
| “Use Anthropic with a large reusable cache.” | cache write plus cached input |
