# Feature-Dev Workflow: Medium Feature Across Three Files with Review

---

## Understanding

**Track selected: Standard**

The request asks to implement a medium-sized feature that touches three files, then perform a formal review. This matches the Standard Track criteria: multiple files affected, non-trivial sequencing, and an explicit review gate. I'll run the full Standard workflow: exploration → clarifying questions → design → implementation (with TDD) → quality review.

---

## Phase 1: Discovery

**Todo list (Standard Track)**

- [x] Determine track and scope
- [ ] Run codebase exploration (2 parallel agents)
- [ ] Resolve clarifying questions if any blockers remain
- [ ] Design implementation approach
- [ ] Implement with TDD (red-green-refactor — required on every track)
- [ ] Run quality review subagents
- [ ] Fix high-severity findings
- [ ] Surface remaining risks

**Interpretation of the feature request**

The feature is a self-contained, medium-scope change that modifies exactly three files. There is no description of what domain this is in, so I'll treat it as a representative walkthrough of how the workflow enforces each phase. The three files will be called `src/core/processor.ts`, `src/api/handler.ts`, and `src/utils/formatter.ts` for concreteness.

---

## Phase 2: Codebase Exploration

Two `code-explorer` agents are launched in parallel on the Standard Track:

| Agent             | Focus                                                                                                                  | Files Returned                                                                                                               |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `code-explorer-A` | Map the architecture around processor and handler — trace the request lifecycle from handler input to processor output | `src/core/processor.ts`, `src/api/handler.ts`, `src/core/processor.test.ts`, `src/api/handler.test.ts`, `src/types/index.ts` |
| `code-explorer-B` | Analyze formatter utilities and understand how they plug into processor and handler output paths                       | `src/utils/formatter.ts`, `src/utils/formatter.test.ts`, `src/api/handler.ts`                                                |

After agents return, the key files are read directly to ground understanding in source rather than agent summaries.

**Relevant Findings**

- `processor.ts` exports a `runProcessor(input: Input): Result` function. It delegates formatting to `formatter.ts`.
- `handler.ts` receives HTTP requests, calls `runProcessor`, and returns the formatted result.
- `formatter.ts` exposes a `formatResult(r: Result): string` helper. The current implementation does not handle the `null` result case — it throws.
- All three files have test files co-located with them.
- Codebase uses Jest; tests are structured as `describe` / `it` blocks with no mocking framework magic.

---

## Phase 3: Clarifying Questions

One potential blocker: the `null` result path in `formatter.ts`. This could be intentional (null is never expected) or a gap. Because the feature is described as "medium-sized" with no specific product requirement, I'll state the assumption:

> **Assumption**: the feature should add graceful null handling in `formatter.ts`, plumb an updated result type through `processor.ts`, and update `handler.ts` to return a proper 404 when null is returned by the processor. No further questions are blocking.

---

## Phase 4: Architecture Design

**Standard Track** — one concrete approach is proposed, since there is no meaningful product fork.

**Approach: Extend the Result type, guard in formatter, propagate to handler**

1. `src/utils/formatter.ts` — add a `null` branch that returns an empty string sentinel.
2. `src/core/processor.ts` — update `Result` type to `Result | null` and adjust any callers.
3. `src/api/handler.ts` — check for the null/empty-sentinel result and respond with HTTP 404.

This is the minimal change path: three files, logical layering from utility → core → API, and no new abstractions.

---

## Phase 5: Implementation

**TDD — red-green-refactor loop (required on all tracks)**

The TDD skill governs implementation. Each change follows the red → green → refactor cycle:

### File 1: `src/utils/formatter.ts`

**Red** — write a failing test:

```typescript
it("returns empty string for null result", () => {
  expect(formatResult(null)).toBe("");
});
```

Test fails: `formatResult` throws on null.

**Green** — add the null guard:

```typescript
export function formatResult(r: Result | null): string {
  if (r === null) return "";
  return JSON.stringify(r);
}
```

Test passes.

**Refactor** — no duplication introduced; no refactor needed.

---

### File 2: `src/core/processor.ts`

**Red** — write a failing test:

```typescript
it("returns null when input is empty", () => {
  expect(runProcessor({ data: "" })).toBeNull();
});
```

Test fails: `runProcessor` currently returns a default `Result` object for empty input.

**Green** — add the null return path:

```typescript
export function runProcessor(input: Input): Result | null {
  if (!input.data) return null;
  // ... existing processing logic
}
```

Test passes.

**Refactor** — the `Result | null` type update cascades cleanly; no logic refactor needed.

---

### File 3: `src/api/handler.ts`

**Red** — write a failing test:

```typescript
it("returns 404 when processor returns null", async () => {
  const res = await handleRequest({ body: { data: "" } });
  expect(res.statusCode).toBe(404);
});
```

Test fails: handler returns 200 with an empty string body.

**Green** — add the 404 branch:

```typescript
export async function handleRequest(req: Request): Promise<Response> {
  const result = runProcessor(req.body);
  if (result === null) return { statusCode: 404, body: "Not found" };
  return { statusCode: 200, body: formatResult(result) };
}
```

Test passes.

**Refactor** — extract the null-check into a one-liner guard; no structural change needed.

---

All todos for implementation are marked done. TDD loop completed for all three files.

---

## Phase 6: Quality Review

**This phase is mandatory on every track and enforces two independent subagent roles.**

### Subagents launched

The Standard Track requires multiple independent review agents run in parallel:

| Subagent          | Role                                                                                                                                                   | Governed by                                  |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------- |
| `code-simplifier` | Identifies dead code, unnecessary abstractions, duplication, and opportunities to simplify logic. Always launched after implementation.                | `skills/code-simplifier/SKILL.md`            |
| `code-reviewer-A` | Reviews for correctness — checks null propagation, type safety, edge cases missed by tests, and behavioral regressions.                                | `skills/feature-dev/agents/code-reviewer.md` |
| `code-reviewer-B` | Reviews for conventions and codebase consistency — checks naming, test structure, error message text, and file organization against existing patterns. | `skills/feature-dev/agents/code-reviewer.md` |

All three run in parallel after implementation completes.

### Consolidated Findings

| Severity | Source            | Finding                                                                                                                                                                                                                    |
| -------- | ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| High     | `code-reviewer-A` | `formatResult` now accepts `null` but the `Result` type export in `src/types/index.ts` was not updated — downstream consumers may not see the updated signature.                                                           |
| Medium   | `code-simplifier` | The empty-string sentinel in `formatter.ts` is a leaky abstraction. The handler should check for `null` directly rather than checking for an empty string. The current approach splits the null concern across two layers. |
| Low      | `code-reviewer-B` | Test description in `handler.test.ts` says "returns 404" but codebase convention is "should return 404". Inconsistency with existing test names.                                                                           |

### Actions Taken

- **High** (fixed directly): Updated `src/types/index.ts` to export `Result | null` so downstream consumers are type-safe. — _Fourth file touched; noted as scope expansion in handoff._
- **Medium** (fixed directly): Removed the empty-string sentinel from `formatter.ts`. Handler now checks the processor result for `null` before calling `formatResult`, keeping null handling in one layer.
- **Low** (fixed directly): Renamed test description to `'should return 404 when processor returns null'` to match codebase convention.

---

## Handoff Artifact

Written to: `.agents/scratchpad/null-result-propagation/handoff-plan.md`

Key contents:

- Feature: null result propagation through formatter → processor → handler
- Track: Standard
- Files changed: `formatter.ts`, `processor.ts`, `handler.ts`, `types/index.ts` (scope expansion)
- Tests added: 3 new test cases (one per file)
- Open risks: None blocking. If additional processors are added later, they should return `Result | null` by convention — recommend adding a lint rule or base type constraint.

---

## How the Workflow Enforced Implementation and Review Requirements

### Implementation enforcement

Phase 5 of the skill contains an explicit rule:

> _Always use the tdd skill to implement with an explicit red-green-refactor loop. Treat this as required for Implementation on every track; do not bypass it._

This means no file can be edited without first writing a failing test, making it pass, then refactoring. The rule applies to **every track** — including Light. It is not optional based on feature size.

### Review enforcement

Phase 6 contains two unconditional rules:

1. > _Always launch an independent `code-simplifier` subagent to identify refactoring opportunities after implementation._

2. > _Always run independent `code-reviewer` agents for quality review on every track._

For the Standard Track specifically, "multiple independent code-reviewer agents in parallel" are required. The skill names the agents explicitly:

- **`code-simplifier`** — from `skills/code-simplifier/SKILL.md`. Always runs. Looks for DRY violations, dead code, unnecessary complexity.
- **`code-reviewer`** — from `skills/feature-dev/agents/code-reviewer.md`. Runs at least once on Light, multiple times in parallel on Standard and Deep.

The Standard Track in this eval used **three subagents in parallel**:

- `code-simplifier` (simplicity/DRY)
- `code-reviewer-A` (correctness/type safety)
- `code-reviewer-B` (conventions/consistency)

High-severity findings are fixed in the same turn. The skill does not create an artificial approval gate here — it says:

> _Fix obvious high-severity issues directly unless the user has asked to stop after review._
