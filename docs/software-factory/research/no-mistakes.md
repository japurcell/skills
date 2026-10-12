# no-mistakes: validation pipeline research

Research date: 2026-10-08 (America/Los_Angeles). Repository: [kunchenguid/no-mistakes](https://github.com/kunchenguid/no-mistakes).

## Evidence and snapshot limits

The cached commit view exposed `d89e633f28dec6ad92bf8bc138b6e1b3bf563061` dated 2026-09-05, but inspected main-branch pages appeared newer. This is not a consistently pinned snapshot. Links below identify inspected files on `main`; future implementation should pin and recheck them. GitHub Contents API was unavailable, so file listings supplied path discovery. No upstream code or tests were run.

## What the implementation contributes

The Go application is a local daemon, CLI, and TUI with SQLite state. This demonstrates a skill as an invocation layer over an ordinary executable. [Dependencies](https://github.com/kunchenguid/no-mistakes/blob/main/go.mod)

The executor persists run and step records, traverses an ordered step list, handles approval waits, and accepts bounded restart requests to earlier steps. A restart clears subsequent step state before replay. This is a concrete code-owned lifecycle. [Executor](https://github.com/kunchenguid/no-mistakes/blob/main/internal/pipeline/executor.go)

Steps return typed outcomes including approval, skip, restart, findings, exit status, and a reviewed commit identity. Agents provide evidence or findings within the lifecycle; the executor interprets outcomes. [Step contract](https://github.com/kunchenguid/no-mistakes/blob/main/internal/pipeline/pipeline.go)

The documented core pipeline is `intent -> rebase -> review -> test -> document -> lint -> push -> pr -> ci`. Review output must cover the trusted changed-file set; malformed output receives bounded retries. Process failures and schema errors are different conditions. Review repair is disabled by default and needs a decision; later review uses a fresh session. Test combines configured command results with typed scenario evidence and explicit inconclusive outcomes. Evidence lives outside the worktree. Tests should rely on independent behavioral oracles, but that rule is prompt guidance, not a mechanical proof of test quality. Worktree confinement is also described as a soft boundary, not an OS sandbox. [Pipeline reference](https://github.com/kunchenguid/no-mistakes/blob/main/docs/src/content/docs/reference/pipeline-steps.md)

## Customization and adapters

The workflow is fixed and linear. Repository configuration can add at most 16 command gates at named anchors, but cannot reorder or replace core steps. Executable and agent-selection policy normally comes from a trusted default-branch copy; the run resolves its gate list at startup. This is a useful pattern for protecting policy from the branch under evaluation, but a poor direct fit for arbitrary graphs. [Repository configuration](https://github.com/kunchenguid/no-mistakes/blob/main/docs/src/content/docs/reference/repo-config.md)

The documented adapter roster includes Codex, Copilot, OpenCode, and Pi, with additional agents through an ACP bridge. Configured process failures may select a fallback within the remaining timeout; malformed findings do not trigger fallback. This distinguishes changing the execution harness from retrying semantic work. These integrations were inspected, not executed. [Global configuration](https://github.com/kunchenguid/no-mistakes/blob/main/docs/src/content/docs/reference/global-config.md)

`no-mistakes init` installs user-level skill entry points into Claude and vendor-neutral skill locations. The CLI exposes historical runs, per-step logs, and usage statistics. Unknown token values remain distinct from zero. [CLI reference](https://github.com/kunchenguid/no-mistakes/blob/main/docs/src/content/docs/reference/cli.md)

## Observability and learning

The TUI exposes current steps, streamed output, findings, diffs, and CI activity. This is operational observability, but not proof of a normalized trace for every prompt, response, tool payload, and skill. [TUI guide](https://github.com/kunchenguid/no-mistakes/blob/main/docs/src/content/docs/guides/tui.md)

Invocation metrics deliberately summarize tool categories and omit raw prompt, output, diff, and command payloads from the metrics store. This does not mean all step logs lack agent output. Full drilldown needs a separate artifact contract, explicit retention, and reliable skill instrumentation. [Metrics implementation](https://github.com/kunchenguid/no-mistakes/blob/main/internal/agent/invocationmetrics.go)

The evaluation system captures adjudicated review cases after runs complete, preserving provenance and unresolved labels. It can replay explicit candidates against frozen cases, use a held-out set, and compare review quality, usage, and duration. Replay covers Review, not the full factory, and does not automatically promote prompts or policies. This is measured improvement, not unrestricted self-modification. [Evaluation reference](https://github.com/kunchenguid/no-mistakes/blob/main/docs/src/content/docs/reference/eval.md)

## Mechanisms to carry forward (design proposals)

1. Give a deterministic controller sole authority over transitions and acceptance.
2. Freeze trusted workflow and policy versions for each run.
3. Keep malformed output, failed quality, absent evidence, and process failure distinct.
4. Bind every review result and approval to the code revision it evaluated.
5. Repair in a bounded loop, then independently revalidate the changed state.
6. Store evidence outside the branch being tested.
7. Evaluate proposed changes against adjudicated cases and a held-out set before promotion.

## Architecture implications

A repo runner can borrow the typed outcome and gate contract. A durable graph can generalize persisted steps into dependencies and approved loops. An event factory can preserve the same contract across workers, but would need leases, duplicate handling, and shared integration controls that this research does not establish upstream.

The proposed shape is: skill entry -> trusted runtime -> versioned workflow -> command or agent step -> typed evidence -> acceptance policy. Events and artifacts feed live/history views and a separate evaluation workflow. Broad trace capture, arbitrary graphs, measured full-run improvement, and cross-repository scheduling remain design work.

## Open questions

Can an interrupted tool operation be reconciled before retry? Which adapters expose skill loading rather than inferred file reads? How should shared policies coexist with local customization? How many evaluation labels require manual adjudication? These need implementation experiments.
