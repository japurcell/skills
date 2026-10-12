# Software factory handoff

Historical snapshot: superseded by the planning scope in [the current handoff](handoff.md). Preserved for evidence; the prototype step below is not an active instruction.

Updated: 2026-10-12. Scope: software-factory.

## Next step

Build a minimal working Restate prototype with parallel reviews, bounded repairs, and human checkpoints. Package it through a skill and test crash recovery, stale approvals, and duplicate publication.

This session only records the next step. Implementation has not started. On resume, verify and pin the Restate server and TypeScript SDK versions, then define the end-to-end failure cases in disposable repositories before implementing the runtime.

## Current state

- Initial research and interactive architecture documents are complete. Repo Runner, Durable Graph, and Event Factory were compared.
- The user selected Restate for the next working prototype. This is not a production runtime commitment.
- Existing HTML workflows are simulations. Chat code sketches contain placeholder factory helpers and have not been compiled or tested.
- No working Restate or DBOS implementation exists. SDK/server versions and the final installable skill path remain open.
- The worktree was clean before this handoff was added.

## Design constraints

- Keep deterministic ordering, gates, limits, evidence checks, approval validation, and publication policy in code. Give agents planning, implementation, review, and repair reasoning.
- Install through a skill into arbitrary repositories. Keep runtime dependencies isolated from the target application's dependency manifest.
- Preserve customizable workflows. Cross-harness support is an eventual goal; one real adapter plus deterministic fixtures is a proposed minimal scope.
- Prefer robustness, simplicity, scalability, and maintainability over development cost.
- Durable orchestration does not make external CLI, Git, or API effects exactly once. Reconcile effects and supervise processes explicitly.

## Proposed minimal workflow

1. Generate a plan, then wait at a durable human plan checkpoint.
2. Implement a candidate in an isolated workspace.
3. Run tests, correctness review, and security review in parallel against the same immutable revision. Use fresh review sessions and read-only review snapshots.
4. Join evidence in code. Missing, failed, or stale evidence cannot pass.
5. Repair failures within a fixed budget, then repeat relevant checks. Earlier sketches used three repairs after the initial candidate, allowing four validation rounds.
6. Present passing evidence at a human candidate checkpoint with approve, revise, and stop decisions. Human-requested revisions consume the same repair budget.
7. Publish only the approved candidate through an idempotent, reconciled external operation. Exhaustion leaves the run incomplete and requires attention.

Separate infrastructure retries from quality repairs. Bind approvals to the run, checkpoint, candidate SHA, workflow/policy version, and evidence digest. Any candidate change requires fresh evidence and approval. Keep runtime completion distinct from factory acceptance.

## Required proof

- **Crash recovery:** kill the worker around review completion and result persistence. Restart without losing recorded evidence or accepting obsolete attempt results. Verify human waits also survive restart.
- **Stale approvals:** change the candidate after a checkpoint is presented. Reject the old decision without resolving the current gate.
- **Duplicate publication:** publish successfully, then crash before recording the receipt. Restart and reconcile the destination; exactly one publication artifact must exist.
- **Bounded repairs:** repeated failed reviews and human revision requests exhaust the configured budget without publication.
- **Skill installation:** install and run in a clean disposable repository without changing its application dependencies.

A persisted run history should remain inspectable without executing tools. The eventual live/history UI should expose agent activity and available usage data.

## Packaging and runtime notes

Proposed package: a skill, deterministic installer, pinned runtime manifest, and workflow/prompt/config templates. The repository owns its workflow code and configuration; an isolated managed location owns runtime dependencies, server data, artifacts, and workspaces. Preserve unfinished runs and their compatible workflow bundles during upgrades.

Restate needs a server plus a Node worker endpoint registered with that server. Prior research used durable steps, Restate promise combinators, and named durable promises resolved by shared handlers for human decisions. Verify these APIs against the pinned release. Explicitly bound infrastructure retries; do not assume defaults are finite.

Super Simple Software Factory already puts phases and gates in Python code; its YAML configures agents. The inspected version did not establish automatic workflow checkpoint recovery. DBOS remains a comparison option; its TypeScript runtime requires PostgreSQL.

## Evidence and recovery

- [Review guide and prior validation scope](README.md)
- [Research synthesis](research.md)
- [Durable Graph interactive prototype](prototypes/durable-graph.html)
- [Super Simple Software Factory source study](research/super-simple-software-factory.md)
- [Harness adapter research](research/harness-adapters.md)
- Official Restate references: [installation](https://docs.restate.dev/installation), [durable steps](https://docs.restate.dev/develop/ts/durable-steps), [concurrency](https://docs.restate.dev/develop/ts/concurrent-tasks), [external events](https://docs.restate.dev/develop/ts/external-events), [error handling](https://docs.restate.dev/develop/ts/error-handling).

Earlier validation covered simulated scenario paths and document interactions, including annotations and export/import. It did not test a real factory runtime. That UI validation was not rerun for this handoff.

To serve the documents, run from `/Users/adam/.codex/worktrees/ea58/skills`:

```sh
rtk proxy python3 -m http.server 8765 --bind 127.0.0.1 --directory docs/software-factory
```

Open `http://localhost:8765/prototypes/durable-graph.html`. Server status was not checked this session. Annotations are browser-local and origin-specific; retain the hostname and port or export notes before changing origin.
