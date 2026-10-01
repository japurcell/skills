# Routing Patterns

These examples illustrate the authoritative rules in:

- [`../SKILL.md`](../SKILL.md)
- [`review-routing.md`](review-routing.md)
- [`escalation-policy.md`](escalation-policy.md)
- [`model-catalog.md`](model-catalog.md)

If an example conflicts with an authoritative rule, follow the authoritative rule.

## Reuse versus fresh routing

| Situation | Illustrative decision |
| --- | --- |
| Multiple workers perform the same deterministic fixture checks under the same constraints | Route once as Fast and reuse the route. |
| Multiple reviews have materially identical scope, risk, affected behavior, history, and runtime constraints | Reuse the route while those conditions remain unchanged. |
| A task changes from test execution to architecture analysis | Route again because the work class and reasoning requirement changed. |
| A non-review task previously missed an important constraint | Route again and apply the non-review prior-miss rule in `escalation-policy.md`. |
| A prior materially similar review missed an important issue | Route again with the Premium floor required by `review-routing.md`. |
| Runtime availability or supported effort changes | Route again because the model constraints changed. |

## Execution and analysis examples

| Request | Illustrative route | Why |
| --- | --- | --- |
| Run tests and summarize explicit failures | Fast | Mechanical execution with bounded summarization. |
| Search a repository for token-lifecycle code | Fast | Bounded exploration without a judgment-heavy conclusion. |
| Format files or apply a specified mechanical edit | Fast | Deterministic transformation with straightforward verification. |
| Rename a symbol mechanically across many files | Fast | File count alone does not raise the tier when verification is straightforward. |
| Change behavior shared across connected files | Standard | Requires cross-file behavioral reasoning. |
| Debug an interaction among several components | Standard | Requires substantive diagnosis and reasoning. |
| Debug an authentication, cache, or concurrency interaction with subtle correctness or security impact | Premium | Security sensitivity or high-stakes subtle correctness establishes a Premium floor. |
| Produce a long-horizon autonomous implementation plan and execute it across a large codebase | Premium | Requires sustained planning, reasoning, and verification. |

## Review examples

Review tiers are governed by [`review-routing.md`](review-routing.md).

| Request | Illustrative route | Why |
| --- | --- | --- |
| Review whitespace-only or comment-only changes | Fast | Non-semantic changes with straightforward verification. |
| Review a generated-file refresh whose generator output can be reproduced | Fast | Mechanical change with direct verification. |
| Review a substantive one-file feature change | Standard | Substantive review is at least Standard regardless of file count. |
| Review an ordinary bounded feature PR | Standard with the budget-review default | Clear scope but meaningful behavioral judgment is required. |
| Review a backend and frontend behavior change | Standard with the general-work default | Broader cross-component reasoning is required. |
| Review test assertions or guard logic | Standard | Substantive review is required even if only tests changed. |
| Review subtle false-pass behavior in security-sensitive tests | Premium | Security and subtle correctness establish a Premium floor. |
| Review authentication callbacks or redirect validation | Premium | Security-sensitive review. |
| Conduct a security audit | Premium | Security review always has a Premium floor. |
| Repeat a materially similar review after an important issue was missed | Premium | Prior important review miss establishes a Premium floor. |

## Failure examples

| Situation | Illustrative response |
| --- | --- |
| Tests fail because the implementation is incorrect | Keep the current tier while diagnosing; the failure alone does not justify escalation. |
| Tests cannot run because a dependency is missing | Fix or report the environment problem before considering escalation. |
| The selected model is unavailable | Choose a capable same-tier fallback and report the availability-driven change. |
| Verification repeatedly exposes missed constraints after the environment and instructions are checked | Escalate according to `escalation-policy.md`. |
| A Fast task turns out to require cross-file behavioral reasoning | Reclassify the floor as Standard and route again. |
| A Standard task becomes security-sensitive | Reclassify the floor as Premium rather than treating this as an optional escalation. |
| A Premium worker still fails | Try a better-fitting Premium configuration, split the task, strengthen verification, or request human review. |

## Token-shape examples

Use [`pricing.md`](pricing.md) for the authoritative cost rules.

| Request shape | Primary cost consideration |
| --- | --- |
| Very large logs with a short diagnosis | Input cost, context thresholds, and the likelihood of needing retries |
| Short prompt requiring a long proposal | Output cost |
| Repeated use of the same repository context | Confirmed cache reuse; assume uncached input if reuse is not verified |
| Reusable context on a model with cache-write charges | Initial cache-write cost plus subsequent cached-input cost |
| Cheap model likely to require multiple retries | Expected total retry and verification cost rather than the first-request rate |
