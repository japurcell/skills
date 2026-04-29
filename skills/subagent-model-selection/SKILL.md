---
name: subagent-model-selection
description: Chooses the least powerful subagent model that can reliably finish the delegated work. Use whenever you are about to launch, spawn, delegate to, or set `model:` for a subagent, task agent, background agent, or parallel worker. Make sure to use this skill before any task-tool launch that needs model selection, especially for exploration, test execution, grading, code review, debugging, or implementation research where a fast cheap model often suffices.
---

# Subagent Model Selection

## Overview

Pick the narrowest capable agent and the cheapest capable model before launching delegated work. This keeps parallel work fast, reduces token cost, and prevents wasting premium reasoning on bounded tasks that a smaller model could finish just as well.

## When to Use

- Use when you are about to call the task tool and must decide `agent_type`, `model`, or both.
- Use when you are launching several agents in parallel and want to avoid defaulting all of them to a strong model.
- Use when a task could fit either a specialized agent plus cheap model or a general-purpose agent plus stronger model.
- Use when you are tempted to choose a stronger model "just to be safe."
- Do **not** use when no subagent is being launched.
- Do **not** override the model when the user explicitly pinned a model or the platform fixes it for you.

## Core Process

1. **Classify the delegated work before picking a model.**
   Decide what the agent actually needs to do:
   - Bounded execution: run tests, collect logs, search files, summarize known output, do deterministic grading.
   - Focused reasoning: inspect a diff, trace a bug through a few files, draft a small plan, review one component.
   - Broad reasoning: synthesize across many files, design architecture, debug unclear failures, perform nuanced tradeoff analysis.

2. **Pick the narrowest capable agent type first.**
   Prefer specialized agents over general-purpose ones because the right agent often lowers the model requirement too.
   - `task` or `explore` for bounded execution and research.
   - `code-review` or a focused reviewer for diff analysis.
   - `general-purpose` only when the work genuinely needs open-ended multi-step reasoning or editing.

3. **Start from the cheapest reasonable model tier.**

   ```
   Simple, bounded, repeatable work
       -> fast tier: haiku / mini / 4.1
   Multi-file reasoning or moderate ambiguity
       -> standard tier: sonnet / GPT-5.x standard
   Exceptional complexity, repeated failure, or explicit premium-quality ask
       -> premium tier: opus / GPT-5.5
   ```

   In current environments, the fast tier commonly includes models such as `claude-haiku-4.5`, `gpt-5.4-mini`, `gpt-5-mini`, or `gpt-4.1`.

4. **Escalate only for a concrete reason.**
   Move up one tier only when at least one of these is true:
   - The task spans many files or systems and depends on synthesis, not just collection.
   - The instructions are ambiguous enough that weak reasoning will likely thrash.
   - A cheaper run already failed or produced clearly inadequate work.
   - The user explicitly prioritizes maximum quality over speed and cost.

5. **If you cannot justify the stronger model in one sentence, do not use it.**
   Good justification: "This agent must reconcile conflicting behavior across three services and propose an architecture change."
   Bad justification: "This is important" or "Sonnet is safer."

6. **Launch, then learn.**
   If a cheap model succeeds, keep it cheap for similar follow-up work. If it fails for a clear capability reason, escalate one step rather than jumping straight to the strongest model.

## Selection Patterns

### Cheap by default

Use the fast tier for work like:

- Running tests, builds, lint, or scripts and reporting the result
- Searching the codebase and listing candidate files
- Summarizing logs, command output, or benchmark artifacts
- Deterministic checks, grading, or fixture comparisons
- Small isolated refactors with clear acceptance criteria

### Standard tier when reasoning dominates

Use the standard tier for work like:

- Debugging an issue that requires tracing behavior across multiple files
- Writing or revising a design with meaningful tradeoffs
- Implementing a non-trivial change where the agent must read, edit, and validate several connected files
- Reviewing a large diff where correctness depends on architectural context

### Premium only when you can defend it

Reserve the premium tier for cases like:

- Repeated failure at lower tiers on the same task
- Unusually high-stakes analysis where subtle reasoning errors are costly
- Very broad or novel tasks where the user explicitly wants best-available reasoning despite the expense

## Examples

**Example 1:**
Input: "Spawn three agents to search the repo for where auth tokens are created, refreshed, and revoked."
Output: Use `explore` or similar focused agents on a fast-tier model.

**Example 2:**
Input: "Launch a reviewer to inspect this 40-file security-sensitive diff for auth and data exposure bugs."
Output: Use a review-focused agent on a standard-tier model; escalate only if the review needs unusually deep cross-system reasoning.

**Example 3:**
Input: "Have a subagent run the test suite and summarize the failures."
Output: Use a `task` agent on a fast-tier model.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "A stronger model is safer." | It is often slower and more expensive without improving bounded execution tasks. |
| "The task is important, so use the best model." | Importance does not equal complexity. Pick for reasoning demand, not emotional weight. |
| "I don't know how hard it is yet." | Start cheap when the task is bounded; escalate only after evidence. |
| "I'm already using a general-purpose agent, so I might as well use a strong model too." | First ask whether a specialized agent would lower both risk and cost. |
| "The user didn't mention cost." | Cost and speed are still engineering constraints unless the user explicitly deprioritizes them. |
| "Parallel agents should all use the same model for consistency." | Match the model to each agent's job; uniform overprovisioning is wasteful. |

## Red Flags

- Reaching for a premium model before classifying the task
- Using the same strong model for test runners, search agents, and reviewers alike
- Choosing `general-purpose` for work that a specialized agent can do
- Escalating after vague dissatisfaction instead of a concrete capability gap
- Omitting the reason for a stronger model because the reason would sound weak

## Verification

After choosing a subagent model, confirm:

- [ ] The delegated work was classified as bounded, focused, or broad before model selection
- [ ] The chosen agent type is the narrowest one that can do the job
- [ ] The selected model is the cheapest reasonable tier for that work
- [ ] Any move above the fast tier has a concrete reason tied to complexity, ambiguity, prior failure, or explicit user priority
- [ ] Premium models are reserved for exceptional cases, not used by default
