---
name: subagent-model-router
description: Chooses the narrowest capable subagent type and cheapest capable model for delegated work. Use whenever you are about to launch, spawn, delegate to, or set `model:` for a subagent, task agent, background agent, or parallel worker. Use this before any task-tool launch that needs model selection, especially for exploration, test execution, grading, code review, debugging, implementation, or implementation research.
---

# Subagent Model Router

Before delegated work, choose:

1. the **narrowest capable agent type**
2. the **cheapest capable model**

Default to cheaper, faster models for bounded work. Escalate only for a concrete reason. When pricing is available, route by actual token cost, not intuition.

For current prices, see [`PRICING.md`](PRICING.md).  
For common routing examples, see [`PATTERNS.md`](PATTERNS.md).

## When to Use

Use this skill when you are about to launch a subagent, task agent, background agent, parallel worker, or task-tool call and must decide:

- `agent_type`
- `model`
- both `agent_type` and `model`

Especially use it for:

- repository exploration
- test execution
- grading or validation
- code review
- debugging
- implementation planning
- implementation research
- parallel worker launches

Do **not** use this skill when:

- no subagent is being launched
- the user explicitly pinned the model
- the platform fixes or auto-selects the model

## Core Process

### 1. Classify the delegated work

Classify the task before choosing a model.

| Class       | Meaning                                                   | Examples                                                                                  |
| ----------- | --------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **Bounded** | Low ambiguity, repeatable, mostly execution or collection | run tests, collect logs, search files, summarize known output, deterministic grading      |
| **Focused** | Some judgment, limited scope                              | inspect a diff, trace a bug through a few files, draft a small plan, review one component |
| **Broad**   | High ambiguity, synthesis, or multi-system reasoning      | architecture design, unclear debugging, multi-file refactoring, tradeoff analysis         |

### 2. Pick the narrowest capable agent type

Prefer specialized agents when possible. Specialized agents often allow a cheaper model.

| Work type                                  | Prefer                                |
| ------------------------------------------ | ------------------------------------- |
| Bounded execution                          | `task`                                |
| Repository search or investigation         | `explore`                             |
| Diff or PR review                          | `code-review` or similar reviewer     |
| Open-ended multi-step reasoning or editing | `general-purpose` only when necessary |

### 3. Map complexity to a model tier

| Task complexity                                             | Default tier                         |
| ----------------------------------------------------------- | ------------------------------------ |
| Bounded / Simple                                            | **Fast**                             |
| Focused / Moderate                                          | **Standard**                         |
| Broad / Complex                                             | **Strong standard**                  |
| Creative, high-stakes, or repeatedly failed lower-tier work | **Premium**, only with justification |

### 4. Choose the cheapest suitable model within the tier

Within the chosen tier, compare:

- input cost
- output cost
- cached input cost
- Anthropic cache write cost, when relevant
- task fit
- model availability

Use token shape:

- large read / short answer -> optimize for **input** cost
- short prompt / long answer -> optimize for **output** cost
- repeated context -> consider **cached input**
- Anthropic cached context -> include **cache write**

If the selected model is unavailable:

1. choose the next cheapest suitable model in the same tier
2. do **not** drop to a lower tier while a suitable same-tier fallback exists
3. if the whole tier is unavailable, move one tier lower for bounded work or one tier higher for reasoning-heavy work
4. if availability forced a tier change, say so in one sentence

### 5. Escalate only for a concrete reason

Move up one tier only when:

- the task spans many files, systems, or concepts
- instructions are ambiguous enough that a weaker model is likely to thrash
- a cheaper run already failed for a capability reason
- the user explicitly prioritizes maximum quality over speed and cost
- the task is unusually high-stakes and subtle errors are costly

If you cannot justify the stronger model in one sentence, do not use it.

## Model Tier Guide

Route by **task fit, availability, and cost**, not vendor marketing labels.

### Fast tier

Use first for bounded, repeatable, low-ambiguity work.

- `gpt-5-mini`
- `gemini-3-flash`
- `gpt-5.4-mini`
- `gpt-5.4-nano`
- `haiku`

### Standard tier

Use when the task needs judgment, cross-file reading, moderate ambiguity, or code editing beyond a very small isolated change.

- `gpt-5.3-codex`
- `gpt-4.1`
- `gemini-3.1-pro`
- `gpt-5.4`
- `sonnet`

### Premium tier

Use only when complexity or quality needs clearly justify the cost.

- `opus`
- `gpt-5.5`

## Code Editing Exception

Do **not** recommend `gpt-5-mini` for code editing tasks.

For code editing:

- use another suitable fast-tier model only for very small, isolated edits with clear acceptance criteria
- use a standard-tier model when the edit requires judgment, cross-file reasoning, debugging, refactoring, or design awareness

## Red Flags

Avoid:

- choosing a premium model before classifying the task
- using the same strong model for test runners, search agents, reviewers, and editors
- choosing `general-purpose` when a specialized agent can do the work
- escalating after vague dissatisfaction instead of a concrete capability gap
- ignoring token shape and choosing only by model reputation
- dropping to a lower tier when a suitable same-tier fallback is available
- using stale pricing when current pricing is available

## Verification Checklist

Before launch, confirm:

- [ ] The work was classified as bounded, focused, or broad.
- [ ] The chosen agent type is the narrowest capable type.
- [ ] The selected tier matches task complexity.
- [ ] The selected model is the cheapest suitable model in that tier.
- [ ] Availability was checked.
- [ ] Same-tier fallback was preferred when the first-choice model was unavailable.
- [ ] Input/output token mix was considered when relevant.
- [ ] Cached input and Anthropic cache write were considered when relevant.
- [ ] Any escalation has a concrete one-sentence justification.
- [ ] Premium models are reserved for exceptional cases.
- [ ] The code editing exception was checked.
- [ ] Pricing matches the current source of truth.
