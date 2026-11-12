# Delegation evaluation

The scenarios in `evals.json` assess orchestration decisions from the supplied skill. They do not demonstrate timer delivery, worker cancellation, or write quiescence in a live host. Preserve raw responses, transcripts, timing, and per-assertion evidence when comparing the current skill with a pre-change snapshot. Point each run at its exact snapshot and ignore installed copies. Report failed or missing evidence separately from measured runtime behavior.

## Maintained diagnostic pilot

`scheduler_pilot.py` is an offline stdlib preparation and grading harness. Its
Codex `run` fails closed pending verification of private hook trust/loading,
host hook-failure semantics and enabled-tool coverage. A native PreToolUse hook
can deny supported commands; workspace-write alone remains a filesystem sandbox. Copilot uses the documented isolation controls below;
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

## Private Codex control policy

`prepare` freezes `control/policy_hook.py`, each cell's `.codex/hooks.json` and
feature config, and their hashes in manifest version3. This registers only a
private per-cell draft. It does not install or enable the owner-disabled global
Guardian, modify user configuration or alter a trust store. The hook CLI reads a
bounded native PreToolUse JSON object on stdin and emits documented native JSON.
Exit0 permits normal processing; exit2 explicitly denies. Unknown tools and input
shapes, shell compounds/substitutions, interpreter wrappers, interactive forms,
nonmatching helper argv and escaped/linked paths are denied by default. Neutral
apply_patch add/update operations are confined to the cell's outputs directory;
move/delete and writes to control/config/snapshots are denied. Audit records
outside agent-writable outputs contain decision, command hash and policy hash.

The documented loading mechanism is project `.codex/hooks.json` with hooks
feature enabled. Non-managed hook definitions require review/trust of their exact
hash through `/hooks`, including project-layer trust. No undocumented trust-file
write or `--dangerously-bypass-hook-trust` is used. A configuration file existing
on disk does not prove it loaded. The operator must review the exact private
cell paths through the documented UI before separately authorized native smoke.
There is no automated trust assertion in this harness.

The existing four smoke prompts now add a harmless forbidden-write attempt.
Smoke requires successful neutral helper execution, native denial of the exact
probe and absence of its marker. Codex additionally requires the frozen hook's
allow/deny audit records to agree with native command hashes and policy hash.
Copilot checks observed native permission denial under its frozen argv. Offline
fixtures simulate those native provider envelopes explicitly; their hook/child
subprocesses are real, but they do not establish live provider loading or trust.
No extra provider call or scored scenario behavior is added.

The [official hook reference](https://learn.chatgpt.com/docs/hooks) documents
pre-tool interception and private hook discovery/trust. It also limits tool
coverage and describes failure paths that can continue execution. Therefore a
valid policy's own deny JSON is not a complete host fail-closed guarantee:
missing/untrusted scripts, host errors/timeouts, specialized opt-out tools and
write_stdin transport still need native verification or a supported restriction.
`preflight`/`run` retain the exact
`codex-private-hook-trust-load-failure-and-enabled-tool-coverage-unverified`
prerequisite. They make no categorical platform-impossibility claim and cannot
be enabled by changing an authored receipt. If the installed host cannot satisfy
those controls, preserve that blocker and keep the live pilot incomplete.

### Ordered evidence and current ownership

Scenario time is checked in recorded native operation order, including rejected
operations and parent writes. Finite synthetic times may be equal but cannot
move backward. C's checkpoint and completion must occur while B is actually
unconfirmed in both captured states, before the native shutdown confirmation;
backdated argv alone do not establish independent progress. A chronology failure
with valid smoke is a comparison-eligible behavioral failure.

The final parent reference must resolve to the helper's actual current
`outputs/ownership.json`. Its current contents, final native readback and parent
write evidence must agree. Candidate receipt evidence must resolve to that same
current target and owner; a detached snapshot cannot replace it. Equivalent
confined spellings of the same path remain valid.

Smoke requires exactly its frozen register/complete argv and
`outputs/smoke-state.json`, actual successful result JSON, ordered linked
before/after states, and the current completed smoke state. The actual neutral
write/readback follows completion. Wrong state, changed argv, missing/reordered
steps or a disconnected state chain invalidate setup rather than being scored as
a scenario failure. These checks do not add provider calls or change native
readiness gates.

### Observed-run qualification

Fresh version 3 preparations pin the executing harness/import hashes separately from selected scheduler snapshots, resolve provider and interpreter identities, and freeze the private environment and safe configuration. Codex discovery and exec share supported overrides and exact private HOME/CODEX_HOME. Discovery performs initialize, initialized, hooks/list and config/read only, requiring one synchronous trusted project hook. Its supported configuration projection includes the inspected Codex 0.167.1 defaults and accepts the absent, empty `/etc/codex/config.toml` layer. Unexpected configuration, hooks or external populated layers fail setup. Authentication receipts contain status or supported token names only.

Preflight `valid` denotes setup readiness. Explicit `syntax_supported`, `setup_ready`, `smoke_ready` and `scenario_ready` distinguish setup from qualification. Each phase creates an exclusive attempt before spawning. A failed or partial attempt blocks replay and remaining calls for its provider. Cell/provider locks serialize execution. Receipts bind the manifest and preflight payload digest, source/interpreter/provider identities, exact command/cwd/environment, safe config, delivered prompt hash, requested/observed selectors, actual session/turn identities, raw/parsed evidence hashes and audit byte intervals. Final receipt replacement is atomic. Codex receives its prompt on stdin, while Copilot retains its frozen prompt argument.

Run and grade re-read raw evidence and current bindings. Both provider smokes must validate before scenarios. Modified evidence, unmatched/duplicate native IDs, unknown tools, selector contradictions, unexpected denials, audit drift, unsupported patch forms and missing telemetry invalidate qualification. Accepted receipts identify `acceptance_contract=verified-observed-run` and describe observed event types and limitations. Absence of an event establishes no universal tool coverage.

The supported Copilot 1.0.109 envelope pairs toolCallId and turnId, requires session.start selectors/session/cwd, validates supplied tool model fields, and supports exact helper bash calls plus single confined Add File apply_patch calls. Patch arguments remain raw strings, completion fileEdits must identify the exact created file, and current bytes must match the patch. Native boolean success stays distinct from captured scheduler child exit status. Update, delete, move and unrecognized write forms invalidate this bounded adapter.

Inspected Codex exec evidence supplies thread/item identity but lacks executing-selector, complete tool inventory and hook tool-use correlation. Codex qualification remains `native-evidence-unsupported`. Grade preserves individual real-child rubric observations as diagnostic assertions with setup invalid, behavior not_evaluated and comparison eligibility false. Synthetic transport fixtures never establish native provider qualification. Copilot fixtures exercise both variants through real helper/scheduler subprocesses and filesystem writes.

Private owner authentication/trust actions and separate exact-payload approval still precede live calls. The ceiling remains four smokes plus four scenarios, at most 600 seconds each, with fresh sessions and no retries.

### Copilot authentication modes

Copilot provider settings accept an optional `authentication` object whose `mode` is `process-token` (the default) or `native-existing-login`. Native mode freezes the standard HOME and effective provider-owned COPILOT_HOME, removes supported token variables from every child, and leaves native credential ownership and refresh with the provider. Credential values, account selectors and whole credential-storage hashes are excluded from evidence. Safe legacy trust/UI behavior, allowlisted user settings, repo overrides and inherited skill names/locations remain bound and rechecked. Unknown behavior keys, grants, providers and configuration layers invalidate setup.

Native preparation freezes repo hook/plugin/skill suppression, manual permission settings, disabled memory/IDE connection and exact inherited skill exclusions. Status uses bounded Content-Length RPC for status.get, auth.getStatus and models.list only, with supported CLI1.0.109/protocol3. Readiness records safe auth status and catalog support. Executing authentication, selector and accepted prompt configuration still require the separately approved observed smoke.

Native prompt argv limits available tools to bash/apply_patch, retains exact existing helper/write grants, disables built-in MCPs, custom instructions, updates and remote session sync, and adds ephemeral --trust-folder for each new session. Headless status omits this incompatible prompt-only flag. Native mode omits --no-bash-env because it persists a preference and instead validates absent/false inherited bashEnv plus a fixed child environment without BASH_ENV. The process-token route retains its private-home behavior.

Existing-login runs may update normal provider session indexes, session-state/<explicit-id>, caches and recent model/account bookkeeping. Scheduler repositories, state/output files, prompts, per-phase logs/share/usage artifacts and fresh session IDs stay disposable and pinned. These permitted provider bookkeeping effects must appear in the exact approval payload. No native execution or login/global trust mutation is performed by offline verification.

### Codex existing native login

Codex accepts optional `authentication` with mode `private` (the default) or
`native-existing-login`. Native mode requires CLI 0.167.1 and exact
`gpt-6.1-sol`/`medium`. Preparation performs bounded metadata discovery, freezes
component/skill identities and disabled user hooks, and derives one ordered
runtime override vector shared by app-server and exec. Native authentication
uses the invoking standard HOME/CODEX_HOME. Global configuration and credential
files are never copied or hashed. Safe native metadata provides the binding.

Every inherited MCP/plugin entry and user skill path receives an explicit
disable rule. Component inventory, native layers, feature state, disabled user
hook identity and interpreter/auth paths are rechecked. Unknown component names,
unsafe provider/tool configuration and enabled inherited hooks fail preparation.
Only the exact prepared project policy can become the active trusted hook.
Read-only preparation may record an untrusted-project configuration warning and
incomplete readiness. Preflight and execution reject that warning.

The controller retains standard HOME for provider-owned login. Shell children
receive an empty read-only `control/shell-home` as HOME and ZDOTDIR, inherit no
environment, and use the pinned interpreter PATH. BASH_ENV/ENV are excluded.
Prompts require `login=false` and `tty=false`. A modified shell-home invalidates
the preparation. Native metadata checks launch no sessions or turns. Existing
native indexes/cache bookkeeping remains provider-owned. Native context,
command/audit binding and qualification remain a dependent implementation task.

Preparation retains configuration warnings as sanitized, unclassified incomplete
setup evidence. Every warning blocks preflight/execution. Project layer identity
is pinned separately from its trust-dependent disabled status, allowing the
scoped project policy to become trusted while other layer drift still fails.

Native mode disables implicit `/tmp` and TMPDIR sandbox grants. Its prepared
repo/tmp roots remain explicit, keeping control/shell-home outside writable
locations even when the disposable run root is under `/private/tmp`.
