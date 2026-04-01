# Feature Dev Skill Improvement — Product-Sized Work in Unfamiliar Repos

**Track**: Standard — the request has a clear goal (improve the skill for a specific scenario) but meaningful ambiguity about what "product-sized" and "better" mean in practice. It touches several files/sections but doesn't require speculative architecture choices.

---

## Understanding

You want the `feature-dev` skill to handle two overlapping challenges better:

1. **Product-sized work** — features that are broader than a single well-defined code task: multi-file epics, changes with significant product/business context, features that require understanding success criteria and user impact, not just API shapes.
2. **Unfamiliar repos** — codebases where the agent/developer has no prior knowledge of conventions, domain, or architecture and needs significantly more orientation before feature-specific exploration is useful.

The current skill calibrates process for _code task complexity_ (Light / Standard / Deep) but treats familiarity with the repo and product context as implicit. That's the core mismatch.

---

## Relevant Findings

Explored `skills/feature-dev/SKILL.md` and the repo structure. Specific gaps:

**`SKILL.md` — Process Selection (lines ~30–55)**
The track criteria are: scope, ambiguity, risk. There is no axis for _repo familiarity_. A light-track task in a totally unknown repo still requires significantly more codebase orientation than a light-track task in a repo the agent knows well. The tracks can silently under-scope exploration.

**`SKILL.md` — Phase 2: Codebase Exploration (lines ~101–115)**
Agent prompts are feature/architecture focused: "find features similar to X," "map the architecture for X." They skip a foundational orientation step: reading the README, identifying tech stack, locating build/test commands, understanding the domain language. In unfamiliar repos, agents often waste exploration budget rediscovering basics.

**`SKILL.md` — Phase 3: Clarifying Questions (lines ~119–135)**
The question scope covers: edge cases, error handling, integration points, scope boundaries, design preferences, backward compatibility, performance. For product-sized work, this omits the product layer: what does success look like, who are the users, where does this fit in the roadmap, what teams or systems are upstream/downstream, what's the rollout plan. Technically correct implementations can still be product-wrong.

**`references/handoff-plan-template.md`**
Has `Technical Context and Constraints` but no `Product Context` section. If a product-sized feature is handed off to another agent or developer, the business rationale and success criteria aren't captured in the artifact, so the next agent re-derives (or ignores) them.

**`SKILL.md` — Phase 5/6: Implementation and Review**
Correctly mandates TDD (red-green-refactor loop via the `tdd` skill), independent code-reviewer agents, and code-simplifier subagent usage. These constraints must be preserved in any revision.

---

## Open Questions

Three questions that would materially change the design of the fix:

1. **What does "product-sized" scope to you?** Sprint-scale (1–2 week feature)? Quarter-scale epic? Something that crosses org boundaries or requires stakeholder sign-off? This determines whether product-context questions belong in a side note or need their own phase section.

2. **What's the concrete failure mode you've seen?** E.g., "the agent asked no questions about business goals," "it missed major architectural constraints in a green-field service," or "it built the right thing technically but wrong for the product." Knowing the actual failure shapes which fix has the most leverage.

3. **Should unfamiliar-repo orientation produce a reusable artifact?** If the agent produces a repo-summary file on first contact, subsequent tasks in the same repo can load it instead of re-exploring from scratch. That's a bigger change to the skill than a one-task orientation pass. Worth knowing if you want that.

---

## Recommendation

Make two targeted additions to the skill — enough to address the gaps without restructuring the entire workflow:

### Change 1 — Unfamiliar-Repo Orientation Sub-Phase (Phase 2)

Add a conditional step at the start of Phase 2: when the repo is new (no prior context, task is in an unknown codebase), run a short "orient before you explore" pass before launching feature-specific agents. The orientation covers: README, tech stack, build/test entry points, domain vocabulary. This prevents agents from diving into feature code without understanding what module system, test runner, or domain language they're working in.

Why it helps: code-explorer agents produce higher-signal summaries when they already know the lay of the land. Without orientation, they often surface the wrong abstraction level or miss that a naming convention makes similar features look different.

### Change 2 — Product-Context Questions (Phase 3)

For feature work that is product-sized (involves significant user-facing impact, cross-team coordination, or ambiguous business requirements), extend the clarifying question list to include: what does success look like, who are the affected users, what are the upstream/downstream dependencies, and is there a rollout or gradual-release constraint?

These can be gated on scope signal — they're not needed for a bounded internal refactor but are nearly always needed when a feature has a user-facing story or a product decision baked in.

This change prevents the skill from optimizing purely for code correctness on work where product correctness is the actual bar.

### Optional Change 3 — Product Context in Handoff Template

Add a short `Product Context` block to `references/handoff-plan-template.md` alongside the existing `Technical Context and Constraints`. Fields: business goal, success criteria, user impact, rollout plan. Low-effort addition that makes handoffs for product-sized work substantially more useful.

### What stays the same

Implementation (Phase 5) and review (Phase 6) keep their current mandatory requirements: TDD with explicit red-green-refactor loop via the `tdd` skill, independent code-reviewer agents for every track, and code-simplifier subagent usage. These are non-negotiable regardless of how discovery and questions change.

---

## Implementation Map

No changes made yet per your request. When ready to edit:

- `skills/feature-dev/SKILL.md` — Phase 2 (orientation sub-phase), Phase 3 (product-context questions)
- `skills/feature-dev/references/handoff-plan-template.md` — add `Product Context` block

Validation: run existing evals to confirm no regressions on non-product-sized tasks before confirming the changes hold for the target scenario.

---

## Artifact Status

No handoff artifact written — you asked for discovery only. If the recommended changes are confirmed, I'll write a handoff plan before editing the skill files.
