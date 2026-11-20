---
name: subagent-model-router
description: Select a subagent model and effort policy using task requirements and catalog pricing. Use when a fast, standard, or premium tier subagent is requested.
compatibility: Requires python3
---

# Subagent Model Router

Classify the task and use the bundled CLI to select a model and effort policy.

Reuse these instructions while they remain current and available in the agent’s context. Run the CLI separately for each assignment, including assignments to a reused agent.

## Classify the task

Use `exploration` for bounded, low-risk exploration with clear requirements and straightforward verification. Use `standard` for exploration requiring substantive judgment or cross-file behavioral reasoning, and `coding` for implementation and debugging. For reviews, classify `task.review` by the judgment required. Read [review-routing.md](reference/review-routing.md) only when review type or risk classification is unclear.

Classify the assigned responsibility, not the agent's title or the artifact it touches:

- Use `bounded` for collecting updates, tracking progress, or applying agreed changes with straightforward verification.
- Use `standard` for reconciling conflicting evidence or resolving inconsistencies without redesigning scope, architecture, dependencies, or sequencing.
- Use `planning` or `execplan` for creating or materially revising scope, architecture, dependencies, or sequencing. These decisions remain planning when updating an existing plan.

Assess the assigned task's risks and difficulty independently; do not inherit another agent's model, effort, or tier.

When material planning and coding are separable, route them as separate tasks. Supply supported task risks and diagnosed failures. Set `task.prior_important_miss` for a known relevant miss. Use `task.selected_tier` as the minimum tier when the user requests a tier or when escalating a previous route for the same task.

Set capability-related failure flags only when supplied evidence identifies a model limitation. A failed test, missing dependency, permission denial, or unavailable model alone does not establish one.

Prefer task-specific evaluation over similar-work evidence, provider guidance, and provisional catalog fit. Use higher-priority evidence to classify task inputs before running the CLI.

## Route

Before first use, run `python3 <skill-root>/scripts/route.py --help` for supported fields, flags, input modes, and result semantics. Reuse that help while it remains current and available in context.

Add model and effort constraints only when explicitly requested by the user, including an exact model absent from the catalog.

Run the CLI with the classified task and supplied constraints, for example: `python3 <skill-root>/scripts/route.py --input request.json`.

Return the CLI's JSON result unchanged.

## Dispatch controls

Honor enforced worker restrictions, including for user-selected models. When worker policy excludes the primary, use the returned fallback if eligible or report the blocker. Descriptive lists are advisory. If availability is unknown, try once; a model-wide rejection excludes every effort. Require `route_available` unless the user selected that exact model. Use the user's explicit effort when supplied. Keep unknown availability, tier, cost and capability unknown. Fallbacks preserve capability floor, effort policy and worker profile. In Copilot, set `task.agent_type` to the required profile ID; `name` labels an instance. Reuse useful context only on the same model with matching explicit effort or originally omitted host-default effort. Missing controls block dispatch. Record overrides and fallbacks outside the router JSON and worker prompt.

Load [maintenance.md](reference/maintenance.md) only when updating snapshots or investigating historical exclusions.
