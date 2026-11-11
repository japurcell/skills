---
name: subagent-model-router
description: Route subagent work to the cheapest capable model. Use when asked to use subagents from a tier or when the user says "use a [fast|standard|premium] subagent".
compatibility: Requires python3
---

# Subagent Model Router

Classify the task and use the bundled CLI to recommend a catalog model and effort policy. The catalog uses GitHub Copilot prices. Its capability classifications are provisional and its results do not establish live host availability.

Reuse these instructions while they remain current and available in the agent’s context. Run the CLI and verify the final route separately for each assignment, including assignments to a reused agent.

## Classify the task

Set `task.work` to `bounded`, `standard`, `coding`, `exploration`, `planning`, or `execplan`. Use `exploration` for bounded, low-risk exploration with clear requirements and straightforward verification; it is Fast. Use `standard` for exploration requiring substantive judgment or cross-file behavioral reasoning. Substantive judgment, agentic coding, deep debugging, and ordinary substantive review are at least Standard. High stakes, security sensitivity, difficult reasoning, repeated failures, or a best-quality request call for Premium. For reviews, set `task.review` to `mechanical`, `substantive`, or `security`. Read [review-routing.md](reference/review-routing.md) only when review type or risk classification is unclear.

Classify each agent by its assigned responsibility, not the artifact it touches or its coordinator title. For work involving a plan:

- Use `bounded` (Fast) for routine coordination: collecting updates, tracking progress, or applying agreed changes with straightforward verification.
- Use `standard` (Standard) for substantive coordination: reconciling findings or resolving inconsistencies without redesigning the plan.
- Use `planning` or `execplan` for creating or materially revising scope, architecture, dependencies, or sequencing. These decisions remain planning when updating an existing plan.

Assess risk and difficulty for the assigned task independently. The plan author's model, effort, and tier do not become a coordinator's constraints or minimum tier. Coordination that owns security-sensitive or other high-risk judgment still requires Premium.

Require explicit effort only for dedicated material planning or architecture (`planning` or `execplan`), substantive review, security review, or an explicit user effort constraint. Coding, tests, debugging, local design, exploration, coordination, mechanical review, and other work omit effort, including when risk or failure flags raise the model tier. When material planning and coding are separable, route them as separate tasks. Explicit user effort constraints always win. An actual user choice of an exact model overrides the router’s advisory tier recommendation; callers apply that choice through existing host controls, subject to model support, permission, live acceptance, applicable restrictions, the effort policy and any explicit user effort, and runtime deadlines. A router recommendation is not user selection. Without an exact user model choice, use normal router selection and constraints. Do not add a CLI override API or infer catalog capability for an out-of-catalog user choice. Supply supported facts in `task.risks`: `security_sensitive`, `high_stakes`, `unusually_difficult`, `repeated_reasoning_failures`, `user_requested_best_quality`, `new_evidence_raises_floor`, `stakes_or_ambiguity_increased`, or `important_review_miss`. Set `task.prior_important_miss` for a known relevant miss. Use `task.failure` for diagnosed `reasoning_gap`, `repeated_constraints_missed`, `repeated_reasoning_failures`, `new_evidence_raises_floor`, or `context_does_not_fit`; use the last only when no suitable same-tier configuration fits the required context. Set `task.selected_tier` when escalating a previous route for this same task.

Before recording a capability gap, check instructions, inputs, context, dependencies, permissions, tools, runtime availability, and verification quality. A failing test, build, or script alone does not establish a model capability gap. Preserve the original floor when availability alone requires a higher-tier configuration.

Prefer task-specific evaluation over similar-work evidence, provider guidance, and provisional catalog fit. Apply higher-priority evidence as judgment when interpreting the recommendation.

## Route

The CLI reads the bundled [`catalog.json`](reference/catalog.json). Add `constraints.models` or `constraints.efforts` only for explicit user constraints. The values are arrays of exact model IDs or effort names.

Optionally provide `usage.input_tokens`, `output_tokens`, `cached_input_tokens`, and `cache_write_tokens` for a token cost estimate. Treat these input counts as disjoint. Set `usage.cache_reuse_confirmed` true only for confirmed reuse; otherwise cached input is charged as uncached. Missing input or output counts, unknown charges, or expired promotional rates leave the affected estimate unknown. With no token estimates, ranking uses the sum of one uncached input and one output unit rate at ordinary context. This is a comparison assumption, not a predicted bill. All estimates exclude retries, verification, tools, and other completion overhead; neither cost nor live availability is verified.

Run `python3 <skill-root>/scripts/route.py --input request.json` to read a JSON request from a file. Use `--input -` to combine JSON from stdin with CLI flags; supplied flags override only their corresponding JSON fields, and repeated `--model` or `--effort` flags replace the JSON lists. With no flags, JSON stdin behavior is unchanged; flags alone do not read stdin. See `--help` for all supported fields and flags. The CLI prints a JSON catalog recommendation to stdout; usage or data errors go to stderr with exit 2. `recommendation_available` says whether the catalog produced a candidate that meets the floor and constraints. It does not certify dispatchability, dispatch work, or modify files.

## Dispatch

Read `recommendation_available` separately from `effort_policy`. In normal catalog routing, no recommendation means `dispatchable: false`. An actual user choice of an exact model bypasses this catalog-candidate gate and uses the existing host model control, even if the CLI has no candidate. Preserve `recommendation_available: false`, record the user-selected model in the final route, and leave its catalog tier, price, and capability unresolved. Apply the task’s effort policy and any explicit user effort. `host_default` has `reasoning_effort: null` and `capability_at_host_default_verified: false`: omit effort and record the inherited default as unverified. `explicit` requires its exact effort; if it is unresolved or unsupported, stop and name that blocker rather than substituting a default. A catalog recommendation never proves interface support, permission, context fit, or live acceptance.

Before routing, confirm the dispatch interface supports the exact model control and that the caller is permitted to set it. For `explicit` effort policy, also confirm effort-control support and permission before routing. These checks are distinct from verifying that the selected model or required effort is accepted live. If a check fails, return `dispatchable: false` and name that specific blocker; do not describe a permission failure as unavailable capability. For the selected model, verify applicable restrictions and live acceptance of that exact model, plus exact effort only when policy is `explicit`. Dispatch only after every required check succeeds. If an exact model or required effort is unconfirmed, do not dispatch.

Fallbacks follow the same effort policy and dispatch checks; do not change policy to make a fallback dispatchable.

A fallback using the same model at another effort addresses effort-specific unavailability only. If the entire model is known unavailable, rule out all its efforts and reassess from already-known facts without gathering an inventory.

Return the final structured route with `dispatchable`, `tier`, `effort_policy`, exact `model` and `reasoning_effort` or unresolved values, `reason`, `escalation_trigger`, and same-tier `fallback` or `none`. The caller controls storage and presentation. The CLI's estimated cost is token-only; `cost_minimum_verified` remains false because actual completion costs are unknown. Load [maintenance.md](reference/maintenance.md) only when updating snapshots or investigating historical exclusions.
