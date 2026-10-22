# Change and audit recipe qualification

Status: fake-mode behavior qualified on 2026-10-22 against the T7 public workflow seam from base `974bfef4`. Milestone 5 live acceptance remains pending a qualified T8 provider. No live provider, publication, install, adoption or learning operation ran for this task.

## Authoring and input contract

Copy both `templates/workflows/change.ts` and `templates/workflows/audit.ts` into the repository's `.factory/workflows/` directory. Audit imports small ordinary-code helpers from change. Copy `templates/prompts/` to `.factory/prompts/` and customize `templates/agents.json` as `.factory/agents.json`, replacing `SELECT_QUALIFIED_HARNESS` with an explicitly qualified provider mode. The placeholder intentionally fails if used directly. Model and reasoning selections remain optional explicit profile choices. Workflows compile once per invocation using the installed pinned toolchain.

Change accepts a nonempty `prompt`, a prose `plan`, or a structured `plan` containing `steps` with nonempty `title`/`prompt` and optional boolean `skip`. Skipped steps are removed from agent context. `planning: true` enables a report phase; `implement: false` skips implementation. `review: false` explicitly skips review. These are ordinary TypeScript recipes, so their phases and result validators can be edited directly.

`checks` is an ordered array of unique named `{name, argv, cwd?, env?, timeoutMs?}` commands. Arguments are passed as data; the recipe does not construct a shell string. The recipe rejects every other check field before launching a workflow phase, including runtime-only `shell`, `childScope`, `required`, `intent`, `priorAttemptId` and `loopKey`. It forwards only the documented command fields plus its own controlled lineage and `required: false`. Optional `cwd`, `env` and `timeoutMs` values are validated and remain available. Selected deterministic E2E commands are checks. Ordinary nonzero command exits become concrete findings; spawn, permission, timeout, capture, protocol and unresolved cleanup failures remain terminal runtime failures. A missing check cannot appear in the returned passing check list.

`agents` supplies independent `planning`, `implementation`, `review` and `repair` phase fields for change. Each can select a named profile, prompt/file, model, reasoning, skills, permissions and timeout through the existing public contract. Recipe defaults use write permissions for implementation/repair and read-only permissions for analysis/review. Final targeted invocation overrides retain the accepted highest precedence. Every review starts a fresh conversation. Browser exploration is skipped unless `browserVerification: {enabled: true, agent?: phaseFields}` explicitly selects it.

Audit accepts explicit `scopes: [{name, target, questions?, skip?, agent?}]`. A target may describe a ref/branch, files, subsystem or investigation question. The recipe passes the target as analysis context and never changes branches or fabricates an implementation task. Investigations are followed by optional synthesis (`synthesis: false` skips it), selected checks, optional explicit browser verification and independent review. Audit phase options are `planning`, `investigation`, `synthesis`, `review` and `repair`. Every audit phase defaults to read-only; an audit check or effective agent override that changes the local candidate causes failure. Report corrections change the returned report only.

Example change input:

```json
{
  "plan": {"steps": [{"title": "Clarify example", "prompt": "Update the disposable fixture text"}]},
  "planning": true,
  "agents": {"planning": {"profile": "planner"}, "implementation": {"profile": "implementer"}, "review": {"profile": "reviewer"}},
  "checks": [{"name": "selected-tests", "argv": ["npm", "test"]}]
}
```

Example audit input:

```json
{
  "prompt": "Audit validation behavior",
  "scopes": [
    {"name": "main-history", "target": "main", "questions": "Inspect validation history"},
    {"name": "candidate-files", "target": "src/validation", "questions": "Check current input boundaries"},
    {"name": "optional-ui", "target": "web", "skip": true}
  ],
  "agents": {"investigation": {"profile": "auditor"}, "review": {"profile": "reviewer"}}
}
```

## Results, correction and follow-up

Control payloads use the runtime's authoritative final envelope. Summary phases require `{summary: nonemptyString}`; review/browser phases additionally require `findings: string[]`. Empty findings accept the candidate. The helper permits exactly one format correction with saved result-capture ID, diagnostic and original context. Format correction has no code-edit rights and never repeats implementation. A valid `needs_input` propagates immediately without format correction. An invalid correction, missing permissions, unsupported provider/profile or infrastructure failure ends the invocation; there is no retry or fallback loop.

Each recipe allows two quality corrections, then fails with concrete findings. Selected checks rerun after every repair. A failed check gates review, and every reviewer finishes before repair can begin. Repeated reviews and no-op repairs consume the existing shared allowance. Audit uses the existing `code_correction` accounting intent for report-quality correction; its effective permissions default to read-only.

Successful reports contain `status`, candidate summary/fingerprint, actual selected check results, correction count, explicit skipped phases and `priorAttempts`. Audit also returns each named investigation. Saved runtime inputs/results retain full review and correction evidence. To explicitly invoke current code in joined history, pass the saved report's `priorAttempts` along with the existing run/worktree IDs. After a failed invocation, obtain the latest operation-to-attempt IDs from public saved history instead. Stable operation keys and explicit lineage preserve the shared twenty-additional-attempt allowance and two-per-loop code allowance. Renaming work is not a supported way to renew lineage.

## Candidate freshness boundary

Before and after independent review/browser phases, all writers have settled and the recipe compares local candidate fingerprints. Audit also checks investigation, synthesis, report correction and selected check phases for mutation. Format-only corrections have the same mutation guard. Root `.git` metadata is excluded; local paths, file modes, content byte lengths/digests and symlink identities are included. File contents use separate SHA256 digests and unambiguous JSON records, preventing adjacent files from impersonating each other's metadata.

Candidate snapshots use asynchronous filesystem traversal and 64 KiB streamed reads so they yield to the foreground event loop. Optional `snapshot: {maxEntries?, maxBytes?, timeoutMs?}` has defaults of 100000 entries, 1 GiB total content and 10000 ms monotonic scan time. Entry/byte counts must be positive safe integers; duration must be finite and positive. Budgets are checked during directory enumeration and every read, including a growing file. Exceeding a budget fails actionably without retry or quality correction. These are per-snapshot resource limits, separate from agent/command/workflow timeouts. JavaScript deadline checks cannot interrupt a blocked native filesystem syscall. Opens request no-follow/nonblocking flags where supported; descriptor/path identity and metadata are checked before and after reading, and directories are rechecked. Unsupported special files, unreadable files and observed unstable reads fail without retry. The fingerprint is a best-effort freshness check, not an atomic filesystem snapshot or permission boundary. Symlink targets outside the worktree are not read, independently authorized transient edits that are restored between observations are not detectable, and external/native filesystem stalls remain subject to operating-system behavior. Customize ordinary recipe code for a repository's explicit source boundary when needed. Provider-enforced permissions and runtime process cleanup remain separate safeguards.

## Reproduction and evidence

Working directory: `packages/software-factory` in this worktree. Locked dependencies were already installed offline. Exact runtime used:

```text
/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/factory-qualified-node-i2fv29e3/node-v24.22.1-darwin-arm64/bin/node
```

Prepend that runtime's `bin` directory to `/opt/homebrew/bin:/usr/bin:/bin` for npm. Run commands through RTK. Native process inspection is required; sandbox `ps`/`sysctl` rejection is invalid environment evidence.

```sh
rtk npm run typecheck
rtk npm run build
rtk proxy node --test test/workflows.test.mjs
rtk proxy node --test test/adapters.test.mjs test/startup.test.mjs
```

The workflow suite is intentionally not registered by this task. The integration owner registers `test:workflows` after independent review; use the explicit test path above until then.

Observed workflow result: 24/24 public subprocess E2Es passed in 27.73 seconds. They cover useful change/audit, passing/failing selected checks and gating, two corrections then pass/exhaustion, rechecks, fresh reviews, format correction/read-only rights and invalid-again termination, valid needs-input, permission/unknown-cleanup/spawn failures, no-op charges, optional selected work, independent phase inputs, explicit browser verification, twenty additional attempts across joined history, retained exhausted quality loops audit mutation rejection, bounded snapshot entry/byte/time policies, generated candidate growth beyond policy and invalid-policy rejection. An independent review found an ambiguous fingerprint serialization; its public reproducer failed before the digest/length fix and passed afterward. The explicit effective-review override mutation scenario also passed separately after its final test update.

Observed strict package typecheck/build: passed. Separate template compilation used `strict`, `exactOptionalPropertyTypes`, `noUncheckedIndexedAccess`, `verbatimModuleSyntax`, NodeNext and the public `dist/workflow.d.ts` mapping: passed. Each public E2E also compiles the copied recipes through real `invoke` using the production workflow builder.

Existing adapter/startup regression result: 83/83 passed in 51.17 seconds.

Security repair proof on 2026-10-22: public change and audit invocation tests were red before the check boundary fix. With `shell: "/bin/sh"` supplied in a check, change returned success after executing the shell payload; audit detected the resulting candidate mutation only after execution. Both now reject the unsupported field before any workflow attempt. Public cases also reject caller-supplied `required`, `intent`, `priorAttemptId`, `loopKey`, `childScope`, arbitrary and `__proto__` fields, and reject malformed optional `cwd`, `env` and `timeoutMs`. A supported check writes the literal argument `hello; touch injected.txt` with no injected file and retains `cwd`, `env` and `timeoutMs` behavior. The pinned-runtime `rtk proxy node --test test/workflows.test.mjs` passes 30/30; `rtk proxy node --test test/adapters.test.mjs test/startup.test.mjs` passes 83/83 with native process inspection. `rtk npm run typecheck`, `rtk npm run build`, separate strict NodeNext template compilation against `dist/workflow.d.ts`, and `rtk git diff --check` pass. The first sandboxed build could not write ignored `dist/`; the approved private-worktree build passed. No runtime command API was changed.

Official API references checked against the documented Node v24.22.1 pages: [filesystem and no-follow/descriptor APIs](https://nodejs.org/docs/latest-v24.x/api/fs.html), [incremental hash APIs](https://nodejs.org/docs/latest-v24.x/api/crypto.html). No dependency, shared runtime API, scheduler, database, package script or build configuration was added.

## Remaining acceptance

The owner must integrate/register this suite and run the combined milestone proof. A harmless live change plus read-only audit using a qualified T8 mode remains pending. No live provider support or milestone completion is claimed by the fake harness. Stop before learning workflows.
