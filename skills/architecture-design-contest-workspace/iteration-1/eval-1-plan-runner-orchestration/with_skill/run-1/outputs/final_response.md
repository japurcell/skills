# Problem framing

**Goal:** add a feature that can execute an already-saved plan, persist progress across runs, and trigger code-review agents at the right checkpoints.

**Non-goals:** replacing `create-plan` / `create-tasks`, inventing a repo-wide runtime, or moving state into benchmark workspaces.

**Hard constraints:**
- The existing workflow is file-backed under `.agents/scratchpad/<feature>/` (`skills/create-plan/SKILL.md:29-38`, `skills/create-tasks/SKILL.md:27-35`).
- `tasks.md` checkboxes are the current resumption contract and may be reverted by checkpoint integrity checks (`skills/implement-plan/SKILL.md:74-80`, `94-132`).
- Review orchestration already has a strict contract: code-simplifier + 3 code-reviewer agents, controller-owned scope, coverage gating (`skills/implement-plan/SKILL.md:134-167`, `skills/implement-plan/references/review-protocol.md:7-27`).
- `*-workspace/**/outputs/` are fixtures, not maintained source (`AGENTS.md:7-10`, `scripts/copilot-install.sh:17-29`).

**Assumptions:**
- “Saved plan” means a normal scratchpad package: `plan.md` plus companion artifacts, especially `tasks.md`.
- Any new persistent state should live next to those artifacts in `.agents/scratchpad/<feature>/`, not in a DB or workspace outputs.
- Checkpoint review should reuse the existing reviewer skills/agents rather than invent new ones.

**Decision criteria:** keep `tasks.md` authoritative, avoid monolith creep, make resume/debug behavior inspectable, and fit the repo’s composable-skill style.

# Codebase / research findings

A few facts drive the design:

1. **The pipeline already exists.** `create-plan` emits a planning package, `create-tasks` turns that into executable `tasks.md`, and `implement-plan` consumes the package phase-by-phase (`skills/create-plan/SKILL.md:80-98`, `skills/create-tasks/SKILL.md:63-71`, `skills/implement-plan/SKILL.md:39-65`).
2. **`tasks.md` is not just docs.** It encodes phases, task IDs, `[P]` parallel markers, and exact file paths, and `implement-plan` uses it as the resumable execution ledger (`skills/create-tasks/SKILL.md:83-168`, `skills/implement-plan/SKILL.md:74-80`).
3. **Checkpoints already exist, but they are validation checkpoints.** After each phase, the workflow verifies integrity and may revert a false `[X]` back to `[ ]` before continuing (`skills/implement-plan/SKILL.md:120-132`).
4. **Code review is currently end-loaded.** `implement-plan` runs mandatory code-simplifier plus three code-reviewer passes after implementation, over a controller-materialized `review_scope_files` list (`skills/implement-plan/SKILL.md:136-167`).
5. **The repo prefers file-backed artifacts over hidden state.** `feature-dev` uses `handoff-plan.md` for durable multi-turn context, which is the closest existing pattern for resumable orchestration metadata (`skills/feature-dev/SKILL.md:150-179`, `skills/feature-dev/references/handoff-plan-template.md:1-74`).

That leads to one big conclusion: the safest design is **not** “replace the workflow,” it is “add a control plane around the workflow.”

# Design A — Extend `implement-plan` directly

**What it optimizes for:** fastest path, smallest new surface area.

Add plan-running, durable progress state, and checkpoint review logic directly into `skills/implement-plan/SKILL.md`.

## Shape
- Keep one execution skill.
- Add a sidecar state artifact such as `.agents/scratchpad/<feature>/execution/state.json` or `state.md`.
- Inject review gates into the existing phase checkpoint block.
- Preserve the current final review as the last checkpoint.

## Why it fits
- `implement-plan` already owns readiness checks, task parsing, execution ordering, verification, checkpoints, and final review.
- It already understands the exact semantics that make resume safe.

## Friction / irreversible commitments
- This makes the most complex skill in the pipeline even bigger.
- The skill already carries a large behavior surface and dedicated evals; adding orchestration, persistence, and phase-review policy increases blast radius.
- Over time it becomes the place where every “just one more workflow rule” lands.

## Best use
Choose this only if the priority is shipping quickly and you are comfortable paying down coupling later.

# Design B — New `execute-plan` orchestrator skill over existing artifacts

**What it optimizes for:** clean boundaries, preserving the current pipeline, and a better default long-term shape.

Create a new skill, e.g. `skills/execute-plan/`, whose job is to orchestrate execution rather than absorb every behavior into `implement-plan`.

## Shape
- `create-plan` and `create-tasks` stay unchanged.
- `tasks.md` remains the canonical task ledger.
- New control artifacts live under `.agents/scratchpad/<feature>/execution/`, for example:
  - `state.md` or `execution-log.md`
  - `checkpoints/<phase>.md`
  - `reviews/<phase>.md`
- `execute-plan` owns:
  - loading/reconciling plan artifacts
  - deciding the next runnable phase
  - materializing checkpoint-scoped review scope
  - dispatching code-simplifier / code-reviewer agents at configured gates
  - advancing or reopening the phase
- `implement-plan` stays either:
  - a simpler execution worker for a phase, or
  - the reference behavior from which `execute-plan` is derived, if you do not want hard skill-to-skill invocation.

## Progress model
- **Authoritative:** `tasks.md` checkboxes.
- **Derived control-plane state:** execution artifacts that record phase status, last checkpoint, unresolved review findings, and next action.
- If the control artifact and `tasks.md` disagree, `tasks.md` wins.

## Why it fits
- It matches the repo’s composable skill style.
- It mirrors the durable-artifact pattern already used by `feature-dev`.
- It keeps review coordination as a controller concern, which matches the existing review protocol’s “controller owns scope, subagents do not recompute it” rule.

## Friction / irreversible commitments
- You now own two execution-oriented skills and need to explain when to use each.
- If you want `implement-plan` to be reusable as a sub-step, you may eventually refactor shared guidance into bundled references to avoid duplicated logic.

## Best use
This is the best fit if you want checkpoint reviews and durable execution state without turning the current executor into the repo’s monolith.

# Design C — Protocol-first split: execution protocol + pluggable runners

**What it optimizes for:** reuse across future workflows.

Define a small protocol layer first, then let multiple skills consume it.

## Shape
- Introduce a new bundled protocol in a skill such as `execute-plan`, for example:
  - `references/execution-state-template.md`
  - `references/checkpoint-policy.md`
  - `references/review-gate-policy.md`
- `implement-plan` remains the simpler “single-run executor.”
- `execute-plan` consumes the protocol for resumable execution.
- Future integrated workflows (for example, a richer `feature-dev` path) can also consume the same checkpoint/review contract.

## Progress model
- `tasks.md` still authoritative.
- Protocol artifacts define the shape of:
  - execution state
  - checkpoint evidence
  - review coverage records
  - reopen rules when review invalidates a supposedly complete slice

## Why it fits
- It acknowledges that the real reusable thing is not “one more skill,” but a stable contract for execution and review orchestration.
- It reduces the chance of drifting checkpoint behavior across future skills.

## Friction / irreversible commitments
- This is more architecture up front.
- You pay an initial documentation/contract tax before shipping the new capability.
- If overdone, it can become abstraction for abstraction’s sake.

## Best use
Choose this if you expect more than one workflow to need resumable execution + checkpoint review in the near future.

# Comparison

**Design A** is the cheapest to start, but it has the worst long-term shape. The current `implement-plan` already spans readiness gating, execution order, verification, checkpoints, review dispatch, and completion validation. Pushing saved-plan execution state and checkpoint review policy into the same skill is the shortest route to a monolith.

**Design C** has the cleanest theory, but I would not start there unless you already know a second consumer is imminent. In this repo, too much upfront protocol work risks feeling heavier than the actual problem.

**Design B** is the pragmatic middle. It keeps the existing plan/task workflow intact, respects the repo’s artifact-driven style, and creates a clear ownership split:
- `tasks.md` says what is done
- `execute-plan` says what phase/run state the workflow is in
- existing reviewer agents say whether the checkpoint is good enough to advance

That is also the safest answer to the checkpoint-scope problem. The orchestrator can materialize a checkpoint-specific `review_scope_files` list, while the final review still uses the current “all uncommitted changed files” rule.

# Recommendation

**I’d bet on Design B, with one piece borrowed from Design C.**

Concretely:
1. Add a new `skills/execute-plan/` skill.
2. Keep `tasks.md` as the only canonical completion ledger.
3. Add small, inspectable execution artifacts under `.agents/scratchpad/<feature>/execution/`.
4. Bundle the execution/checkpoint/review policy as references owned by that new skill, so the contract is explicit and reusable.
5. Keep `implement-plan` as the simpler baseline executor/fallback rather than stuffing every new behavior into it.

That gives you the right system shape for this repo:
- **modular** instead of monolithic,
- **file-backed** instead of hidden,
- **resume-safe** because `tasks.md` still wins,
- **review-aware** because checkpoint review is a first-class controller action.

If I were sequencing it, I’d ship it in two steps:
- **Step 1:** `execute-plan` with durable execution state + checkpoint records, but minimal new policy.
- **Step 2:** add configurable checkpoint review gates once the basic resume loop feels solid.

# Next design decision

Pick one of these:
- **Recommended:** Design B (new `execute-plan` orchestrator + scratchpad execution artifacts)
- **Fastest:** Design A (extend `implement-plan` directly)
- **Most reusable:** Design C (protocol-first split, then build `execute-plan` on top)
