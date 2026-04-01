# Feature-Dev Skill Improvement: Product-Sized Work in Unfamiliar Repos

## Understanding

I'm reading this as a meta-request: you want to improve the **feature-dev skill itself** so it handles product-sized work in unfamiliar repos better. "Product-sized" suggests features that span multiple subsystems, require understanding architectural intent, touch user-facing behavior, and may need alignment with product stakeholders — larger than a standard medium feature, but not necessarily monolithic.

**Chosen process track**: Deep — this is broad and ambiguous work about the skill itself, and the recommendations could meaningfully change the skill's design.

---

## Relevant Findings

Looking at the current feature-dev skill and this repository:

**What the skill does well now:**

- Three-tier calibration (Light / Standard / Deep) provides a reasonable size signal
- It delegates codebase exploration to `code-explorer` agents and reads key files afterward
- It explicitly avoids artificial approval gates on implementations
- The handoff artifact pattern (`handoff-plan.md`) is good for cross-turn continuity

**Where "product-sized work in unfamiliar repos" creates gaps:**

1. **No stakeholder/product context phase.** The skill's Phase 1 (Discovery) focuses on what to build, but product-sized work in an unfamiliar repo also requires understanding _why_ this feature exists, who uses it, and what success looks like. The clarifying questions listed are mostly technical — they don't surface product intent.

2. **Codebase exploration assumes familiarity.** The `code-explorer` agent prompts assume you know enough to ask about similar features or an "existing feature area." In a truly unfamiliar repo, the agent needs to do orientation work first (naming conventions, module boundaries, test strategy, CI setup, ownership signals in comments/commit history).

3. **Architecture design agents lack product constraint input.** The `code-architect` agents receive technical scope, but product-sized features often have constraints that aren't in the code: rollout strategy, backward compatibility windows, feature flag requirements, observability needs.

4. **No "done" criteria beyond code review.** Quality Review uses a `code-reviewer` agent but never checks whether the feature actually satisfies the original product intent. For product-sized work this gap matters — code can be clean while completely missing the requirement.

5. **Handoff artifact is implementation-focused.** The `handoff-plan-template.md` captures files, sequencing, and trade-offs but doesn't include a section for product requirements, acceptance criteria, or stakeholder alignment state.

6. **Track selection is size-only.** The Deep Track rule currently says "large, risky, cross-cutting, or highly ambiguous work." It doesn't explicitly trigger on _unfamiliarity_ — a small but unfamiliar repo would be routed to Light or Standard even though it needs orientation work.

---

## Open Questions

These would materially change what I recommend:

1. **What does "product-sized" mean to you specifically?**
   - Is it measured by: lines changed, number of subsystems touched, team coordination required, or the presence of product decision-making?
   - Are there existing examples in this repo of what you'd call product-sized vs. standard work?

2. **What breaks most often today with the current skill in unfamiliar repos?**
   - Agent exploration returns low signal? The wrong files? Misidentifies the architecture?
   - Too many or too few clarifying questions asked?
   - Implementation diverges from product intent even after a thorough process?

3. **Who is the target user of the improved skill?**
   - A single developer working alone in a new codebase?
   - An agent operating in a repo it has never seen before with no human to ask?
   - A team lead coordinating contributors across a large feature?
   - All three? (The answers imply different levels of human-in-the-loop.)

4. **Should the skill ever refuse to implement until product clarity is confirmed?**
   - Currently the skill says "Do not create artificial approval gates." For product-sized work with genuine product ambiguity, should there be a real gate where the agent stops and waits?

5. **What role do existing specification artifacts play?**
   - If the repo has AGENTS.md, an issue tracker, or ADRs, should the skill consult them before asking questions?
   - Is the expectation that those are always present, sometimes present, or absent?

6. **Are there output format expectations?**
   - Does "product-sized" work need a more formal plan document — e.g. a product brief, an ADR, a spec — vs. the current `handoff-plan.md`?

---

## Recommendation

Before editing anything, I'd focus the improvements on **four targeted areas**:

### 1. Add an unfamiliarity signal to track selection

Extend the Deep Track heuristic to trigger on _repo unfamiliarity_ as an independent axis, not just size. Add a brief "repo orientation" step (checking AGENTS.md, README, test strategy, CI config) as a mandatory Phase 1 action when the repo is new territory.

### 2. Add product context to the clarifying questions phase

Expand Phase 3 to separate _technical_ gaps from _product_ gaps. Product-sized work needs to capture: who uses this feature, what success looks like, what risks product stakeholders care about, and whether there's a rollout constraint. This makes clarifying questions higher-leverage, not more numerous.

### 3. Add a product-intent check to quality review

After the `code-reviewer` agents run, add a lightweight check: does the implementation satisfy the feature's stated acceptance criteria? This doesn't require a new agent — it can be a self-review step. But it should be explicit in the skill so it isn't skipped.

### 4. Extend the handoff artifact template

Add two optional sections to `handoff-plan-template.md`:

- **Product context**: the original intent, success criteria, and open product questions
- **Alignment state**: what has been confirmed with stakeholders and what is still assumed

None of these changes require a new phase — they slot into existing phases — so the skill stays lean.

---

## What I Would NOT Change

- The three-tier calibration — it's the right shape; it just needs `unfamiliarity` as a modifier
- The agent parallelism model — launching agents in parallel is correct
- The "no artificial approval gates" principle — gates should only exist when there's genuine blocking uncertainty
- The handoff artifact path convention — `.agents/scratchpad/<feature-name>/handoff-plan.md` is good

---

## Implementation Map (for the skill edits, if you confirm)

| Change                                                | Phase affected                     | Files to edit                         |
| ----------------------------------------------------- | ---------------------------------- | ------------------------------------- |
| Add unfamiliarity heuristic to track selection        | Phase 1, Process Selection section | `SKILL.md`                            |
| Add repo orientation step                             | Phase 2                            | `SKILL.md`                            |
| Split clarifying questions into product vs. technical | Phase 3                            | `SKILL.md`                            |
| Add product-intent acceptance check to review         | Phase 6                            | `SKILL.md`                            |
| Add product context + alignment state sections        | Handoff artifact                   | `references/handoff-plan-template.md` |

No new agents needed. No new phases. All changes are additive within the existing structure.

---

_Ready to proceed with edits once you answer the open questions, or I can proceed with my best assumptions if you'd prefer to see a draft first._
