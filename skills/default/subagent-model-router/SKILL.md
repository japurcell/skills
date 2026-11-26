---
name: subagent-model-router
description: Select a subagent model and effort policy using task requirements and catalog pricing. Use when a fast, standard, or premium tier subagent is requested.
compatibility: Requires python3
---

Load these instructions and read `python3 <skill-root>/scripts/route.py --help` once per session. Reuse both for subsequent assignments. Run `route.py` with each assignment’s inputs, including when reusing a worker. Copy CLI output verbatim, including the full `reason` string.

Classify independently. Use `bounded` for routine updates, `standard` for reconciling reports without a review assignment. Straightforward, bounded, low-risk investigation is `exploration`, substantive or cross-file reasoning `standard`. Creating or materially revising scope, architecture, dependencies or sequencing is planning. Implementation and debugging are `coding`. Route separable planning and coding independently.

Prefer task evaluation, then similar work, provider guidance, catalog fit. Supply evidenced risks, diagnosed capability failures and relevant prior important misses. Requested tiers and same-task escalations set floors. Apply only user-specified model and effort constraints, including uncatalogued IDs.

## Review classification

Set `task.review` to `mechanical` for readily verified nonsemantic edits, `substantive` for behavior, tests, guards or meaningful refactoring, or `security` for security-sensitive review.

Authentication, authorization, secrets, credentials, cryptography and trust boundaries warrant `security_sensitive`. Serious correctness, subtle concurrency, cache consistency and false-pass risks warrant `high_stakes`. Use `unusually_difficult` for difficult reasoning across large or highly connected codebases. File count alone establishes no risk. Flag repeated reasoning failures and explicit best-quality requests.

## Dispatch controls

Enforce worker policy. Never dispatch Gemini Argon, Hydrogen or Carbon, even on request. Claude Fable and GPT Astra require an exact model ID named by the user. Only exact user models bypass `route_available`. Lists are advisory. Try unknown availability once. Model-wide rejection excludes every effort.

Blocked primary requires an eligible returned fallback or blocker. Preserve floor, effort policy, profile and explicit user effort. Missing controls block dispatch. Preserve unknowns.

Reuse useful context only with matching model and explicit effort or originally omitted default effort. Copilot `task.agent_type` selects profiles, `name` labels instances. Record overrides/fallbacks outside router JSON and worker prompts.

## Catalog maintenance

Refresh [catalog.json](reference/catalog.json) from its dated sources. Verify availability, restrictions, administrator enablement and retirement cutoffs against supported models, fit against model comparison, IDs and efforts against the runtime. Bypass stale caches before declaring absence.

Reconcile Copilot rates, thresholds, cache charges and promotion deadlines. Preserve currency, token units and legacy annual-plan multipliers. Promote a supported same-family successor wherever its predecessor starts a task at the required tier and effort. Keep the eligible predecessor first among alternatives and remove duplicates. Align tier rows with overlapping task preferences and order newer family versions first. Preserve catalog routing exclusions and explicit-only families. Update entries, defaults, snapshot dates and restriction/exclusion provenance together.

**2026-11-25 snapshot.** GPT-5.6 Terra and Claude Opus 5 retired November 16. Standard Claude Opus 4.8 remains available to legacy annual Pro+ subscribers. Fast mode has its own availability and price. The October 19 retirements are GPT-5 mini, GPT-5.4, GPT-5.4 mini, GPT-5.5 and Gemini 3.7 Flash. Exclude fully retired models from routing even when a price row remains. Opus 4.7, Gemini 3.5 Flash, Gemini 3.6 Flash and Kimi K2.7 Code retired October 2. GitHub recommended their latest family successors. Sonnet 4 retired May 1 despite its price row. Qwen2.5 lacked support and pricing. Recheck [retirement history](https://docs.github.com/en/copilot/reference/ai-models/supported-models#model-retirement-history) before restoring candidates.

Argon is GA and excluded by routing policy. Terra Standard/medium and Gemini 3.8 Flash Fast/medium require runtime confirmation.
