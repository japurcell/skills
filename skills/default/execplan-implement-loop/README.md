# Maintaining execplan-implement-loop

The runtime is portable within this bundle. It uses Python 3.12+ standard library on macOS/Linux and real Git. No package installation, user Git configuration changes, or provider log scraping occurs.

## Readiness and reviewed policy

The adapter pins Gemini CLI **0.65.0**. Before a prompt, the runner checks `gemini --version` exactly and verifies required local skill files. Use `--doctor` for a no-prompt diagnosis. Doctor inspects the plan, Git state, provider version, required skill files, selected policy, and limited conventional user/workspace configuration paths. It does not activate skills, run acceptance commands, create runner state, or change files.

Doctor returns one JSON object with `status: "diagnosed"`, a `readiness` snapshot, and `blockers`. `readiness.status` is `blocked` or `unknown`; it never means ready. Exit 0 with `can_attempt: true` means no known local blocker, not that authentication, trust, effective permissions, or paid use are available or authorized. The normal runner refreshes readiness before each new provider iteration, including a resume that needs a provider. Completed and commit-only recovery does not need provider prerequisites. See [protocol](references/protocol.md) for report fields and exit meanings.

Skill lookup checks workspace `.agents/skills`, workspace `.gemini/skills`, user `~/.agents/skills`, then user `~/.gemini/skills`. It requires readable `exec-plans/SKILL.md` and `tdd/SKILL.md` and records paths and hashes. Extension-only skills are not accepted by this portable v1 preflight. File discovery does not establish folder trust, skill activation permission, authentication, or model compliance. The runner inherits the configured model and approval mode unless explicit options are supplied; it never silently selects `yolo`.

An explicit `--policy PATH` accepts one caller-reviewed UTF-8 `.toml` regular file no larger than 1 MiB. Its physical path and SHA-256 of exact bytes are recorded, and the same file is passed to Gemini. Symlink path components and commas are rejected. The runner checks the bytes again before every provider spawn; changed bytes block until they are explicitly reviewed and selected. Omitting `--policy` preserves inherited provider configuration.

On resume, omitting `--policy` reuses the last explicit path and expected hash. If those bytes changed, resume blocks. Supplying `--policy` on resume explicitly selects the reviewed path and bytes for that invocation and records the previous and selected values; it does not skip Git or transaction recovery checks.

Gemini CLI 0.65.0 disables implicit workspace `.gemini/policies` discovery. An explicit `--policy` file is an additional supplied input; it does not replace or erase inherited user policy, and is not proof of effective permissions. The historical qualification used `~/.gemini/policies/qualification.toml`. If it remains on a machine, its owner should review whether it is still needed through their normal configuration process before a fresh provider attempt. If the owner decides it is no longer needed, they may remove it through that same process. The runner and this guide never write, edit, or delete that global file. Doctor inventories only conventional configuration paths and bounded file metadata. It records path, state, and digest, not file bodies, credentials, environment dumps, or provider logs. It does not emulate precedence or regex matching, or claim a complete effective grant set. Never write global policy, add admin policy, or install broad grants as a workaround. Never silently enable an approval mode that the caller did not select.

Pinned official sources: [policy-engine documentation](https://github.com/google-gemini/gemini-cli/blob/v0.65.0/docs/reference/policy-engine.md), [CLI policy option](https://github.com/google-gemini/gemini-cli/blob/v0.65.0/packages/cli/src/config/config.ts), [headless output](https://github.com/google-gemini/gemini-cli/blob/v0.65.0/docs/cli/headless.md), [non-interactive execution](https://github.com/google-gemini/gemini-cli/blob/v0.65.0/packages/cli/src/nonInteractiveCli.ts), and [skills discovery](https://geminicli.com/docs/cli/skills/). Requalify the adapter and fixtures before changing the pinned version. Do not silently accept arbitrary provider versions.

## Qualification status

The original adapter had a successful owner-run Gemini CLI 0.65.0 qualification on 2026-10-27. That historical evidence covers the original adapter flow only. It does not establish readiness on the current machine or qualify the follow-up doctor, policy, blocker, observation, and qualification-helper behavior. The new follow-up behavior has no live provider proof as of 2026-10-28. Deterministic tests and fake-provider runs are not live evidence. An owner may gather fresh evidence with the [live qualification guide](references/live-qualification.md) after explicitly authorizing paid use.

The bundled qualification helper has `setup`, `run`, and `collect` commands. Setup and collect are local-only; run repeats doctor before the provider and requires both `--authorize-paid-run` and actual owner authorization. Use the foreground workflow in the guide and wait on the same long-running session.

## Worker packet and provider diagnostics

Before a provider iteration, the runner builds a self-contained `RUNNER_PACKET` containing the current task, prerequisite state, acceptance commands, design context, result schema, and exact UTF-8 contents and SHA-256 digests for the bundled message and protocol references. The complete prompt is limited to 96 KiB; required context that exceeds the limit stops before provider invocation with `worker_context_limit`. Workers use the embedded reference content instead of searching the source checkout for it.

When a provider process returns normally after cleanup without a terminal result, the iteration records typed `provider_diagnostic` metadata and may retain a sanitized stderr artifact. This covers zero-exit protocol-retry outcomes and nonzero provider-blocked outcomes, not every failure. Captured stderr is bounded at 1 MiB and a saved artifact at 65,536 bytes. If capture was truncated, text is omitted. Redaction applies known credential patterns and values from credential-like environment names; arbitrary secrets cannot be guaranteed removed. Timeouts, midstream decoder failures, and cleanup-unconfirmed outcomes that exit before normal returned-outcome handling keep their existing behavior and do not gain a new artifact. A persistence error stops with `diagnostic_persistence_failed`. Helper collection carries the typed metadata and original relative reference without copying the artifact.

## Validation

These commands are repository-maintainer checks, not installed runtime dependencies. From the source repository root:

```sh
rtk proxy python3 scripts/test-execplan-implement-loop.py
rtk proxy python3 scripts/test-execplan-implement-loop.py --group readiness
rtk proxy python3 scripts/test_test_all.py
rtk proxy python3 scripts/test-all.py --list
rtk proxy python3 scripts/test-execplan-qualification.py
```

Groups: contract, readiness, process, git, loop, packaging. Tests exercise copied bundles with fake Gemini executables, real verification processes, and disposable Git repositories. The qualification suite tests the separate helper through its CLI. Process-group tests require permission to inspect child groups with `/bin/ps`; run them serially with that inspection available. Tests must assert descendant termination before cleanup. Provider usage missing in a fixture remains null.

The `evals/evals.json` scenarios cover fresh execution, interrupted recovery, and invalid/blocked plans. Generated agent comparison artifacts belong outside the bundle. Deterministic fixture results establish runner behavior; paired agent runs establish sampled instruction behavior. Neither establishes current-machine readiness or live qualification of the follow-up behavior.

## Recovery and limits

State, bounded verification logs, message files, and atomic summary.json live under the worktree-specific Git directory by default. A custom new run directory must be outside the worktree. State paths cannot contain symlinks. Files are owner-only. The kernel lock covers all loop instances in the physical worktree, regardless of run directory. It does not coordinate unrelated editors.

Write-ahead commit intent records before/after plan bytes, changed paths/fingerprints, parent, message digest, candidate digest, and index/tree state. Resume recognizes only the prepared transaction. The runner compares staged and committed blob identities with verified working bytes, blocking Git filters that transform deliverables. Hooks and signing settings run normally. A failed commit preserves its staged delta. Fix hook/configuration causes, then resume; do not rerun implementation.

The summary contains structured `blockers` for unsuccessful outcomes, including failures before engine startup. Read the blocker, its remediation, and its resume path together with the top-level reason. Unknown errors receive generic inspection guidance; provider text is data, never executable remediation. A validated blocked worker remains `blocked` in the new iteration and resume history without a commit or retry/failure-count increment.

After `cleanup_unconfirmed` or an unclean stop, do not start a replacement provider or runner while owned children may still exist. Confirm the old process tree has stopped, inspect the saved worktree and task delta, and reconcile HEAD, index, plan, and lock ownership. Supply `--acknowledge-unclean-stop` only after that review; it records an operator assertion and does not prove cleanup. Do not delete a lock as a shortcut or remove a lock owned by another process.

Commands and Gemini run with selected user permissions. This is an orchestration tool, not a sandbox against malicious repository code. Monotonic execution deadlines bound subprocess work; final local integrity inspection and report persistence can finish afterward. Uninterruptible OS I/O cannot provide a hard real-time guarantee. No provider raw JSONL is persisted; provider session IDs locate the original transcript when available.

An alternate I/O method is allowed only for the same already-authorized writable paths. A tool-specific failure does not widen authority beyond user, sandbox, policy, filesystem, or path restrictions.
