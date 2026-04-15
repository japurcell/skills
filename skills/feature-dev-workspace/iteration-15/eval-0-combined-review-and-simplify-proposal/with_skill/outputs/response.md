# Evaluation: Combined 'review-and-simplify' Agent Proposal

## Understanding

**Process track**: Light — this is a well-bounded process question with no codebase ambiguity. The answer follows directly from the feature-dev skill's explicit Phase 6 rules.

**Proposal summary**: Replace the two separate Phase 6 subagents (code-simplifier + code-reviewer) with a single combined agent to save time and reduce overhead.

---

## Relevant Findings

Phase 6 of the feature-dev skill specifies the quality review structure with two explicit and distinct mandates:

**1. code-simplifier (Step 1)**
> "Launch independent `code-simplifier` subagents to identify refactoring opportunities after implementation."

Critically, the skill adds:
> "…since each agent **applies edits directly** and overlapping scopes would produce conflicting writes."

The code-simplifier is a **writing agent** — it modifies files on disk.

**2. code-reviewer (Step 2)**
> "Always run **independent** `code-reviewer` agents for quality review on every track."
> "Standard or Deep: launch multiple independent code-reviewer agents in parallel with different focuses such as **simplicity, correctness, and conventions**."

The code-reviewer is a **reading/reporting agent** — it surfaces findings without applying edits.

---

## Recommendation

**The proposal is not acceptable.** Here's why:

### 1. Sequential dependency — simplify must precede review

The code-simplifier edits the code; the code-reviewer should evaluate the post-simplification state. Merging them into one agent collapses this ordering: the agent would review code that it is simultaneously (or previously) rewriting, producing a review of a stale or mid-flight version of the codebase. The whole point of running simplification first is so the reviewer sees the final, cleaned-up form.

### 2. Role conflict: editor vs. auditor

The code-simplifier makes direct writes to files. The code-reviewer reads and reports. Combining them creates an agent that is both judge and rewriter — this undermines the independence the skill explicitly requires. The word "independent" appears for both agents; independence here means each agent has a single, non-overlapping responsibility and does not interfere with the other's output.

### 3. Write-conflict risk at scale

For large changes (>5 changed files), the skill partitions files across multiple code-simplifier agents to prevent conflicting writes. A combined agent reviewing and rewriting the same file it is also "reviewing" reintroduces exactly the conflict the partitioning rule is designed to prevent — especially if the combined agent is run in parallel copies.

### 4. Parallelism is already built in — the overhead savings are marginal

The skill already instructs both agent types to run in parallel. The actual overhead of launching a second agent type is minimal. The perceived "overhead" the developer wants to eliminate is largely illusory; what they would actually eliminate is the correctness guarantee that comes from separating concerns.

### 5. Correctness and simplicity are different review lenses

The code-reviewer explicitly covers **simplicity, correctness, and conventions** as distinct focuses. Simplicity at the review stage is about raising issues; the code-simplifier is about fixing them. Folding refactoring into a review pass risks a muddled output — half finding, half rewrite — that is harder to consolidate and prioritize (Step 3 of Phase 6).

---

## Summary

| Criterion | Separate agents (current) | Combined agent (proposed) |
|-----------|--------------------------|--------------------------|
| Ordering guarantee | ✅ Simplify → then review final code | ❌ Ordering undefined or collapsed |
| Role clarity | ✅ Editor vs. auditor are distinct | ❌ Mixed responsibilities |
| Write-conflict safety | ✅ Explicit partitioning rules apply | ❌ Rules no longer map cleanly |
| Independence | ✅ Explicitly required by skill | ❌ Violated by combination |
| Actual time saved | Marginal (parallel launch is cheap) | Not worth the trade-offs |

The feature-dev skill's Phase 6 structure is intentional. The separation between code-simplifier and code-reviewer is not bureaucratic overhead — it encodes a sequential dependency (edit before review) and a role separation (writer vs. auditor) that together ensure the quality review produces reliable, actionable output. The proposal should be declined.
