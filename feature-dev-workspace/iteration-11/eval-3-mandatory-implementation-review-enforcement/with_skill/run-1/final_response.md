# Eval 3 – Mandatory Implementation & Review Enforcement

**Skill**: feature-dev  
**Track Selected**: Standard  
**Rationale**: The request is a medium-sized feature that updates three files with light ambiguity — enough scope to justify Standard Track, not so large or unclear that Deep is warranted.

---

## Understanding

The request asks to implement a bounded medium-sized feature across three files, then perform a full review. Standard Track applies: explore in depth, ask targeted questions if needed, implement, then run mandatory quality review.

---

## How the Workflow Enforces Implementation Requirements

### Phase 1 – Discovery

A todo list is created and scaled to the actual work:

- [ ] Explore relevant codebase areas (2 code-explorer agents)
- [ ] Ask clarifying questions if blocking gaps remain
- [ ] Design the approach
- [ ] Implement with TDD
- [ ] Run quality review (code-simplifier + code-reviewer agents)
- [ ] Fix high-severity issues
- [ ] Write handoff artifact

### Phase 2 – Codebase Exploration (Standard Track)

Two **code-explorer** agents launch in parallel, each targeting a different angle:

- Agent 1: "Map the architecture and abstractions for the feature area, tracing through the code comprehensively"
- Agent 2: "Find features similar to this one and trace through their implementation comprehensively"

After they return, the skill requires reading the key files they surface — grounding understanding in source code, not just agent summaries.

### Phase 3 – Clarifying Questions

Assumptions are stated for minor gaps. Only truly blocking questions are asked. Because three specific files are identified and the scope is concrete, this phase proceeds quickly.

### Phase 4 – Architecture Design (Standard Track)

The skill calls for 1–2 approaches if a real design trade-off exists. A single recommended approach is proposed here (minimal change path), since the scope is tight. No artificial fork is manufactured.

### Phase 5 – Implementation (MANDATORY Enforcement)

> **"Always use the tdd skill to implement with an explicit red-green-refactor loop. Treat this as required for Implementation on every track; do not bypass it."**

Enforcement mechanism — the skill text is prescriptive and unconditional:

1. **Write failing tests first** (red) for each of the three files being changed
2. **Implement the minimal code** to make tests pass (green)
3. **Refactor** for clarity and DRYness without breaking tests

This sequence applies regardless of track. There is no conditional path that skips TDD.

The three files are updated in the sequence defined by the Implementation Map, with todos checked off after each file.

---

## How the Workflow Enforces Quality Review Requirements

### Phase 6 – Quality Review (MANDATORY Enforcement)

The skill text specifies two unconditional rules that apply on every track:

#### Rule 1 — code-simplifier (always)

> **"Always launch an independent [code-simplifier](../code-simplifier/SKILL.md) subagent to identify refactoring opportunities after implementation."**

**Subagent role**: `code-simplifier`  
**Source**: `skills/code-simplifier/SKILL.md`  
**Purpose**: Independently reviews the newly written code for redundancy, over-engineering, naming quality, and structural clarity. It does not participate in implementation — it operates after the fact, independently.

#### Rule 2 — code-reviewer (always, multiplied by track)

> **"Always run independent [code-reviewer](agents/code-reviewer.md) agents for quality review on every track."**

**Subagent role**: `code-reviewer`  
**Source**: `skills/feature-dev/agents/code-reviewer.md`  
**Scale**:

- **Light**: at least one `code-reviewer` agent
- **Standard or Deep**: multiple `code-reviewer` agents launched **in parallel**, each with a different focus

For this Standard Track execution, the skill launches multiple code-reviewer agents in parallel:

| Agent              | Focus                                                                   |
| ------------------ | ----------------------------------------------------------------------- |
| `code-reviewer` #1 | Simplicity — are the changes as minimal and readable as possible?       |
| `code-reviewer` #2 | Correctness — do the changes handle edge cases and integrate cleanly?   |
| `code-reviewer` #3 | Conventions — does the code match existing codebase style and patterns? |

#### Post-Review Actions (also enforced)

- Findings are consolidated and prioritized by severity.
- **High-severity issues are fixed directly** unless the user explicitly asked to stop after review.
- Remaining risks and follow-up items are surfaced clearly.

---

## Exact Subagent Roles Summary

| Subagent          | Phase   | Track                   | Mandatory? | Source                        |
| ----------------- | ------- | ----------------------- | ---------- | ----------------------------- |
| `code-explorer`   | Phase 2 | Standard: 2 in parallel | Per-track  | `agents/code-explorer.md`     |
| `code-architect`  | Phase 4 | Deep only               | Deep only  | `agents/code-architect.md`    |
| `code-simplifier` | Phase 6 | **All tracks**          | **Always** | `../code-simplifier/SKILL.md` |
| `code-reviewer`   | Phase 6 | **All tracks**          | **Always** | `agents/code-reviewer.md`     |

> Note: `code-simplifier` is the only cross-skill subagent (sourced from a sibling skill). All others are sourced from the feature-dev agents directory.

---

## Handoff Artifact

Per skill requirements, a handoff artifact would be written to:

`.agents/scratchpad/<feature-name>/handoff-plan.md`

Following the template at `skills/feature-dev/references/handoff-plan-template.md`.

---

## Conclusion

The feature-dev skill enforces implementation and review requirements through **unconditional language** ("always", "required", "do not bypass") in Phases 5 and 6. On Standard Track:

- TDD is mandatory in Phase 5 on every track — no bypass path exists
- `code-simplifier` launches independently after every implementation
- Multiple parallel `code-reviewer` agents run with distinct focuses (simplicity, correctness, conventions)
- High-severity findings are fixed immediately, not deferred
