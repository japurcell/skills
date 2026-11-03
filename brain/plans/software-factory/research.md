# Agentic workflows and software factory: initial research

Research date: 2026-10-08 (America/Los_Angeles). Status: architecture exploration, with no production architecture selected. Start the visual review at [the interactive comparison](prototypes/index.html).

## The design center

Build a deterministic runtime that invokes reasoning agents. Installing a skill should make that runtime discoverable and easy to use. The skill should not be the only place where required transitions, retries, approvals, or acceptance rules exist.

This is our design conclusion, informed by three inspected repositories and Shopify's first-party writing. It does not imply that any one reference already satisfies the whole brief. Repository research was source inspection; no upstream code or tests were run.

## Requirements carried forward from the idea

- Install through a skill in arbitrary repositories, with project-specific settings and prerequisites detected explicitly.
- Support several named, customizable workflows: planning, implementation, checkpoints, prototypes, reviews, and repair loops.
- Learn from completed runs, while distinguishing memory accumulation from measured improvement.
- Route independently across coding harnesses and models, including Codex, GitHub Copilot, Gemini CLI, OpenCode, and Pi.
- Observe every active workflow, then inspect historical runs through the same interface.
- Drill into prompts, responses, tool calls/results, skill evidence, errors, artifacts, and usage when the harness exposes them.
- Keep deterministic behavior in code and reasoning in agents.
- Deliver alternative architecture prototypes as interactive HTML documents with durable, exportable annotations.

Local-first execution is an exploration assumption, not a settled requirement. Cross-repository concurrency and long unattended runs are the main reasons to consider stronger coordination. The documents show proposed behavior with simulated data; they do not invoke agents.

## What each reference teaches

| Source | Strongest contribution | Important boundary |
| --- | --- | --- |
| Super Simple Software Factory | Explicit Python phases, typed agent results, bounded correction, SQLite traces, and skill-carried templates/UI | The inspected implementation uses Pi; process/session continuity is not durable workflow recovery. |
| no-mistakes | A persisted executor, typed outcomes, strict evidence handling, approval/restart boundaries, and review evaluation | The core workflow is fixed. Review evaluation does not measure or improve the entire factory. |
| Noodle | Agents propose work; Go validates and dispatches it. An optional Markdown brain separates reflection and consolidation | Memory admission is largely prompt-guided; measured cross-run improvement was not established. |
| Shopify Helix | Small checkpoints, evidence gates, isolated reviewers, and feedback | Internal source and crash-recovery mechanisms are unavailable. |
| Shopify Roast | Declarative workflows that interleave code and agent steps | First-party documentation was reviewed; the current runtime was not audited or executed. |

Evidence: [SSSF runner](https://github.com/disler/super-simple-software-factory/blob/de31374882e7a4e3e5b7bb9bd09e69dc2f779356/.claude/skills/sssf/templates/adws/adw_modules/runner.py), [no-mistakes executor](https://github.com/kunchenguid/no-mistakes/blob/main/internal/pipeline/executor.go), [Noodle loop](https://github.com/poteto/noodle/blob/82d2921c52370f23f29086de81ccfb600939c037/loop/loop.go), [Helix](https://shopify.engineering/helix), [Roast](https://shopify.engineering/introducing-roast).

The supplied video is AI LABS' reconstruction of Helix. Its transcript was retrieved and reviewed. Its critic/fixer pairing and final human-review timing differ from Shopify's two-reviewer and default checkpoint-approval description. Keep those choices distinct. [Video](https://www.youtube.com/watch?v=bBMp5tLxShQ), [source comparison](research/shopify.md).

## Three architectures to explore

### A. Repo runner

A skill launches a repo-local executable. Ordinary code defines named recipes using a small step API. One process schedules work, writes an append-only journal, and records artifacts in a local store. A local UI queries those records. Agents propose plans and produce patches; code owns transitions, validators, attempt limits, and acceptance.

This is the closest fit to installing the factory as a skill and keeping runtime semantics easy to audit. It supports custom logic without inventing a large workflow language. The tradeoff is explicit recovery work: a recorded agent session alone cannot establish whether a partly completed tool action should run again. A process restart must reconcile external effects before resuming. Cross-process contention requires a repo lock, and cross-repo scheduling is a separate concern.

Question to test: can one well-designed local runner provide sufficient durability and customization for the actual workload? [Interactive design](prototypes/repo-runner.html)

### B. Durable checkpoint graph

A skill submits a versioned workflow to a local service. The graph declares dependencies, command steps, agent steps, human gates, and bounded repair subflows. A durable state machine records runs, steps, attempts, leases, and evidence. Workers execute outside the coordinator. The UI renders the graph and persisted events.

This is the leading candidate for long runs, multiple workflows, and checkpoint review. Parallel independent steps become explicit, while joins enforce evidence from the same revision. Durability means more than storing JSON: the implementation needs atomic claims, fenced attempts, resumable waits, and reconciliation of uncertain side effects. A graph also becomes a language whose versioning and migration rules must stay comprehensible.

Question to test: can a stopped controller recover the right work without duplicating actions or accepting stale evidence? [Interactive design](prototypes/durable-graph.html)

### C. Event-driven factory

A skill submits intent to an event log and work queue. An agent proposes work; a deterministic admission service validates it. Independent specialist workers claim jobs, emit results, and react to explicit event rules. A coordinator enforces gates and serializes integration. Read models project the same events into live and historical views. A separate learning worker proposes improvements.

This is useful when work arrives continuously across repositories or teams, and when independent workers matter more than a single readable graph. It has the largest correctness surface: duplicate delivery, out-of-order events, stale claims, backpressure, conflicting writes, and eventual consistency. An agentic planner is optional; policy still owns admission and dispatch. Add this complexity only when the workload requires it.

Question to test: can autonomous workers cooperate without duplicate publication, conflicting ownership, or hidden state? [Interactive design](prototypes/event-factory.html)

## Shared contracts worth deciding before the engine

**A run freezes its inputs.** Record source revision, workflow revision, prompt/skill hashes, routing policy, permission profile, and context bundle. Edits apply to a future run or an explicit versioned migration.

**An attempt is not a step.** A step may have several attempts. Each gets its own identity, workspace, evidence, usage, and terminal result. Separate process retries, malformed-output repair, and quality repair. Attempt exhaustion pauses or fails according to policy; it never becomes success.

**Evidence is revision-bound.** A result includes status, revision, command or reviewer identity, artifact references, and completeness. Missing evidence is unknown. Relevant code changes invalidate older reviews and approvals. Passing a deterministic command establishes that command's result, not semantic correctness of the entire product.

**Publishing is a distinct effect.** Before a commit, merge, or PR action, record intent and an idempotency key. After an uncertain interruption, inspect the external outcome before retrying. Worktrees isolate Git changes; OS/process controls provide the execution boundary.

**The event contract serves live and history.** Record an event ID, run/step/attempt IDs, sequence, timestamp, kind, actor, source revision, adapter version, payload reference, and observation quality. A live connection tails persisted records after a cursor. Historical playback renders records without rerunning tools. Large artifacts remain separately addressable. Unknown usage stays unknown.

**Adapters advertise what they expose.** A routing policy selects a capability-compatible harness, then an available model and effort. It records its reason and fallback. A requested skill is not necessarily a loaded skill; the UI should distinguish observed, inferred, and unavailable information. [Adapter feasibility and primary references](research/harness-adapters.md)

## Learning without giving agents control of policy

Use three stages: capture evidence, propose a change, measure it. Store candidate lessons with source run, scope, confidence, counterexamples, and expiry. Evaluate prompt, routing, and workflow candidates against adjudicated cases and a held-out set. Compare completion quality and regressions before speed or token usage. A prior run's success alone is weak evidence.

Promotion should be a deterministic policy: low-risk context updates may auto-promote after preauthorized checks; workflow gates, executable policy, permissions, or publication rules require the configured review boundary. Keep versions and a rollback path. Run this as a normal workflow so its own inputs, reasoning, evidence, and acceptance are inspectable. None of the references establishes this full loop for the proposed factory.

## Recommendation and first experiments

Prototype B first if overnight runs and several workflows are central. Borrow A's small install footprint and inspectable code steps. Keep C as a distinct option for a genuine multi-repository workload. This recommendation is architectural judgment, not a benchmark result.

Before selecting an implementation stack, prove these boundaries in disposable repositories:

1. Run one small change through two harnesses and compare the same normalized trace and result contract.
2. Stop execution before and after an external effect; resume without duplicate publication or lost state.
3. Change code after review; show that stale verdicts cannot satisfy the new revision's gates.
4. Exhaust a repair budget; keep the task incomplete and make the next owner action clear.
5. Replay a completed run in the UI with no tool execution.
6. Propose one memory or prompt improvement; reject it when held-out outcomes regress.

The annotated prototypes answer which model feels right. These later experiments would answer whether it works.

## Evidence inventory and remaining uncertainty

- [SSSF report](research/super-simple-software-factory.md): pinned snapshot `de31374882e7a4e3e5b7bb9bd09e69dc2f779356`.
- [no-mistakes report](research/no-mistakes.md): mixed cached main-branch views; exact snapshot consistency is unverified.
- [Noodle report](research/noodle.md): pinned snapshot `82d2921c52370f23f29086de81ccfb600939c037`; latest live branch status is unverified.
- [Shopify/video comparison](research/shopify.md): first-party descriptions and a retrieved auto-generated video transcript; no private implementation access.
- [Harness feasibility](research/harness-adapters.md): current docs plus local Codex CLI help, not live integration tests.

Noodle's documented same-order parallel stage groups conflict with the inspected dispatch helper. SSSF's visualizer documentation and skill scope differ. Those discrepancies reinforce the need to test executable semantics instead of adopting documentation wholesale. Full trace parity, Windows portability, distributed recovery, and measured learning remain open validation work.
