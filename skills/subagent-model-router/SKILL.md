---
name: subagent-model-router
description: Chooses the least powerful subagent model that can reliably finish delegated work. Use whenever you are about to launch, spawn, delegate to, or set `model:` for a subagent, task agent, background agent, or parallel worker. Use this before any task-tool launch that needs model selection, especially for exploration, test execution, grading, code review, debugging, or implementation research where a fast cheap model often suffices.
---
# Subagent Model Router

## Overview
Before delegated work, choose:
1. the **narrowest capable agent type**
2. the **cheapest capable model**

Default to cheaper/faster models for bounded work. Escalate only for a concrete reason. When pricing is available, route by actual token cost, not intuition.

## When to Use
- Use when you are about to call the task tool and must decide `agent_type`, `model`, or both.
- Use when launching several agents in parallel and you want to avoid defaulting all of them to a strong model.
- Use when a task could fit either a specialized agent plus a cheap model or a general-purpose agent plus a stronger model.
- Use when you are tempted to choose a stronger model "just to be safe."
- Do **not** use when no subagent is being launched.
- Do **not** override the model when the user explicitly pinned it or the platform fixes it.

## Core Process
1. **Classify the delegated work.**
   - **Bounded:** run tests, collect logs, search files, summarize known output, deterministic grading
   - **Focused:** inspect a diff, trace a bug through a few files, draft a small plan, review one component
   - **Broad:** synthesize across many files, design architecture, debug unclear failures, analyze tradeoffs

2. **Pick the narrowest capable agent type.**
   Specialized agents often allow a cheaper model.
   - `task` or `explore` for bounded execution and research
   - `code-review` or similar reviewer for diff analysis
   - `general-purpose` only when open-ended multi-step reasoning or editing is truly needed

3. **Map complexity to a tier.**
   - **Bounded / Simple** -> **Fast tier**
   - **Focused / Moderate** -> **Standard tier**
   - **Broad / Complex** -> **Strong standard**, or **Premium** only if clearly justified

4. **Within the tier, prefer the cheapest available model that fits the task.**
   - Consider token shape when pricing differs by input, output, cached input, or cache write.
   - If the selected model is unavailable, choose the next cheapest suitable model in the same tier.
   - Do **not** drop to a lower tier while a suitable model in the chosen tier is available.
   - If the whole tier is unavailable, move to the nearest tier:
     - prefer one tier lower for bounded/tightly scoped work
     - prefer one tier higher for focused/broad reasoning-heavy work
   - If availability forces a tier change, say so in one sentence.

5. **Escalate only for a concrete reason.**
   Move up one tier only when:
   - the task spans many files or systems and requires synthesis
   - instructions are ambiguous enough that a weaker model will likely thrash
   - a cheaper run already failed for a capability reason
   - the user explicitly prioritizes maximum quality over speed and cost

6. **If you cannot justify the stronger model in one sentence, do not use it.**
   - Good: "This agent must reconcile conflicting behavior across three services and propose an architecture change."
   - Bad: "This is important." / "A stronger model is safer."

7. **Launch, then learn.**
   Reuse cheap models that worked. If one fails for a clear capability reason, escalate one step, not straight to the strongest model.

## Routing Rules
Routing depends on **task fit, availability, and cost**, not vendor labels like "Lightweight," "Versatile," or "Powerful."

| Task complexity | Route to | Examples |
|---|---|---|
| Simple | Cheapest suitable fast-tier model | File renaming, simple search, format conversion, status checks |
| Moderate | Cheapest suitable standard-tier model | Code review, test writing, refactoring, documentation |
| Complex | Strong suitable standard-tier model; premium only if justified | Architecture design, subtle debugging, multi-file refactoring |
| Creative / high-stakes | Premium only with explicit justification | Novel algorithms, critical security review, broad system design |

## Pricing Fundamentals
Model pricing is token-based:
- cost may include **input**, **output**, **cached input**, and for Anthropic sometimes **cache write**
- prices may be shown in **GitHub AI Credits**, where **1 credit = $0.01 USD**
- total cost depends on both **model** and **token volume**

### Cost heuristics
- Prefer the lowest **combined input + output** cost that still meets the task's reasoning needs.
- If the agent will read a lot and write little, optimize for **input** cost.
- If it will generate long responses, optimize for **output** cost.
- If it will reuse large context, consider **cached input** cost.
- For Anthropic models, include **cache write** cost when relevant.
- Do not pay premium rates for bounded execution work.
- When two models are close in price, prefer the one that better fits the task.

## Pricing Reference
All prices below are **per 1 million tokens**.

### OpenAI
| Model | Status | Category | Input | Cached input | Output |
|---|---|---|---:|---:|---:|
| GPT-4.1 | GA | Versatile | $2.00 | $0.50 | $8.00 |
| GPT-5 mini | GA | Lightweight | $0.25 | $0.025 | $2.00 |
| GPT-5.3-Codex | GA | Powerful | $1.75 | $0.175 | $14.00 |
| GPT-5.4 | GA | Versatile | $2.50 | $0.25 | $15.00 |
| GPT-5.4 mini | GA | Lightweight | $0.75 | $0.075 | $4.50 |
| GPT-5.4 nano | GA | Lightweight | $0.20 | $0.02 | $1.25 |
| GPT-5.5 | GA | Powerful | $5.00 | $0.50 | $30.00 |

### Anthropic
| Model | Status | Category | Input | Cached input | Cache write | Output |
|---|---|---|---:|---:|---:|---:|
| Haiku | GA | Versatile | $1.00 | $0.10 | $1.25 | $5.00 |
| Sonnet | GA | Versatile | $3.00 | $0.30 | $3.75 | $15.00 |
| Opus | GA | Powerful | $5.00 | $0.50 | $6.25 | $25.00 |

### Google
| Model | Status | Category | Input | Cached input | Output |
|---|---|---|---:|---:|---:|
| Gemini 3 Flash | Public preview | Lightweight | $0.50 | $0.05 | $3.00 |
| Gemini 3.1 Pro | Public preview | Powerful | $2.00 | $0.20 | $12.00 |
| Gemini 3.5 Flash | GA | Lightweight | $1.50 | $0.15 | $9.00 |

## Practical Cost Tiers
Use exact pricing when possible; these tiers are shortcuts.

### Fast tier
Use first for bounded, repeatable, low-ambiguity work.

| Model | Input | Output | Notes |
|---|---:|---:|---|
| GPT-5.4 nano | $0.20 | $1.25 | Cheapest listed |
| GPT-5 mini | $0.25 | $2.00 | Low-cost general option |
| Gemini 3 Flash | $0.50 | $3.00 | Lightweight, preview |
| GPT-5.4 mini | $0.75 | $4.50 | Stronger lightweight option |
| Haiku | $1.00 | $5.00 | Fast reasoning, pricier than mini/nano |

### Standard tier
Use when the task needs judgment, cross-file reading, or moderate ambiguity.

| Model | Input | Output | Notes |
|---|---:|---:|---|
| GPT-5.3-Codex | $1.75 | $14.00 | Often cheapest standard-tier input; strong for coding |
| GPT-4.1 | $2.00 | $8.00 | Lower output cost; versatile |
| Gemini 3.1 Pro | $2.00 | $12.00 | Powerful, preview |
| GPT-5.4 | $2.50 | $15.00 | Versatile |
| Sonnet | $3.00 | $15.00 | Strong reasoning |

### Premium tier
Use only when complexity or quality needs justify the cost.

| Model | Input | Output | Notes |
|---|---:|---:|---|
| Opus | $5.00 | $25.00 | Premium Anthropic tier |
| GPT-5.5 | $5.00 | $30.00 | Highest listed OpenAI cost |

## Selection Patterns
### Cheap by default
Use the fast tier for:
- running tests, builds, lint, or scripts and reporting results
- searching the codebase and listing candidate files
- summarizing logs, command output, or benchmark artifacts
- deterministic checks, grading, or fixture comparisons
- small isolated refactors with clear acceptance criteria

Recommended starting models:
- `gpt-5.4-nano`
- `gpt-5-mini`
- `gemini-3-flash`
- `gpt-5.4-mini`
- `haiku`

### Standard when reasoning dominates
Use the standard tier for:
- debugging across multiple files
- writing or revising a design with meaningful tradeoffs
- implementing a non-trivial change across connected files
- reviewing a large diff that depends on architectural context
- code review where judgment matters more than simple collection

Recommended starting models:
- `gpt-5.3-codex`
- `gpt-4.1`
- `gemini-3.1-pro`
- `gpt-5.4`
- `sonnet`

### Premium only when you can defend it
Reserve the premium tier for:
- repeated failure at lower tiers
- unusually high-stakes analysis where subtle reasoning errors are costly
- very broad or novel tasks where the user explicitly wants best-available reasoning despite the expense

Recommended starting models:
- `opus`
- `gpt-5.5`

## Examples
- "Spawn three agents to search the repo for where auth tokens are created, refreshed, and revoked."  
  -> Use focused `explore`-style agents on a fast-tier model such as `gpt-5.4-nano`, `gpt-5-mini`, `gpt-5.4-mini`, or `haiku`.

- "Launch a reviewer to inspect this 40-file security-sensitive diff for auth and data exposure bugs."  
  -> Use a review-focused agent on a standard-tier model such as `gpt-5.3-codex`, `gpt-4.1`, or `sonnet`; escalate only if unusually deep cross-system reasoning is needed.

- "Launch a reviewer to inspect a medium-sized diff, and `gpt-4.1` is unavailable."  
  -> Keep the task in the standard tier and choose another available standard-tier model such as `gpt-5.3-codex`, not a fast-tier model like `gpt-5-mini`.

- "Have a subagent run the test suite and summarize the failures."  
  -> Use a `task` agent on a fast-tier model.

- "Have a subagent read a very large log bundle and produce a short diagnosis."  
  -> Prefer a model with low **input** cost.

- "Have a subagent draft a long architecture proposal from a short prompt."  
  -> Prefer strong reasoning, but compare **output** cost because generation volume may dominate.

## Special Cases
- If the platform auto-selects the model, do not pretend precise per-model cost control is available.
- Public preview models may change behavior, pricing, or availability more often than GA models.
- Long-context pricing may differ from base rates; check current documentation when relevant.
- The cheapest model within a tier can vary by token mix, so use exact pricing when available.
- Do not equate vendor labels like "Powerful" or "Lightweight" with this skill's routing tiers.

## Common Rationalizations
| Rationalization | Reality |
|---|---|
| "A stronger model is safer." | It is often slower and more expensive without helping bounded tasks. |
| "The task is important, so use the best model." | Importance is not the same as complexity. |
| "I don't know how hard it is yet." | Start cheap when the task is bounded; escalate only after evidence. |
| "I'm already using a general-purpose agent, so I might as well use a strong model too." | First ask whether a specialized agent would lower both risk and cost. |
| "The user didn't mention cost." | Cost and speed still matter unless the user explicitly deprioritizes them. |
| "Parallel agents should all use the same model for consistency." | Match the model to each agent's job; uniform overprovisioning is wasteful. |

## Red Flags
- reaching for a premium model before classifying the task
- using the same strong model for test runners, search agents, and reviewers alike
- choosing `general-purpose` for work a specialized agent can do
- escalating after vague dissatisfaction instead of a concrete capability gap
- omitting the reason for a stronger model because it would sound weak
- ignoring token shape and choosing only by model reputation
- dropping to a lower tier when a suitable same-tier fallback is available
- treating the first named model in a tier as mandatory
- confusing vendor capability labels with this skill's routing tiers

## Verification
After choosing a subagent model, confirm:
- [ ] The work was classified as bounded, focused, or broad before model selection.
- [ ] The chosen agent type is the narrowest one that can do the job.
- [ ] The selected model is the cheapest reasonable tier for that work.
- [ ] Within that tier, the exact model choice considered fit, availability, and major pricing differences.
- [ ] If the first-choice model was unavailable, fallback stayed within the selected tier when possible.
- [ ] Input/output token mix, cached input, and Anthropic cache write were considered when relevant.
- [ ] Any move above the fast tier has a concrete reason tied to complexity, ambiguity, prior failure, or explicit user priority.
- [ ] Premium models are reserved for exceptional cases, not used by default.
- [ ] The pricing table matches the current source of truth.