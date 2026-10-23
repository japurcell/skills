# Maintaining execplan-implement-loop

The runtime is portable within this bundle. It uses Python 3.12+ standard library on macOS/Linux and real Git. No package installation, user Git configuration changes, or provider log scraping occurs.

## Provider qualification

The adapter pins Gemini CLI **0.65.0**. Preflight checks `gemini --version` exactly before any prompt invocation. Source-backed protocol fixtures cover init, string assistant message deltas, terminal result, and aggregated usage. These are compatibility fixtures, not proof of a live authenticated run.

Pinned official source: [noninteractive execution](https://github.com/google-gemini/gemini-cli/blob/v0.65.0/packages/cli/src/nonInteractiveCli.ts), [headless documentation](https://github.com/google-gemini/gemini-cli/blob/v0.65.0/docs/cli/headless.md), and [skills discovery](https://geminicli.com/docs/cli/skills/). Requalify the adapter and fixtures before changing the pinned version. Do not silently accept arbitrary provider versions.

Gemini skill lookup checks workspace `.agents/skills`, workspace `.gemini/skills`, user `~/.agents/skills`, then user `~/.gemini/skills`, requiring readable exec-plans/SKILL.md and tdd/SKILL.md and recording digests. Discovery files do not establish folder trust, skill activation permission, authentication, or actual model compliance. Those remain provider prerequisites, with explicit prompt instructions and blocked provider failures. Extension-only skills are not accepted by this portable v1 preflight. The runner inherits the configured model and approval mode. The explicit `--approval-mode yolo` option permits autoapproval only when the caller supplies it.

## Validation

From the source repository root:

```sh
rtk proxy python3 scripts/test-execplan-implement-loop.py
rtk proxy python3 scripts/test_test_all.py
rtk proxy python3 scripts/test-all.py --list
```

Groups: contract, process, git, loop, packaging. Tests copy the bundle into an isolated installation, use fake Gemini executables, real verification processes, and real disposable Git repositories. Process-group tests require permission to inspect child groups with `/bin/ps`. Tests must assert descendant termination before cleanup. Provider usage missing in a fixture remains null.

The evals/evals.json scenarios cover fresh execution, interrupted recovery, and invalid/blocked plans. Generated agent comparison artifacts belong in sibling execplan-implement-loop-workspace/iteration-N, never in this bundle. Deterministic fixture results establish runner behavior; paired agent runs establish sampled instruction behavior. Neither establishes live Gemini acceptance.

Live-provider acceptance remains pending until an owner-run smoke test demonstrates the pinned CLI, permission policy, skill activation, and terminal parsing. Follow the [copy-and-run live qualification guide](references/live-qualification.md) on a machine with Gemini CLI. It includes a disposable source-code plan and the evidence to return. Do not claim live acceptance from mocked tests.

## Recovery and limits

State, bounded verification logs, message files, and atomic summary.json live under the worktree-specific Git directory by default. A custom new run directory must be outside the worktree. State paths cannot contain symlinks. Files are owner-only. The kernel lock covers all loop instances in the physical worktree, regardless of run directory. It does not coordinate unrelated editors.

Write-ahead commit intent records before/after plan bytes, changed paths/fingerprints, parent, message digest, candidate digest, and index/tree state. Resume recognizes only the prepared transaction. The runner compares staged and committed blob identities with verified working bytes, blocking Git filters that transform deliverables. Hooks and signing settings run normally. A failed commit preserves its staged delta. Fix hook/configuration causes, then resume; do not rerun implementation.

After SIGKILL or unconfirmed cleanup, ordinary resume blocks. Stop the old child tree, inspect Git locks left by killed Git processes and reconcile their ownership, inspect the task delta and frozen plan, and only then acknowledge with `--acknowledge-unclean-stop`. Never kill an unverified reused PID or remove a lock owned by another process. The acknowledgement is an operator assertion, not a containment guarantee.

Commands and Gemini run with selected user permissions. This is an orchestration tool, not a sandbox against malicious repository code. Monotonic execution deadlines bound subprocess work; final local integrity inspection and report persistence can finish afterward. Uninterruptible OS I/O cannot provide a hard real-time guarantee. No provider raw JSONL is persisted; provider session IDs locate the original transcript when available.
