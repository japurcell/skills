# Delegation evaluation

The scenarios in `evals.json` assess orchestration decisions from the supplied skill. They do not demonstrate timer delivery, worker cancellation, or write quiescence in a live host. Preserve raw responses, transcripts, timing, and per-assertion evidence when comparing the current skill with a pre-change snapshot. Point each run at its exact snapshot and ignore installed copies. Report failed or missing evidence separately from measured runtime behavior.

## Maintained diagnostic pilot

`scheduler_pilot.py` compares frozen scheduler bundles through public `prepare`,
`preflight`, `run` and `grade` commands. Every command supports `--help`.
The harness uses Python's standard library. Run its deterministic offline suite
from the repository root.

```sh
rtk proxy python3 skills/default/delegate-to-subagents/evals/test_scheduler_pilot.py
```

The suite launches real helper and scheduler children and supplies native-shaped
provider envelopes. Actual sanitized Copilot 1.0.109 envelopes are retained in
`fixtures/copilot-native-envelopes.json`, with source provenance. The actual P03
denied helper shape stays invalid. Offline success establishes harness behavior.
Each scored phase must demonstrate its own helper execution and permission acceptance.

### Prepare and execute

Use absolute executable paths and the approved model and effort in configuration.

```json
{
  "providers": {
    "codex": {
      "executable": "/absolute/bin/codex",
      "model": "gpt-6.1-sol",
      "effort": "medium",
      "authentication": {"mode": "native-existing-login"}
    },
    "copilot": {
      "executable": "/absolute/bin/copilot",
      "model": "gpt-6.1-sol",
      "effort": "medium",
      "authentication": {"mode": "native-existing-login"}
    }
  },
  "timeout_seconds": 600
}
```

```sh
python3 scheduler_pilot.py prepare --run-root /private/tmp/fresh-pilot --baseline /absolute/v2 --candidate /absolute/v3 --config /absolute/config.json
python3 scheduler_pilot.py preflight --manifest /private/tmp/fresh-pilot/manifest.json --provider codex
python3 scheduler_pilot.py preflight --manifest /private/tmp/fresh-pilot/manifest.json --provider copilot
python3 scheduler_pilot.py run --manifest /private/tmp/fresh-pilot/manifest.json --cell codex-baseline --phase scenario
python3 scheduler_pilot.py grade --manifest /private/tmp/fresh-pilot/manifest.json --cell codex-baseline
```

Preparation freezes selected skill bodies verbatim, scheduler/helper bytes,
executable mode, adjacent invocation settings, prompts, rubric, argv and relevant
nonsecret environment identities in a fresh physical 0700 root. The payload has
four scored sessions, baseline and candidate for each provider. Each scored
phase independently validates its own evidence. Optional baseline-cell smoke
commands remain diagnostic. Attempts are exclusive and cannot be replayed.
Each session has at most 600 seconds. The approved pilot has no retries or budget
expansion.

Existing native login stays provider-owned. Native Codex uses standard
HOME/CODEX_HOME and CLI 0.167.1. Native Copilot uses standard HOME/COPILOT_HOME,
CLI 1.0.109, create-only session IDs and bounded status/auth/model RPC preflight.
Defaults also support private Codex HOME and Copilot process-token authentication.
Process-token mode passes supported token variables only in memory and records
variable names. Credential values and storage files stay outside evidence.

Codex uses workspace-write sandbox and ordinary approval controls. Its shell
startup HOME is empty and read-only. Copilot grants the literal frozen extensionless executable
helper path and scoped repo writes, with repo/snapshot directory access, built-in
MCP disabling and manual permissions. Its helper has an absolute pinned Python
shebang and executable mode before hashes freeze. Prompt commands and permission
rules share the literal invoke-scheduler prefix and explicitly require direct
execution without prepending Python. Scored execution must prove native acceptance.

### Evidence and grading

JSON command results go to stdout and diagnostics to stderr. Harness stdin is
unused. Codex receives the frozen prompt on stdin. Preparation/preflight and
successful phase execution exit 0. Invalid setup or invocation exits 2, timeout
124 and interruption 130. Grade exits 0 when it writes a grading artifact,
including behavioral failures. Closed stdout exits 1.

Run and grade re-read the same raw evidence and bindings. Receipts retain source,
prompt, session, selector, cwd, command, exit, timing and raw stdout/stderr hashes.
Codex completed stdout commands and results establish helper execution. The
observed python3 prefix and exact pinned absolute-interpreter equivalent are
accepted only for Codex when frozen shell PATH resolves to that hashed interpreter
and the exact helper path follows it. Original native commands remain retained.
Other interpreters and mismatched remaining argv remain invalid. Its exact
fresh-session raw rollout establishes session/model/effort/cwd identity. Local
file URI and absolute cwd paths compare semantically. Copilot pairs native tool
starts and terminal completions by tool ID and turn. Unknown observational
telemetry stays in raw evidence. Missing optional usage is reported as unavailable.
Provider-defined usage remains raw, with no estimates or zero substitution.
Wrapper elapsed includes provider execution and evidence collection.

Every required action must match one real helper receipt with exact scheduler
argv, actual child exit/stdout, before/after state and output readback. Duplicate,
replayed, fabricated or missing receipts, changed source/prompt/results, wrong
selectors and inconsistent state chains invalidate the corresponding evidence.
Harmless incidental inspection does not alone invalidate behavior.

The scenario rubric checks deadline stops, one extension, a genuine rejected
second extension, independent C progress and stop-before-transfer. Parent transfer
requires an actual helper parent write/readback in causal order. Candidate
acknowledgment is reported separately and must bind the same current ownership
record. Artifacts resolve within the cell's outputs, with traversal and symlinks
rejected. Grade retains setup, behavior, output and comparison status separately.
All shutdown facts remain synthetic. Every grade requires independent semantic
review. A paired pilot supplies bounded diagnostic evidence.
