---
name: subagent-model-router
description: Route subagent work to the cheapest capable model. Use before dispatching subagents, task tools, background agents, code reviewers, security reviewers, or parallel workers when a model must be selected.
compatibility: Requires python3
---

# Subagent Model Router

Classify the task and use the bundled CLI to recommend an exact catalog model and effort. The catalog uses GitHub Copilot prices. Its capability classifications are provisional and its results do not establish live host availability.

## Classify the task

Set `task.work` to `bounded`, `standard`, `coding`, `exploration`, `planning`, or `execplan`. Use `exploration` for bounded, low-risk exploration with clear requirements and straightforward verification; it is Fast. Use `standard` for exploration requiring substantive judgment or cross-file behavioral reasoning. Substantive judgment, agentic coding, deep debugging, and ordinary substantive review are at least Standard. High stakes, security sensitivity, difficult reasoning, repeated failures, or a best-quality request call for Premium. For reviews, set `task.review` to `mechanical`, `substantive`, or `security`. Read [review-routing.md](reference/review-routing.md) only when review type or risk classification is unclear.

Supply supported facts in `task.risks`: `security_sensitive`, `high_stakes`, `unusually_difficult`, `repeated_reasoning_failures`, `user_requested_best_quality`, `new_evidence_raises_floor`, `stakes_or_ambiguity_increased`, or `important_review_miss`. Set `task.prior_important_miss` for a known relevant miss. Use `task.failure` for diagnosed `reasoning_gap`, `repeated_constraints_missed`, `repeated_reasoning_failures`, `new_evidence_raises_floor`, or `context_does_not_fit`; use the last only when no suitable same-tier configuration fits the required context. Set `task.selected_tier` when escalating a previous route.

Before recording a capability gap, check instructions, inputs, context, dependencies, permissions, tools, runtime availability, and verification quality. A failing test, build, or script alone does not establish a model capability gap. Preserve the original floor when availability alone requires a higher-tier configuration.

Prefer task-specific evaluation over similar-work evidence, provider guidance, and provisional catalog fit. Apply higher-priority evidence as judgment when interpreting the recommendation.

## Route

The CLI reads the bundled [`catalog.json`](reference/catalog.json). Add `constraints.models` or `constraints.efforts` only for explicit user constraints. The values are arrays of exact model IDs or effort names.

Optionally provide `usage.input_tokens`, `output_tokens`, `cached_input_tokens`, and `cache_write_tokens` for a token cost estimate. Treat these input counts as disjoint. Set `usage.cache_reuse_confirmed` true only for confirmed reuse; otherwise cached input is charged as uncached. Missing input or output counts, unknown charges, or expired promotional rates leave the affected estimate unknown. With no token estimates, ranking uses the sum of one uncached input and one output unit rate at ordinary context. This is a comparison assumption, not a predicted bill. All estimates exclude retries, verification, tools, and other completion overhead; neither cost nor live availability is verified.

Run `python3 <skill-root>/scripts/route.py --input request.json` to read a JSON request from a file. Use `--input -` to combine JSON from stdin with CLI flags; supplied flags override only their corresponding JSON fields, and repeated `--model` or `--effort` flags replace the JSON lists. With no flags, JSON stdin behavior is unchanged; flags alone do not read stdin. See `--help` for all supported fields and flags. The CLI prints a JSON catalog recommendation to stdout; usage or data errors go to stderr with exit 2. `recommendation_available` says whether the catalog produced a candidate that meets the floor and constraints. It does not certify dispatchability, dispatch work, or modify files.

## Dispatch

If `recommendation_available` is false, return a final route with `dispatchable: false`. Otherwise, use already-available dispatch interface facts to confirm that both the selected exact model and exact effort are accepted. If both are confirmed and applicable catalog restrictions are satisfied, return a final route with `dispatchable: true` and apply both values explicitly. If either value cannot be confirmed, including when the interface exposes no effort value, return `dispatchable: false` and do not dispatch. A catalog recommendation alone never confirms acceptance or context fit. Do not ask the user to select or approve a route.

Respect catalog restrictions returned with the selection or fallback and any already-known interface limitations. If the selected pair is known unavailable, use an eligible fallback or reassess using the known facts without collecting a complete inventory. Confirm the exact fallback pair before dispatch, preserving the floor and explicit constraints.

A fallback using the same model at another effort addresses effort-specific unavailability only. If the entire model is known unavailable, rule out all its efforts and reassess from already-known facts without gathering an inventory.

Return the final structured route with `dispatchable`, `tier`, exact `model` and `reasoning_effort` or unresolved values, `reason`, `escalation_trigger`, and same-tier `fallback` or `none`. The caller controls storage and presentation. The CLI's estimated cost is token-only; `cost_minimum_verified` remains false because actual completion costs are unknown. Load [maintenance.md](reference/maintenance.md) only when updating snapshots or investigating historical exclusions.
