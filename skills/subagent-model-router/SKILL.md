---
name: subagent-model-router
description: Routes delegated work to the narrowest capable agent type and cheapest capable model. Use when user wants or mentions a `fast`, `standard`, or `premium` tier model; before every subagent, task, background agent, parallel worker, or `task`-tool launch that still needs `agent_type` or `model` selection, especially for exploration, test execution, grading, code review, debugging, implementation, or research. If a model is pinned or auto-selected, still use this skill to route the remaining choices and state the constraint.
---

# Subagent Model Router

## Overview

Choose smallest agent and cheapest model that can succeed. Default cheap and specialized. Escalate only for a concrete capability, ambiguity, or quality reason.

To optimize token efficiency and minimize context window usage, **lazy-load reference files**:
- Read [`PRICING.md`](PRICING.md) only when the model choice is genuinely ambiguous or if the user/caller explicitly requests cost/pricing details.
- Read [`PATTERNS.md`](PATTERNS.md) only when the classification of the work pattern is highly uncertain or ambiguous.
- Skip reading these files on routine repeats.

## When to Use

- Before any delegated launch where `agent_type`, `model`, or both are still open.
- Especially for exploration, test/build/log execution, grading, code review, debugging, implementation planning, implementation, research, or parallel fan-out.
- If the user or platform already fixed the model, route the remaining choices and note that model control is constrained.
- Do not use this skill when no delegated launch is happening.

## Workflow

### 1. Classify work first

| Class       | Meaning                                           | Examples                                                                             |
| ----------- | ------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **Bounded** | Low ambiguity, repeatable execution or collection | run tests, collect logs, search files, summarize known output, deterministic grading |
| **Focused** | Some judgment, limited scope                      | inspect a diff, trace a bug through a few files, draft a small plan                  |
| **Broad**   | High ambiguity or multi-system synthesis          | architecture design, unclear debugging, multi-file refactoring, tradeoff analysis    |

### 2. Reuse prior routing when context is materially unchanged

Reuse prior routing decision for repeated launches in same launch group or batch when all remain true:

- same work class (`bounded`, `focused`, or `broad`)
- same delegated work shape and specialist lane
- same stakes and ambiguity level
- same model constraints (pinned model, auto-selected model, or open model choice)

When reuse applies, restate reused `agent_type` and model choice/constraint briefly instead of recomputing full routing per launch.

Do fresh routing before launch when any of these changed materially:

- work class or work shape
- stakes (for example routine execution vs high-stakes review)
- ambiguity or reasoning depth needed
- model constraint or availability state

### 3. Pick narrowest capable agent type

| Work type                                  | Prefer                                               |
| ------------------------------------------ | ---------------------------------------------------- |
| Bounded execution                          | `task`                                               |
| Repository search or investigation         | `explore`                                            |
| Diff or PR review                          | `code-review` or comparable review specialist        |
| Open-ended multi-step reasoning or editing | `general-purpose` only when a specialist will not do |

### 4. Map complexity to tier

| Task shape                                                                                 | Tier                            |
| ------------------------------------------------------------------------------------------ | ------------------------------- |
| Bounded / simple                                                                           | **Fast**                        |
| Focused / moderate                                                                         | **Standard**                    |
| Broad / complex                                                                            | high end of **Standard** first  |
| Repeated lower-tier failure, unusually high stakes, or best-available reasoning by request | **Premium**, with justification |

### 5. Pick cheapest suitable model inside that tier

Compare:

- input cost
- output cost
- cached input cost
- Anthropic cache write, when relevant
- task fit
- availability

Use token shape:

- large read / short answer -> optimize for **input** cost
- short prompt / long answer -> optimize for **output** cost
- repeated context -> consider **cached input**
- Anthropic cached context -> include **cache write**

If first choice is unavailable, or if a subagent launch/API call fails with a model support or access error (such as `400 model gpt-4.1 is not supported via Responses API`, 403, 404, or similar error indicating model/endpoint issues):

1. **NEVER fall back to executing the complex or delegated work directly yourself.** Fallback to manual execution wastes token budget and context window capacity.
2. **Stay in the same tier** and choose the next cheapest suitable model in that tier (e.g., switch from `gpt-4.1` to `gpt-5.3-codex`, `gemini-3.1-pro`, or `sonnet` in the standard tier).
3. do **not** change tiers while a same-tier fallback exists.
4. if the whole tier is unavailable, move one tier lower for bounded work or one tier higher for reasoning-heavy work.
5. **Retry the subagent launch** with the new fallback model. Keep trying alternative models within the same tier until a model successfully executes.
6. if availability or a launch error forced a tier change, say so in one sentence.

### 6. Escalate only for a concrete reason

Move up one tier only when:

- the task spans many files, systems, or concepts
- instructions are ambiguous enough that a weaker model is likely to thrash
- a cheaper run already failed for a capability reason
- the user explicitly prioritizes maximum quality over speed and cost
- the task is unusually high-stakes and subtle errors are costly

If you cannot justify the stronger model in one sentence, do not use it.

## Specific Techniques

### Tier guide

Route by task fit, availability, and current pricing, not brand reputation. Models below are examples; only choose from models the environment actually offers.

| Tier         | Use for                                                                                       | Typical models                                                                                   |
| ------------ | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| **Fast**     | bounded execution, collection, deterministic grading, small non-code transforms               | `gpt-5-mini`, `gpt-5.4-mini`, `gpt-5.4-nano`, `gemini-3.1-flash-lite`, `gemini-3-flash`, `haiku` |
| **Standard** | cross-file reading, judgment, debugging, code review, non-trivial code edits                  | `gpt-5.3-codex`, `gpt-4.1`, `gemini-3.5-flash`, `gemini-3.1-pro`, `gpt-5.4`, `sonnet`            |
| **Premium**  | repeated lower-tier failure, subtle high-stakes analysis, best-available reasoning by request | `gpt-5.5`, `opus`                                                                                |

### Code editing exception

- Use fast-tier editing only for very small isolated changes with clear acceptance criteria.
- Use standard tier for cross-file reasoning, debugging, refactoring, or design-sensitive edits.

### Decision shape

Provide the routing decision in one of two formats based on requested verbosity:

#### Compact Output Mode (Default)
By default, return exactly one line formatted as:
`agent_type | model | tier | reason`
Do not output any markdown headings, lists, verbose reasoning, or conversational preamble unless specifically requested.

#### Verbose Mode (Explicitly Requested)
If the user or caller explicitly requests a detailed justification or passes a `verbose` flag/intent, return:
- chosen `agent_type`
- chosen model or constrained-model note
- tier
- one-sentence justification for any escalation or availability fallback

## Common Rationalizations

| Rationalization                                                                                           | Reality                                                                                       |
| --------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| "It is only a test runner; use the strongest model to be safe."                                           | Bounded execution should start with `task` plus a fast-tier model.                            |
| "First-choice model is unavailable, so drop a tier immediately."                                          | Stay in the same tier until same-tier options are exhausted.                                  |
| "User pinned the model, so this skill is irrelevant."                                                     | Route the remaining choices and state that model control is constrained.                      |
| "The API returned a 400 'model not supported' error when launching, so I should just do the work myself." | Do NOT fall back to manual execution. Switch models within the same tier and retry launching. |

## Red Flags

Avoid:

- using this skill when no delegated launch exists
- choosing a premium model before classifying the task
- using the same strong model for test runners, search agents, reviewers, and editors
- choosing `general-purpose` when a specialized agent can do the work
- escalating after vague dissatisfaction instead of a concrete capability gap
- ignoring token shape and choosing only by model reputation
- dropping tiers while same-tier fallback exists
- ignoring the code-editing exception
- treating an auto-selected model as a reason to skip agent routing
- using stale pricing when current pricing is available
- falling back to manual/direct execution of a complex delegated task because a subagent launch failed with a model support or API error
- reading or loading `PRICING.md` or `PATTERNS.md` unconditionally on routine routing requests
- outputting verbose reasoning or multiple lines by default when compact output mode is expected

## Verification

Before launch, confirm:

- [ ] The work was classified as bounded, focused, or broad.
- [ ] Prior routing was reused only when launch-group context was materially unchanged.
- [ ] The chosen agent type is the narrowest capable type.
- [ ] The selected tier matches task complexity.
- [ ] The selected model is the cheapest suitable available option in that tier, or the model constraint was stated.
- [ ] Input/output token mix was considered when relevant.
- [ ] Cached input and Anthropic cache write were considered when relevant.
- [ ] Same-tier fallback was preferred when the first-choice model was unavailable.
- [ ] Fallback and retry strategy is prepared if the chosen model fails with an API/support error (e.g., 400 not supported).
- [ ] Any escalation or availability-driven tier change has a concrete one-sentence justification.
- [ ] Fresh routing was done when work class, stakes, ambiguity, or model constraints changed materially.
- [ ] The code editing exception was checked.
- [ ] Pricing matched the current source of truth when exact cost mattered.
- [ ] Reference files `PRICING.md` and `PATTERNS.md` were lazy-loaded (only read if model choice was ambiguous or cost details were requested).
- [ ] Output conforms to the single-line compact format (`agent_type | model | tier | reason`) by default.
