# Delegation evaluation

The scenarios in `evals.json` assess orchestration decisions from the supplied skill. They do not demonstrate timer delivery, worker cancellation, or write quiescence in a live host. Preserve raw responses, transcripts, timing, and per-assertion evidence when comparing the current skill with a pre-change snapshot. Point each run at its exact snapshot and ignore installed copies. Report failed or missing evidence separately from measured runtime behavior.

## Maintained diagnostic pilot

`scheduler_pilot.py` is an offline stdlib preparation and grading harness. Its
Codex `run` fails closed because workspace-write lacks the required native
exact command allowlist. Copilot uses the documented isolation controls below;
its static preflight requires supported flags and an auth token for the isolated
home. Exact requested Sol/medium resolution remains pending a separately
authorized smoke, rather than being treated as known incompatibility. The
current operator environment has no supported token, so native Copilot remains
unrun. A successful help/version capture is syntax evidence, not execution
readiness. Codex requires a separately reviewed command-boundary solution.
Copilot smoke requires separate approval of its exact frozen payload. Editing a
receipt cannot bypass the Codex capability check or Copilot auth/environment checks.

The public commands are `prepare`, `preflight`, `run` and `grade`; each has `--help`.
Stdin is unused. JSON results go to stdout, diagnostics to stderr. Exit 0 means
preparation or a grading artifact was produced, including behavioral failure;
2 means invalid setup or blocked provider prerequisites; interrupted helper execution
exits 130, timed-out helper children 124, closed stdout 1. Grade keeps invalid
setup, behavior, output contract, permission failure and comparison eligibility
separate. A native readiness failure does not erase offline evidence or invent
behavior.

Run only the focused deterministic suite (no inference):

```sh
python3 skills/default/delegate-to-subagents/evals/test_scheduler_pilot.py
```

It prepares frozen v2/v3 bundles, executes real scheduler subprocesses through
the exact frozen `invoke_scheduler.py`, captures native-shaped Codex/Copilot
command results and grades through the public CLI. The helper executes one
agent-selected scheduler invocation, or a neutral smoke/parent record write and
readback. It chooses no scenario sequence or deadlines. The grader requires the
native event to show that exact helper invocation and its emitted child argv,
exit status, stdout and before/after state. Mutable authored receipts alone,
AST literals and arbitrary subprocess wrappers are insufficient evidence.
Copilot tool success remains distinct from the helper's actual child exit 2.
The helper kills remaining child process-group members after success, timeout or
interruption, including descendants whose leader and output pipes have closed.

Minimal config (use verified absolute executables and approved selectors):

```json
{
  "providers": {
    "codex": {"executable": "/absolute/bin/codex", "model": "gpt-6.1-sol", "effort": "medium"},
    "copilot": {"executable": "/absolute/bin/copilot", "model": "gpt-6.1-sol", "effort": "medium"}
  },
  "timeout_seconds": 600
}
```

```sh
python3 scheduler_pilot.py prepare --run-root /private/tmp/fresh-pilot --baseline /absolute/v2 --candidate /absolute/v3 --config /absolute/config.json
python3 scheduler_pilot.py preflight --manifest /private/tmp/fresh-pilot/manifest.json --provider codex
python3 scheduler_pilot.py preflight --manifest /private/tmp/fresh-pilot/manifest.json --provider copilot
```

`prepare` rejects provider configuration directories inside snapshot bundles,
then freezes source snapshots, helper/spec files, exact prompts/rubric/argv,
settings and relevant nonsecret environment/config fingerprints in a fresh 0700
root. Hash, settings or environment drift fails closed. No secret values are
copied. The fingerprint is evidence of observed configuration, not proof that all
provider configuration sources are isolated. Provider preflight captures native version/help/executable hash. It records
Codex's unsupported boundary, or Copilot's missing auth as applicable, separately
from requested-vs-observed model status. Copilot exact signed-in account support
for Sol/medium remains unverified and can be established by an authorized smoke;
selectors are requested without substitution. Codex exposes
`--ignore-user-config`/`--ignore-rules`; draft argv uses those controls, but
workspace-write is a workspace sandbox and not a command allowlist.

Draft Copilot argv scopes recursive `write(ABSOLUTE_REPO/**)`, the exact frozen
helper Python prefix, repo/snapshot path access, disables automatic temp access,
built-in MCPs and BASH_ENV. The draft uses a fresh HOME/COPILOT_HOME/COPILOT_CACHE_HOME, disables automatic
plugin discovery and login-shell environment loading, and freezes manual
permission mode, hook disabling and bypass-mode disabling. Only the explicitly
listed nonsecret environment is included; auth tokens must be supplied separately
in memory and marked secret for shell/MCP environments, never copied to evidence.
This draft has not been exercised with live Copilot.
`COPILOT_ALLOW_ALL`, assisted approval and persisted permission grants cannot be
silently treated as covered by the narrow command flags. Copilot `run` uses only that frozen nonsecret environment plus supported auth
variables supplied in memory; the native smoke must observe the exact requested
model and effort. An operator may supply COPILOT_GITHUB_TOKEN, GH_TOKEN or
GITHUB_TOKEN from an existing secret manager into the invoking process. Do not
put values in config, command arguments, prompts, manifests, logs or source. The
harness records variable names only and passes --secret-env-vars to strip those
credentials from shell/MCP environments. Persisted credentials are not copied.
No generic unavailable-capability claim is made for those documented controls. No all-tools, all-paths, yolo or other permission bypass is added.

The future ceiling is four smoke plus four scored calls, each at most 600s, with
no retries/expansion. Each phase has a fresh session. Both variants' valid smoke
receipts are required before either scored cell for that provider. Smoke embeds
the selected skill body, actually executes neutral register/complete operations,
and proves writing/readback at the exact `repo/outputs/smoke.json`. It teaches no
scored deadline/transfer behavior. Failed/missing smoke means invalid setup.

The combined controlled scenario lives in `pilot-scenarios.json`. Each action
must match real child operation/time/exit/state evidence; state continuity and
final authored state are checked against native helper receipts. Follow-up at150,
rejected second extension at151, independent C progress and premature transfer
exit2 are required. Parent transfer additionally needs the helper's native
write/readback receipt in sequence after authorization. Candidate acknowledgment
is separate from common assertions. Evidence resolves strictly inside the current
cell's `outputs/`, with traversal/symlinks rejected. Missing/wrong/malformed output
after valid smoke fails its contract. Missing usage is explicit and not estimated.
Every grade still requires semantic review. All shutdown facts are synthetic;
this harness does not establish real worker termination or general reliability.
