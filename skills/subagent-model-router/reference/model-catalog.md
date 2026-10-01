# Model Catalog

Use this catalog after determining the task's capability floor.

Sources:

- [Supported AI models in GitHub Copilot](https://docs.github.com/en/copilot/reference/ai-models/supported-models)
- [AI model comparison](https://docs.github.com/en/copilot/reference/ai-models/model-comparison)
- [GitHub Copilot models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)

Verified **2026-09-29**.

This catalog contains routing candidates derived from the cited sources. A pricing or comparison entry alone does not establish runtime availability. Absence from this catalog does not establish retirement.

Model IDs below are routing shorthand. Always use the exact identifier and reasoning-effort value accepted by the target dispatch interface.

## Catalog descriptions versus dispatch values

Catalog effort descriptions define eligible configurations or ranges. They are not necessarily exact dispatch values.

Before returning a router result:

1. inspect the values accepted by the current dispatch interface
2. resolve the selected catalog configuration to one exact model ID
3. resolve the selected effort description to one exact effort value
4. do the same for any fallback
5. return `dispatchable: false` if exact values cannot be confirmed

Do not copy descriptive phrases such as these into a dispatchable route:

- “runtime-supported”
- “lower or medium”
- “Standard effort”
- “high or greater”
- “strongest available”
- “when applicable”

Configured, inherited, or runtime defaults do not resolve these descriptions unless the user explicitly requested those defaults and the dispatch interface accepts the resulting values explicitly.

## How to read the catalog

Routing tiers are local capability classifications, not provider labels.

A tier applies to a **model-and-effort configuration**, not necessarily to an entire model family. A model may appear in more than one tier when different reasoning-effort settings produce materially different routing configurations.

Before launching:

1. establish the task floor
2. identify a configuration listed for that tier
3. confirm that the dispatch interface exposes the exact model
4. choose one exact supported reasoning-effort value that satisfies the listed configuration
5. apply the same-tier fallback policy if the selected configuration is unavailable

Use [`pricing.md`](pricing.md) when exact cost matters.

## Fast configurations

Use only when the task floor established by `SKILL.md` is Fast.

| Provider | Model and eligible effort | Status | Best for |
| --- | --- | --- | --- |
| OpenAI | `gpt-5.4-nano`; exact supported Fast effort | GA; Codex VS Code extension and Copilot Pro+ only | Lightweight work without cache-write charges; unavailable in Copilot Chat |
| OpenAI | `gpt-5-mini`; exact supported Fast effort | GA | Fast coding and writing; mechanical or style-only review |
| OpenAI | `gpt-5.6-luna`; lower or medium supported effort | GA | Bounded, low-risk coding with clear requirements; fallback for GPT-6 Luna |
| OpenAI | `gpt-6-luna`; `medium` effort | GA | Bounded, low-risk coding with clear requirements; verify output |
| Anthropic | `claude-haiku-4.5`; exact supported Fast effort | GA | Simple or repetitive tasks |
| Google | `gemini-3.5-flash`; exact supported Fast effort | GA; retires 2026-10-02 | Fast, simple work |
| Microsoft | `mai-code-1.1-flash`; exact supported Fast effort | GA | Lower-cost lightweight code work |

Fast review is limited to mechanical, generated, formatting, comment-only, or similarly non-semantic changes with straightforward verification.

Substantive review is at least Standard regardless of file count.

## Standard configurations

Use when the task floor established by `SKILL.md` or [`review-routing.md`](review-routing.md) is Standard.

| Provider | Model and eligible effort | Status | Best for |
| --- | --- | --- | --- |
| OpenAI | `gpt-5.6-luna`; `max` effort | GA | Cost-conscious agentic coding or ordinary bounded review when demonstrated to fit |
| OpenAI | `gpt-6-luna`; `max` effort | GA | Cost-conscious agentic coding and ordinary bounded review; verify task fit |
| OpenAI | `gpt-5.4-mini`; exact supported Standard effort | GA | Bounded substantive code review |
| OpenAI | `gpt-6.1-sol`; exact supported Standard effort | GA | Connected or complex coding, efficient reasoning, and broader analysis; lower cached-input rates than GPT-6 Sol |
| OpenAI | `gpt-6-sol`; exact supported Standard effort | GA | Interactive and agentic coding; fallback for GPT-6.1 Sol |
| OpenAI | `gpt-5.6-terra`; exact supported Standard effort | GA | Connected coding and broader analysis; long-context pricing |
| OpenAI | `gpt-5.3-codex`; exact supported Standard effort | GA | Agentic coding and review with demonstrated task fit |
| Anthropic | `claude-sonnet-5.5`; exact supported Standard effort | GA | General coding and agent tasks with fewer steps and tool calls; fallback to `claude-sonnet-5` when unavailable |
| Moonshot AI | `kimi-k2.7-code`; exact supported Standard effort | GA; retires 2026-10-02 | Code-oriented versatile work |
| Google | `gemini-3.6-flash`; exact supported Standard effort | GA; retires 2026-10-02 | Versatile work; promotional pricing |
| Google | `gemini-3.7-flash`; exact supported Standard effort | GA | Versatile work; promotional pricing |
| Google | `gemini-3.8-flash`; exact supported Standard effort | GA | Versatile work; promotional pricing |
| xAI | `grok-4.5`; exact supported Standard effort | GA | Versatile work; long-context pricing |
| xAI | `grok-4.6`; exact supported Standard effort | GA | Versatile work; long-context pricing |
| xAI | `grok-4.7`; exact supported Standard effort | GA | Agentic coding; long-context pricing |

## Premium configurations

Use when the task floor established by `SKILL.md` or [`review-routing.md`](review-routing.md) is Premium.

| Provider | Model and eligible effort | Status | Best for |
| --- | --- | --- | --- |
| OpenAI | `gpt-6.1-sol`; `high` or stronger supported effort | GA | Demanding code or security review when demonstrated to fit |
| OpenAI | `gpt-6-sol`; `high` or stronger supported effort | GA | Demanding code or security review; fallback for GPT-6.1 Sol |
| OpenAI | `gpt-5.6-terra`; `high` or stronger supported effort | GA | Demanding connected-code analysis when demonstrated to fit |
| OpenAI | `gpt-5.3-codex`; strongest suitable supported effort | GA | Demanding agentic coding or review when demonstrated to satisfy the Premium floor |
| OpenAI | `gpt-5.4`; exact supported Premium effort | GA | Broad, difficult general work; long-context pricing |
| OpenAI | `gpt-5.5`; exact supported Premium effort | GA | Powerful reasoning; long-context pricing |
| OpenAI | `gpt-6-astra`; exact supported Premium effort | GA | Powerful reasoning and demanding autonomous work; long-context pricing |
| Anthropic | `claude-opus-4.7`; exact supported Premium effort | GA; retires 2026-10-02 | Deep reasoning and debugging |
| Anthropic | `claude-opus-4.8`; exact supported Premium effort | GA | Deep reasoning and debugging |
| Anthropic | `claude-opus-4.8-fast`; exact supported Premium effort | GA | Premium reasoning when speed justifies cost |
| Anthropic | `claude-fable-5`; exact supported Premium effort | GA | Long-horizon autonomous coding and knowledge work |
| Anthropic | `claude-opus-5`; exact supported Premium effort | GA | Powerful reasoning |
| Anthropic | `claude-opus-5.5`; exact supported Premium effort | GA | Long-running agentic coding and knowledge work |
| Anthropic | `claude-fable-5.1`; exact supported Premium effort | GA | Long-horizon autonomous coding and knowledge work; low cached-input rate |
| Moonshot AI | `kimi-k3`; exact supported Premium effort | GA | Multi-step agentic coding across large contexts |

A Premium configuration must be confirmed by the current dispatch interface.

If a listed effort range is eligible, choose one exact accepted value from that range. Do not copy the range into the router output.

If an eligible effort is unavailable, do not assume the same model at a lower effort still satisfies the Premium floor.

## Task defaults

These defaults are provisional starting candidates, not measured quality rankings.

They follow GitHub task guidance and the pricing snapshot. Prefer task-specific evaluations or demonstrated materially similar performance when those disagree with a default.

Every starting configuration and fallback must be resolved to an exact model and exact reasoning-effort value before it is returned by the router.

| Default | Tier | Starting configuration | Alternatives and conditions |
| --- | --- | --- | --- |
| Bounded work | Fast | `gpt-6-luna` with `medium` effort | Includes low-risk coding changes with clear requirements and mechanical review. If unavailable, use `gpt-5.6-luna` with one exact eligible Fast effort. Use `mai-code-1.1-flash` if neither Luna configuration is available. |
| Budget review | Standard | `gpt-6-luna` with `max` effort | For ordinary bounded substantive diffs with clear scope. If unavailable, use another exact Standard review configuration. Use the general-work default for broader behavioral review. |
| General work | Standard | `gpt-6.1-sol` with one exact supported Standard effort | For interactive or agentic coding, substantive rewrites, debugging, cross-file behavioral reasoning, and broader review. Consider `gpt-6-sol`, `gpt-5.6-terra`, and then `gpt-5.3-codex` for availability or demonstrated task fit. |
| Demanding review | Premium | `gpt-6.1-sol` with one exact supported effort of at least `high` | For security-sensitive or high-stakes review, prior important review misses, or repeated reasoning failures. Same-tier candidates include `gpt-6-sol` with one exact effort of at least `high`, `gpt-6-astra` with an exact Premium effort, and other Premium configurations with demonstrated review fit. |
| Demanding autonomous work | Premium | `gpt-6-astra` with one exact supported Premium effort | For long-horizon autonomous work or repeated Premium failures. Justify the added cost, task decomposition, and verification approach. |

Do not use the bounded-work default for substantive review.

Review floors are defined in [`review-routing.md`](review-routing.md).

## Exact-value resolution

To resolve a catalog entry:

1. Obtain the exact model identifiers accepted by the dispatch interface.
2. Obtain the exact reasoning-effort values accepted for each candidate model.
3. Remove unavailable models and unsupported effort values.
4. Remove configurations below the task's capability floor.
5. Apply explicit current-request user constraints.
6. Compare expected costs among the remaining capable configurations.
7. Select exactly one model and one effort.
8. Select exactly one same-tier fallback model and effort when available.

For example, a catalog entry that says:

```text
gpt-6.1-sol with high or stronger supported effort
```

must become an exact router result such as:

```yaml
model: gpt-6.1-sol
reasoning_effort: high
```

It must not become:

```yaml
model: gpt-6.1-sol
reasoning_effort: high or greater
```

If the dispatch interface accepts only `medium` for that model, the configuration does not satisfy a catalog requirement of `high` or stronger.

If the dispatch interface does not expose its accepted values, return `dispatchable: false`.

## Defaults and user constraints

Persistent model or effort configuration is not a hard user constraint.

Use configured, inherited, or runtime defaults only when the user explicitly requests their use in the current request.

Otherwise, the router-selected model and effort take precedence.

If the user explicitly requests configured defaults:

1. resolve those defaults to exact model and effort values
2. verify that they satisfy the capability floor
3. return `dispatchable: false` if they cannot be resolved or do not satisfy the floor

Do not omit routing fields as a way to preserve defaults.

## Evidence and uncertainty

Newer names, higher prices, and provider categories do not demonstrate review or security-review accuracy.

For an unvalidated task class:

- identify the route as provisional
- explain the platform or catalog guidance used
- require independent verification appropriate to the stakes
- do not describe the configuration as proven

If two configurations have similar expected cost, prefer the one with better demonstrated task fit.

## Availability and source notes

- Public-preview models may change behavior, pricing, or availability.
- Effort-based tier assignments are local routing choices, not GitHub capability guarantees.
- Confirm that the target dispatch interface exposes the requested reasoning effort.
- Published pricing does not establish that a model is selectable.
- GitHub publishes GPT-6 Luna and GPT-6 Sol token rates. The official comparison describes Luna for fast or simple tasks and Sol for interactive or agentic coding. Verify bounded-work Luna results before broadening its use.
- GitHub lists GPT-6.1 Sol as GA and recommends it for complex coding. Its input, output, and cache-write rates match GPT-6 Sol, while its cached-input rate is lower. The defaults remain provisional rather than measured review-quality rankings.
- GitHub schedules Claude Opus 4.7, Gemini 3.5 Flash, Gemini 3.6 Flash, and Kimi K2.7 Code for retirement on **2026-10-02**. Prefer listed replacements after retirement: Claude Opus 5, Gemini 3.8 Flash, and Kimi K3.
- Claude Sonnet 4.6 is available only to individual annual Pro or Pro+ subscribers after its September 1, 2026 retirement. Confirm runtime availability before routing.
- Claude Sonnet 4 remains in the pricing table but retired on **2026-05-01** and is not a routing candidate.
- Qwen2.5 appears only in model comparison, without a supported-models entry or published Copilot rate.

## Refresh procedure

When refreshing this catalog:

1. fetch the live sources directly
2. reconcile supported-model entries, availability restrictions, and retirement dates
3. do not infer availability from pricing or comparison pages alone
4. document intentionally excluded models
5. verify exact runtime IDs and effort settings separately
6. bypass stale caches before claiming that a model or entry is absent
7. update the verification date
