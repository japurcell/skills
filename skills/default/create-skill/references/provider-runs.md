# Isolated provider runs

Use the bundled runner for live evaluations that fit its contract. Check this scope before preparing runs; use its `--help` for exact arguments and exit statuses.

## Capability check

- Requires Python 3, Git, and a supported Codex or Copilot CLI on macOS or Linux. These are runner requirements, not requirements for every use of the create-skill skill.
- Requires a disposable Git repository with an initial commit and no remotes, a skill snapshot, and an immutable configuration file. Preserve the intended baseline conditions when choosing the harness.
- Supports `smoke`, `contribution`, and `commit` phases in one persistent session. Every commit phase requires a prior successful contribution phase. Git-only commit scenarios without agent contribution do not fit this sequence; adding a dummy contribution would change the experiment.
- Copilot's mutation grants cover the prepared commit fixture workflow. Workflows requiring other tools or write locations need a suitable scenario harness.

For unsupported platforms, providers, phase sequences, permission needs, or baseline conditions, select a maintained scenario harness and document the gap. Preserve private per-run paths, immutable inputs, provider/settings evidence, bounded subprocesses, and session continuity where the scenario requires it. Keep failed or unavailable evidence visible. If no suitable harness exists, report the scenario as unrun until the missing capability is implemented and verified; preserve the scenario rather than bypassing runner checks.

## Prepare and execute a supported run

Run `preflight` first; it checks provider version/help without launching a model. Then prepare a fresh root with `init`, or use the commit fixture's preparer followed by `adopt` as described below. For each candidate/baseline run, complete its own `turn --phase smoke` before its scenario turns. Smoke is a real provider invocation: keep its prompt free of the behavior being scored, verify it has not changed the fixture, and retain its evidence separately. When evaluations are excluded by the user, do not invoke any `turn` phase.

From the active skill installation, substitute the path containing its `SKILL.md` for `<create-skill-root>`:

```sh
python3 <create-skill-root>/scripts/eval_runner.py --help
python3 <create-skill-root>/scripts/eval_runner.py preflight \
  --provider codex --executable codex
python3 <create-skill-root>/scripts/eval_runner.py init \
  --run-root /tmp/skill-eval/run-01 \
  --skill /absolute/path/to/skill-snapshot \
  --config /absolute/path/to/immutable-config.json \
  --repo /absolute/path/to/disposable-fixture-repository
```

Copilot recognizes read-only Git inspection commands without an explicit grant. The adapter supplies write grants for `repo/`, `outputs/`, `messages/`, and `message.txt`, plus Git add/commit and validator command grants. Include the command contract `python3 <run>/skill/scripts/validate_message.py <message-path>` in the smoke prompt so later turns use the granted validator invocation. Preflight records `--version` plus the relevant CLI help output fingerprint and fails if required session, model, workspace, or output options are absent. The runner constructs provider commands itself; callers cannot append arbitrary flags that could bypass isolation or start an ephemeral session. No permission-bypass options are used.

Each run gets a new mode-0700 root containing a read-only skill/config snapshot, a copy of the supplied fixture repository, isolated `messages/`, `evidence/`, and `tmp/` paths, and a manifest binding evidence to the run ID, provider version, settings, and persistent session ID. The fixture repository must have an initial commit and no remotes. Never point messages or evidence outside the run root. The runner checks physical repo root, remote absence, initial HEAD before commit, immutable snapshot/config hashes, and private directory containment before every turn. It rejects external message paths, session/settings changes, failed contribution turns, and commit turns without a successful contribution.

Create a separate prompt file for each turn inside the run's `messages/`. A successful smoke writes a receipt tied to provider version, settings, session identity, and evidence. Run the scenario's contribution and, when required, commit turns through that same manifest. The runner fixes cwd, adds the run root as scoped writable content, and pins model/reasoning settings. Codex's installed resume command does not expose cwd or add-dir options, so the runner resumes its recorded thread from the same repository cwd established by smoke; Copilot receives `--add-dir` on each turn. If a provider changes required CLI options, help preflight fails closed. Turn timeouts are 1-1800 seconds; version/help calls use a separate fixed timeout. Timeout exits 124 and does not create a smoke receipt. `init` failures after root creation retain `preparation-error.json`; failed provider turns retain execution evidence. Continue one run through its manifest, and allocate fresh roots for independent runs or retries instead of resetting prior evidence.

For each phase, provide `--manifest <run>/manifest.json`, `--provider codex|copilot`, `--executable <cli>`, `--phase smoke|contribution|commit`, `--message-file <run>/messages/<file>`, and the same `--setting model=<model>` plus any selected `reasoning_effort` or Codex `sandbox` setting. Repeat the exact settings on every turn, including an explicitly selected `sandbox=workspace-write`. The runner records Codex's thread ID from its JSON event; for Copilot it generates a UUID, passes it with `--session-id` and resumes that requested ID on later turns. Distinguish the requested Copilot ID from independent observation of provider session continuity. Do not pass provider command arguments.

For a supported commit scenario, prepare it with `<commit-skill-root>/evals/prepare_validation_workflow.py`, then use `eval_runner.py adopt --run-root <prepared-run> --config <immutable-config.json>`. Adoption adds runner metadata to the existing prepared root, preserving its absolute observer paths, Git hook, validator, and grader-visible repo. It refuses an existing manifest or runner directory and verifies the fixture's recorded initial HEAD and lack of remotes. Use distinct run roots and message paths for concurrent runs. The commit grader rejects validator paths or argument paths that resolve outside the run, including symlink escapes.

## Grade retained evidence

Normalize native execution records using [evaluation validation and evidence](validation.md) before invoking the maintained grader and aggregator. The runner does not produce `grading.json`, normalized `response.md`/`timing.json`/`transcript.md`, or a benchmark report. A smoke receipt and a zero provider exit establish execution only; grade the scenario's outputs and observations separately. Deterministic fake-provider maintenance checks are listed in each bundle's README and do not establish live model performance.
