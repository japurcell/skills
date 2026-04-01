# Feature Dev Workflow: Go/No-Go for Skipping Exploration

## Understanding

A developer new to the repo wants to deliver a medium-sized feature. Their lead recommends skipping exploration and coding immediately. Using the feature-dev workflow to give a clear recommendation and pre-implementation checklist.

**Track chosen**: Standard — medium-sized feature, unfamiliar repo, some ambiguity about conventions and architecture.

---

## Recommendation: NO-GO on Skipping Exploration

Do not start implementation without first completing the exploration phase.

### Why Skipping Exploration is High-Risk in an Unfamiliar Repo

The feature-dev workflow's Phase 2 (Codebase Exploration) exists specifically because "understanding before acting" is a core principle. Here is what skipping it costs you:

| Risk                                                                            | Workflow Phase This Affects                             |
| ------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Writing code that duplicates existing utilities or abstractions                 | Phase 2: miss similar-feature patterns                  |
| Violating naming, error-handling, or layering conventions                       | Phase 2: miss architecture and convention mapping       |
| Missing integration points that break adjacent behavior                         | Phase 3: cannot ask targeted questions without findings |
| Choosing the wrong design approach because you didn't see the existing patterns | Phase 4: architecture design is based on guesswork      |
| TDD tests written in the wrong test harness or fixture style                    | Phase 5: test conventions not known                     |

"Figure out conventions as you go" is specifically what the workflow prevents — corrections at implementation time are expensive.

---

## Pre-Implementation Checklist (Minimum Required)

Complete all of the following before writing production code. For a Standard track feature, launch **two focused code-explorer agents in parallel**, each targeting a different angle.

### Exploration Outputs Required

- [ ] **Similar-feature trace**: Find 1–2 features in the codebase that are structurally similar to what you're building. Trace their full implementation: entry point → business logic → persistence/output → tests. Understand the pattern you'll be following.

- [ ] **Architecture and touchpoint map**: Identify which layers, modules, or services your feature will touch. Map: Which abstractions already exist? What extension points are available? What integration contracts must you respect?

- [ ] **Test and CI convention mapping**: Identify the test framework, fixture patterns, and test file locations. Know what a passing test file looks like in this codebase before you write your first one.

- [ ] **Read key files directly**: After agents return their findings, read the 5–10 files they flag as most important. Your understanding must be grounded in actual source, not just agent summaries.

### Clarifying Questions (Keep to High-Leverage Items Only)

Before implementation, confirm:

1. **Scope boundary**: Where does this feature end? Is there shared state, API contract, or downstream consumer affected that is out of scope for this work?
2. **Error and edge case handling**: What should happen on invalid input or partial failure? If this is unspecified, the implementation could go in two very different directions.
3. **Backward compatibility requirement**: Does the feature need to preserve any existing interface, configuration key, or behavior?

Ask only these if the answer would materially change your design or scope. If you can state a reasonable assumption, do that and keep moving.

---

## Mandatory Gates Before You Hand Back Work

Even after completing exploration and implementation, the workflow requires three non-negotiable checkpoints regardless of track:

1. **TDD red-green-refactor loop** — Implementation must use the TDD skill with an explicit red-green-refactor loop. This is required on every track and cannot be bypassed.
2. **Independent `code-simplifier` pass** — A dedicated subagent identifies refactoring opportunities after implementation.
3. **Independent `code-reviewer` review** — At least one independent `code-reviewer` agent performs quality review (more for Standard/Deep tracks with parallel specialist lenses).

These are not optional even under time pressure. If you are under deadline constraints, use the Light track for bounded sub-tasks rather than skipping these gates.

---

## Summary

Skip-exploration is a **no-go**. Complete the three exploration outputs above, then resolve only the highest-leverage clarifying questions before proceeding to design and implementation. The workflow will move faster with this foundation than without it.
