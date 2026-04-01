# Response: Feature-dev for Product-Sized Work in Unfamiliar Repos

**Track**: Standard. The request involves exploring one skill file and a focused body of related files to identify gaps and propose changes. There's some ambiguity about what "product-sized" means in the user's context, which warrants a few targeted questions before recommending. Not Deep — the scope is bounded and the skill is well-structured; this doesn't need broad multi-angle exploration.

---

## Understanding

The user wants the feature-dev skill to better handle two related conditions that compound each other: **product-scale scope** (larger than a single bounded feature) and **unfamiliar repositories** (no existing mental model of architecture, conventions, or dev environment). The request explicitly stops at discovery — "before editing anything" — so this response covers findings, open questions, and a recommended approach only.

---

## Relevant Findings

From reading `skills/feature-dev/SKILL.md` and the agents in `skills/feature-dev/agents/`:

**1. Unfamiliar codebases are already in scope — but orientation isn't explicit.**
The frontmatter description says "medium-to-large changes in unfamiliar codebases," but nothing in Phase 2 defines what to do when the repo is genuinely foreign. There's no step that says: read the README, check CI config, find the test runner. Code-explorer agents launched without that foundation produce architecture summaries that are accurate but may miss critical conventions (custom test runners, repo-specific patterns, ownership models).

**2. All code-explorer prompt templates are purely technical.**
Phase 2 lists four example agent prompts: "Find features similar to...", "Map the architecture...", "Analyze the current implementation...", "Identify UI patterns, testing approaches, or extension points." Every one is feature- or implementation-scoped. There's no template for "orient to this repo's dev environment and repo structure" — which is the most common gap when entering an unfamiliar codebase at product scale.

**3. Phase 3 (Clarifying Questions) has no product-layer prompts.**
The guidance lists edge cases, error handling, integration points, scope boundaries, design preferences, backward compatibility, and performance needs. These are all implementation-level. For product-sized work, the blocking unknowns often live one level up: release milestone, migration plan, stakeholder sign-off, whether a breaking API change is acceptable, or whether the work overlaps an active sprint on another team.

**4. The Deep track assumes you can go broad technically, not that you need product context.**
Deep says "Run broad exploration across architecture, similar features, and constraints" with 2-3 code-explorer agents. This is good for large technical changes, but doesn't address the product framing that product-sized work requires before technical exploration can be productive.

**5. Implementation and review requirements are already correct.**
Phase 5 mandates TDD with an explicit red-green-refactor loop on every track. Phase 6 mandates a code-simplifier subagent for refactoring opportunities and independent code-reviewer subagents for quality review — also on every track. These don't need to change.

---

## Open Questions

Three questions that would materially change the scope of each proposed change:

1. **What does "product-sized" mean in your context?**
   The skill has a Deep track for large work. Are you finding that Deep-track responses are still too technically framed when the problem requires product-strategy thinking (release timelines, migration plans, stakeholder sign-off)? Or is this about work that genuinely spans multiple features or sprints where the current skill doesn't have a natural wedge?

2. **What's the specific failure mode you've encountered?**
   For example: does the agent skip repo orientation (never checks how to run tests or what CI is), ask technically focused questions when product-level ones would unblock the work, or produce plans that are accurate but not actionable in an unfamiliar repo because they assume too much context?

3. **Is "unfamiliar repo" primarily about developer setup or product context?**
   There's a meaningful difference between orienting to "how do I build and test this codebase" vs. "what's the release cadence and who owns this product." Both are valid gaps — the fix for each is different.

---

## Recommendation

Three targeted additions to `skills/feature-dev/SKILL.md`, each tied to a specific gap. These are proposals, not final decisions — answers to the questions above would refine or narrow them.

---

### Change 1 — Repo Orientation sub-step in Phase 2

**Gap addressed**: Code-explorer agents in unfamiliar repos produce technically accurate summaries but miss foundational conventions.

**Proposed addition**: In Phase 2, before launching code-explorer agents, add an explicit orientation step for unfamiliar repos (explicitly triggered when the repo is new to the agent or the user says "unfamiliar"). The agent (not a subagent) does a 5-minute pass: read the README, find the CI config (`.github/workflows`, `Makefile`, etc.), identify the test runner, note the build system. This is logged as context before any code-explorer agent is launched.

**Why this helps unfamiliar repos specifically**: Without it, code-explorer agents often assume a standard stack and may miss that "run tests" means something repo-specific. Orientation anchors downstream agents in the actual dev environment rather than an assumed one.

---

### Change 2 — Product context question cluster in Phase 3

**Gap addressed**: Phase 3 question guidance is implementation-scoped; product-sized work often blocks on questions one level above implementation.

**Proposed addition**: Add a product-layer question cluster as a named example set within Phase 3, conditionally surfaced for large or product-sized work: release milestone or freeze, migration/backward-compatibility strategy, stakeholder sign-off requirements, overlap with other teams' in-flight work. These sit above the current implementation-level questions (edge cases, error handling, etc.) and are asked first when scope is large.

**Why this helps product-sized work specifically**: A feature may be technically feasible but blocked by a release freeze two weeks out, or require a migration plan that adds a sprint. Without these questions, the agent designs toward implementation while the real blocker is a product constraint.

---

### Change 3 — New code-explorer agent prompt template for repo orientation

**Gap addressed**: The four existing example agent prompts are all about code features and architecture — none are about repo infrastructure.

**Proposed addition**: Add one new example agent prompt for the Deep track: _"Map this repository's development environment: test runner, CI/CD pipeline, major conventions, build system, and ownership model. Surface anything a developer unfamiliar with this repo would need to know before making a large change."_

**Why this helps unfamiliar repos specifically**: Gives the agent a concrete, repeatable way to frame a repo-orientation agent. Without an explicit template, agents default to architecture exploration even when the higher-priority gap is dev environment orientation.

---

## What to Keep Unchanged

- **TDD in Phase 5** — already mandatory on every track with explicit red-green-refactor loop. No change needed.
- **code-simplifier subagent in Phase 6** — already required after implementation on every track. No change needed.
- **Independent code-reviewer subagents in Phase 6** — already required on every track (Light: at least one; Standard/Deep: multiple in parallel). No change needed.

These are the right requirements at the right scope. Any implementation of the above changes must continue to follow them.

---

## Next Step

Answers to the three open questions above would confirm whether all three changes are needed or whether one of them is the primary fix. If the answers point to a clear narrow gap, only that change is worth making — the other two can remain on the table but won't be implemented.
