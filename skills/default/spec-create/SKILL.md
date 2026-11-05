---
name: spec-create
description: Create or revise a portable behavioral SPEC for a feature or whole product. Use when specifying a new idea, documenting an existing system for reimplementation, or defining a change while preserving compatibility. Implementation planning is a separate task.
argument-hint: "[<feature, product, or existing spec>] [<output path>]"
---

# spec-create

Write a Markdown contract that an independent team can implement and check using only the SPEC and its declared public contracts. A planner should be able to choose a different language, architecture, or test framework without renegotiating behavior.

## Choose the boundary and destination

Identify who uses the system, through which interfaces, and what outcomes are in scope. For a feature, include the callers and neighboring behavior the feature can affect. For a product, define shared rules once and cover journeys that cross feature boundaries.

Use an explicit output path first. Otherwise, revise the existing canonical spec for this scope in place or follow the project's established spec location. If neither exists, use:

- Product: `SPEC.md` at the project root.
- Feature: `docs/specs/<short-kebab-case-feature-name>/SPEC.md`, for example `docs/specs/job-cancellation/SPEC.md`.

Read an existing spec before editing. Preserve unrelated contracts, conformance cases, and useful organization. Check that the chosen file belongs to this scope before writing.

## Establish what the spec can promise

- **New idea.** Draft the behavior supported by the request and declared public contracts. Ask only about unresolved choices that would change a caller's experience or the verdict of a conformance check. Group independent questions in one round and continue drafting settled parts.
- **Existing system.** Start at its normal entry points. Use current docs, callers, tests, and code to identify compatibility cases, then exercise them where practical. Capture concrete inputs, outputs, visible effects, and relevant failure or recovery behavior. Distinguish direct observations, reported observations, and inferences. If the system is unavailable, identify what could not be checked.
- **Change to an existing system.** Establish that baseline for the affected scope. Identify what callers can still rely on, what intentionally changes, and what happens to existing callers, data, or in-flight work where relevant. Apply existing rules to the change without silently extending them. A single example can demonstrate an outcome without establishing a general policy. If two plausible policies produce different results, find a distinguishing case or ask.

When evidence disagrees, record the competing behaviors and investigate caller reliance. If the intended contract remains unclear, ask which behavior to preserve. Keep the decision open and the spec in **Draft**. Silence, an implementation accident, and an inability to run the system do not authorize a new promise.

## Write the contract

Use descriptive headings for scope, observable behavior, and conformance cases. Add sections such as state transitions, interfaces, failures, or compatibility only where they carry distinct obligations. A small feature may need just a few rules.

Use `MUST` for requirements, `SHOULD` for recommendations with reasons to depart, and `MAY` for permitted choices. State exact formats, names, units, limits, or protocols when users, callers, or integrations rely on them. Express other constraints through their effects. For example, preserve a public `job_id` field and say whether an accepted job survives restart. Leave the storage engine to the planner.

Describe deliberate variation precisely enough to judge either implementation. If listing order is immaterial, require each eligible item exactly once and allow any order. If callers depend on knowing an implementation's chosen policy, require the implementation to document it. Keep unresolved decisions distinct from permitted variation.

Give every required behavior an observable pass/fail criterion. Under the relevant heading or in a conformance section, state the initial conditions, action, and expected result or allowed range. Use ordinary prose, examples, or a compact table. Refer to behaviors by descriptive headings and case descriptions, without assigning per-behavior IDs. Include relevant failure, recovery, compatibility, and cross-feature cases. For an optional capability, make its checks conditional on providing it.

If source paths, test names, observations, or verification gaps help explain a decision, collect them in a short **informational** appendix. Keep the normative contract intelligible without that appendix or access to the original repository.

## Decide whether it is ready for planning

Read the spec as two independent implementers. Find a concrete input, failure, or sequence where both could follow the text and produce materially different outcomes. Try relevant boundaries such as a retry after a lost response, a restart mid-operation, or competing requests. For each difference, tighten the rule and its check, explicitly allow both outcomes, or surface the unresolved choice.

Mark the spec **Ready for planning** only when each required behavior has a check, compatibility obligations are accounted for, and no material decision remains open. Otherwise save a **Draft** with the unresolved questions, their consequences, and any gaps in the baseline evidence. Report the file, status, and decisions needed. Building an implementation, choosing its tests, and proving it passes belong to downstream work.
