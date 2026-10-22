# T5 foreground invocation evidence

Verified locally on 2026-10-21 with Node 24.22.1 darwin-arm64, Git 2.54.0,
TypeScript 7.0.2 and @types/node 24.19.2 on the qualified APFS placement.
This is development invocation evidence, not milestone 3 or release acceptance.

## Public entry points

`invoke --repository PATH --workflow .factory/workflows/FILE.ts --input JSON_FILE
(--new-worktree [--ref COMMIT] | --worktree ID_OR_PATH) [--run RUN_ID]
[--question CAPTURE_ID] [--context CAPTURE_ID ...] [--json]` starts the current
workflow from entry. `history --repository PATH --invocation ID [--json]`
returns invocation, worktree, attempts, captures and accounting. Help retains the
development label. Missing required CLI arguments exit 3 without starting work.

New worktrees come only from the resolved selected commit. Their absent path is
reserved in the store, then exclusively claimed, before Git creates it. Explicit
reuse checks the Git common directory, registration and stored identity, and
preserves tracked, staged and untracked edits. IDs and registered Git paths work.
Neither history nor a joined run restores executable state.

The workflow exports `run(context, inputs)`. `WorkflowContext` is available as a
type-only import from `@local/software-factory`; native ESM relative `.js` imports
resolve their ordinary TypeScript source files. Context supplies `worktree`,
`scope(name, async context => ...)`, `command(name, options)`, `progress(text)`,
`needsInput(question, context)` and `agent(name, options)`. Agent calls fail
explicitly without fabricating an attempt or result until T7/T8 exist.

Commands accept `argv: string[]`, optional worktree-contained `cwd`, explicit
`env: Record<string,string>` (default PATH only), and optional absolute `shell`.
No shell is selected implicitly. `intent`, `priorAttemptId` and `loopKey` use the
existing store admission rules. Joined-run repeated work must explicitly supply
its intent and prior attempt. Startup build operations have an invocation-scoped
identity and command-only admission during `starting`; no agent is admitted.

## Shared installation contract for T15

The explicit installer must create `<git-common>/factory/toolchain/manifest.json`
and its `node_modules` before startup. The manifest shape is:

    {"schema":1,"node":"24.22.1","typescript":"7.0.2",
     "dependencies":{"@types/node":"24.19.2"}}

Additional declared workflow dependencies appear as exact package/version pairs
in `dependencies`, with matching installed package versions. `.factory/package.json`
must declare `type: module`; declared dependencies/devDependencies must match the
shared manifest and installed versions. Startup validates these files and never
runs a package manager, downloads, rewrites locks or installs application packages.
Tests assemble this environment only inside disposable Git fixtures by copying
the pinned development dependencies installed offline with scripts disabled.
No real repository installation or generic installer integration was performed.

After claiming its worktree, startup creates `.factory/node_modules` as a link to
the shared environment only when absent. An existing exact link is reused;
conflicting user-owned scaffolding is refused without replacement. Each invocation
builds once into `<git-common>/factory/builds/INVOCATION_ID`, with native ESM output,
a generated tsconfig and a link to that same environment for runtime imports.
Neither application node_modules nor application lockfiles are modified.

## Observed checks

In `packages/software-factory`, with the qualified Node directory first on PATH:

- `npm run typecheck`: both source and qualification checks passed.
- `node scripts/build.mjs`: runtime plus public declaration build passed.
- `node --test test/startup.test.mjs test/store.test.mjs test/capture.test.mjs test/recording-integration.test.mjs test/fixtures.test.mjs`: 45 passed, 0 failed/skipped.

Fourteen startup tests cover committed helper imports and dirty source/index
preservation, compiler failure before phases/agents, absent and mismatched
dependencies, malformed inputs, invalid refs, missing/foreign references,
current-entry reuse, scaffold collision, shared runtime imports, pending command
drainage, explicit same-run followup and saved question/context references.

The first public CLI test failed with startup exit 3 before implementation.
Additional public reproductions exposed emitted-code dependency resolution and
unawaited-command finalization races; both now pass. Tests use real compiler and
command subprocesses, not substituted successful builds. Existing 27 store,
capture and composed checks and four harness/Git fixtures also pass unchanged.
Parent owns CLI smoke and package test-registry integration.

## Cleanup limits and remaining ownership

A normally closed POSIX command releases occupancy only when its owned process
group is absent. A live descendant after parent exit is tested: cleanup stays
unknown, ownership/capacity remain occupied and invocation exits 1. Windows
commands conservatively retain unknown cleanup until native scope support exists.
No saved PID is used for runtime cleanup or takeover.

T6 still owns bounded timeout/cancellation, signals, peer interruption, inherited
pipes held open by descendants, process identity qualification and manual
clearance. Pending command promises drain before normal finalization, but long
running activity is not yet bounded by that future shutdown controller. Recorder
failure preserves uncertainty. No executable resume, automatic retry, live
harness call, release publication or native cross-platform support claim occurred.

Official sources used for implementation choices:
[Git worktree](https://git-scm.com/docs/git-worktree/2.54.0) and
[TypeScript NodeNext modules](https://www.typescriptlang.org/tsconfig/module.html).

Reflection: races and shared ESM resolution are encoded in public tests. Remaining
findings are task-specific and captured here for T6/T15; no brain write was needed.
