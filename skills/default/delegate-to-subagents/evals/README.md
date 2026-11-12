# Delegation evaluation

The scenarios in `evals.json` assess orchestration decisions from the supplied skill. They do not demonstrate timer delivery, worker cancellation, or write quiescence in a live host. Preserve raw responses, transcripts, timing, and per-assertion evidence when comparing the current skill with a pre-change snapshot. Point each run at its exact snapshot and ignore installed copies. Report failed or missing evidence separately from measured runtime behavior.

## Maintained diagnostic pilot

`scheduler_pilot.py` is a stdlib scenario harness. It deliberately bypasses the
create-skill commit runner: scheduler experiments have no contribution/commit phase.
Its public commands read no stdin, print JSON to stdout and diagnostics to stderr.
`--help` is offline. Exit 0 means successful preparation/preflight/execution or a
produced grade (including failed behavior); 2 means invalid setup/invocation or
failed smoke, 124 timeout and 130 interruption. Evidence from every attempted
phase is retained; retries require a fresh private root.

Run the deterministic suite only:

```sh
python3 skills/default/delegate-to-subagents/evals/test_scheduler_pilot.py
```

No model calls are made by `prepare`, `preflight`, `grade` or these tests.
`run` performs a model call and requires separate authorization. The initial
pilot budget is four smoke and four scenario calls, with no automatic retries.
Use frozen v2 baseline and integrated v3 candidate bundle directories.

Create a JSON config with exactly this shape (substitute verified absolute CLI
paths and approved model/settings; these example names do not select a model):

```json
{
  "providers": {
    "codex": {"executable": "/absolute/bin/codex", "model": "approved-model", "effort": "medium"},
    "copilot": {"executable": "/absolute/bin/copilot", "model": "approved-model", "effort": "medium"}
  },
  "timeout_seconds": 600
}
```

```sh
python3 scheduler_pilot.py prepare --run-root /private/tmp/fresh-pilot --baseline /absolute/v2 --candidate /absolute/v3 --config /absolute/config.json
python3 scheduler_pilot.py preflight --manifest /private/tmp/fresh-pilot/manifest.json --provider codex
python3 scheduler_pilot.py preflight --manifest /private/tmp/fresh-pilot/manifest.json --provider copilot
```

Preflight captures native version/help and executable hashes. Review those files,
the immutable config/rubric/prompts, all four cells' exact `argv`, scoped write
roots and fresh phase session IDs before authorizing calls. Hash drift or an
already attempted phase fails closed. Copilot gets selected-snapshot access,
repo-scoped writes and only the selected scheduler and immutable smoke helper
Python patterns. Codex uses workspace-write sandbox with repo cwd and private tmp.
Neither adapter adds unrestricted permission bypasses. Host-global instructions
may remain visible in Codex; this is a comparison limitation.

After approval, use `run --manifest PATH --cell codex-baseline --phase smoke`
then `--phase scenario`; repeat for codex-candidate, copilot-baseline and
copilot-candidate. Each phase starts a fresh session with identical cell settings,
cwd, snapshot and grants. Smoke embeds the exact selected skill body, executes a
neutral register/complete fixture and proves the exact smoke output was written
and read through the frozen helper. Smoke teaches no scored transfer behavior.

`grade --manifest PATH --cell CELL` writes `evidence/grading.json` and emits it.
The combined scenario and output schema live in `pilot-scenarios.json`, frozen as
`rubric.json`. Result JSON, parent ownership and scheduler state are read from
exact repo outputs paths. Each action's JSON evidence contains `command` and
`exit_code` matching a retained native command event. Native successful script
execution and the authored result are checked separately. Candidate acknowledgment
is separate from common assertions. Missing output with valid smoke fails behavior;
failed smoke is invalid setup; permission failure excludes causal comparison.
Missing usage is explicit and never estimated. Retain raw JSONL, stderr, native
summaries, run argv and timing. A deterministic pass still requires semantic review
of every authored artifact and native event. All worker/write shutdown facts are
synthetic; this harness cannot establish real worker termination or reliability.
