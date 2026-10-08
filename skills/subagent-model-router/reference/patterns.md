# Routing Patterns

These examples are non-authoritative. If they conflict with `SKILL.md`, [`review-routing.md`](review-routing.md), or [`escalation-policy.md`](escalation-policy.md), follow the authoritative rule.

## Reuse

| Situation | Route |
| --- | --- |
| Identical deterministic checks under unchanged constraints | Reuse a Fast route |
| Reviews with unchanged scope, risk, behavior, history, and runtime constraints | Reuse the route |
| Execution changes to architecture analysis | Route again |
| A non-review task previously missed an important constraint | Route again and apply general escalation |
| A similar review previously missed an important issue | Route again with a Premium floor |
| Runtime model or effort availability changes | Route again |

## Task examples

| Request | Tier |
| --- | --- |
| Run tests and summarize explicit failures | Fast |
| Search a repository for relevant code | Fast |
| Apply formatting or a specified mechanical edit | Fast |
| Rename a symbol mechanically across many files | Fast |
| Change behavior across connected files | Standard |
| Debug a multi-component interaction | Standard |
| Analyze subtle authentication, cache, or concurrency risk | Premium |
| Perform long-horizon autonomous work over a large codebase | Premium |

## Review examples

| Request | Tier or default |
| --- | --- |
| Review whitespace, comments, or reproducible generated output | Fast |
| Review a substantive one-file change | Standard |
| Review an ordinary bounded feature change | Standard; budget-review default |
| Review cross-component behavior | Standard; general-work default |
| Review tests or guard logic | Standard |
| Review security-sensitive false-pass behavior | Premium |
| Review authentication, authorization, redirects, or trust boundaries | Premium |
| Conduct a security audit | Premium |
| Repeat a similar review after an important miss | Premium |

## Failure examples

| Situation | Response |
| --- | --- |
| Tests fail | Diagnose before escalating |
| A dependency is missing | Fix or report the environment problem |
| The selected configuration is unavailable | Reroute within the same tier; move higher only if no same-tier configuration qualifies |
| Verification repeatedly exposes reasoning gaps | Apply the escalation policy |
| A task becomes security-sensitive | Reclassify the floor as Premium |
| Premium work still fails | Change Premium configuration, split the task, strengthen verification, or seek human review |

## Cost examples

| Request shape | Primary consideration |
| --- | --- |
| Large input, short answer | Input and context-threshold cost |
| Short input, long answer | Output cost |
| Reused context | Confirmed cache behavior and cache-write cost |
| Likely retries | Expected retry and verification cost |
