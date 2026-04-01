# Feature Dev: Improve Skill for Product-Sized Work in Unfamiliar Repos

**Track**: Standard  
_This is a meta-feature: improving the feature-dev skill itself. It's moderately ambiguous (what "product-sized" and "unfamiliar" mean precisely affects the design), has genuine design choices, and the user explicitly wants a discovery-only pass before any editing._

---

## Understanding

The user wants to improve the feature-dev skill to handle **product-sized work** (larger-than-medium scope) in **unfamiliar repositories** (codebases the agent hasn't seen before). The ask is pre-implementation: figure out the gaps, surface the questions that matter, and recommend an approach. No edits yet.

---

## Relevant Findings

From exploring this repository:

**`skills/feature-dev/SKILL.md`** — Current skill.

- Three tracks (Light / Standard / Deep) selected up front.
- Deep Track description: "large, risky, cross-cutting, or highly ambiguous work." No distinction between _large-but-familiar_ vs. _large-and-unfamiliar_.
- Phase 2 (Exploration) scales the number of code-explorer agents by track but frames all agents as feature-focused ("find similar features," "map the architecture for [feature area]"). There is **no repo-orientation pass** before diving into a specific feature area.
- Phase 3 (Clarifying Questions) is generic: edge cases, error handling, integration points, design preferences. **Product-level context is absent**: stakeholders, feature flags, rollout strategy, backward-compatibility windows, downstream system impact.
- Phase 4 (Architecture) can spawn code-architect agents but does not call out when to escalate to an external skill like `create-plan` or `create-spec`.
- Phase 5 (Implementation) says "do not create artificial approval gates" — useful principle, but for product-sized work in an unfamiliar repo this can fire too aggressively and skip legitimately necessary checkpoints.

**`skills/feature-dev/references/handoff-plan-template.md`**

- Has `Non-goals`, `Technical Context and Constraints`, and `Open Questions` sections.
- Missing: deployment/rollout concern, affected teams/consumers, integration test surface, migration scope. The template works well for engineering scope; it's thin on product scope.

**`skills/feature-dev-workspace/`** (10 iterations of evolution)

- Iterations show a history of tightening phases for smaller work. No iteration appears to have specifically targeted the unfamiliar-large-repo scenario based on directory naming.

**`skills/create-plan/SKILL.md`** / **`skills/create-spec/SKILL.md`** (exist in repo)

- There are sibling skills for planning and spec'ing. The feature-dev skill does not currently instruct the agent when to hand off to or compose with these skills, even though "product-sized" work often warrants a spec or plan artifact before implementation.

**Key gap summary**:

1. No repo-orientation step — exploration jumps to the feature area without building a base mental model of the repo.
2. No product-context questions — product-sized work requires understanding stakeholders, compatibility, phasing, rollout, and consumers.
3. Deep Track doesn't specialize for unfamiliar repos vs. familiar ones.
4. No escalation path to `create-plan`/`create-spec` for work that genuinely needs a plan before code.
5. Handoff template is engineering-complete but product-thin.

---

## Open Questions

These are the questions I'd ask before editing anything. They would materially change the shape of the fix:

**1. What does "product-sized" mean to you?**  
Options: multi-sprint, multi-engineer, cross-team, cross-subsystem, carries explicit product requirements (PRD or spec), or all of the above? The answer determines whether product-context gathering needs to be a new phase or just additional questions within Phase 3.

**2. What's the failure mode you've actually observed?**  
Is the skill:

- (a) Making wrong architectural decisions because it didn't understand the repo's actual patterns before designing?
- (b) Skipping product-context questions that later caused rework (e.g., not asking about backward compatibility, then designing a breaking change)?
- (c) Jumping to implementation when it should have paused for a spec or plan?
- (d) Getting lost in large repos because exploration agents go too narrow too fast?

The answer determines which phase(s) to fix most urgently.

**3. What does "unfamiliar repo" mean in practice?**  
Options: a repo in a language/framework the agent hasn't worked in; a large codebase with no obvious entry point; a repo with heavy internal conventions undocumented in README; or simply any repo seen for the first time in a session. This determines how much repo-orientation work to prescribe.

**4. Should the skill handle the full workflow itself, or should it route to `create-plan` / `create-spec` for genuinely large work?**  
If product-sized work should sometimes produce a spec or plan artifact first, the skill needs routing logic. If the skill should keep doing everything itself, the fix is internal (new phase, richer questions).

**5. Is there a specific case or session that motivated this request?**  
A concrete example of where things went wrong would let me pinpoint the exact gaps rather than fixing all plausible ones.

---

## Recommendation

**Based on the findings above, the most impactful improvements for product-sized work in unfamiliar repos are likely:**

### A — Add a Repo Orientation Sub-step to Phase 2 for Deep Track

When the track is Deep (and especially when the repo is unfamiliar), add a mandatory repo-orientation pass _before_ launching feature-focused exploration agents. This pass:

- Maps the repo top-level: languages, frameworks, build system, test strategy, major subsystems.
- Identifies whether there are existing conventions docs (ADRs, AGENTS.md, README architecture sections).
- Returns a "known unknowns" list that scopes subsequent feature-focused agents better.

Without this, agents go narrow immediately and miss load-bearing patterns they'd have noticed with 5 minutes of orientation.

### B — Add Product-Context Questions to Phase 3 for Standard/Deep Tracks

Extend the clarifying questions section with a product-scoped question group:

- Who consumes this feature (users, downstream services, other teams)?
- Is backward compatibility or a migration required?
- Are there rollout constraints (feature flags, phased deploy, gradual rollout)?
- Are there stakeholders who need to approve the design before implementation starts?

These are not engineering questions; they are product questions that currently fall through the cracks.

### C — Add Explicit Escalation Guidance for Product-Sized Work

When exploration + questions reveal that the work is actually multi-sprint, cross-team, or requires a written spec before coding, the skill should instruct the agent to either:

- Produce a `create-plan` or `create-spec` artifact and pause, or
- Say explicitly to the user that this work has crossed the scope boundary where a plan/spec should precede implementation.

Currently there's no guidance here, and "prefer forward progress" can push the agent past this moment.

### D — Enrich the Handoff Template for Product Scope

Add optional sections to the handoff template:

- **Affected Consumers / Downstream Systems**
- **Rollout and Compatibility Notes**
- **Blocking External Dependencies** (design review, infra provisioning, third-party APIs)

These are no-ops for small work but become critical for product-sized features.

---

## Implementation Map

_Deferred until the Open Questions above are answered. The shape of the changes is clear at a sketch level, but the exact wording, phase placement, and depth of new instructions depend on the answers to Q2 (failure mode) and Q4 (routing vs. internal)._

When ready to implement:

- Primary edit target: `skills/feature-dev/SKILL.md` — Phase 2, Phase 3, and track descriptions
- Secondary edit target: `skills/feature-dev/references/handoff-plan-template.md` — add product-scope sections
- Optional: `skills/feature-dev/agents/code-explorer.md` — add repo-orientation agent prompt variant

---

## Artifact Status

No handoff artifact written yet — the user asked for discovery-only. If you want to proceed to implementation, answer the five questions above (especially Q2 and Q4) and I'll update the skill.
