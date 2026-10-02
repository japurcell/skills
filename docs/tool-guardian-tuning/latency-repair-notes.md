# Policy module extraction for full guardian startup

The final matched B/C/C/B experiment before this repair failed. Clean baseline
and candidate warm median pairs were 27.811/30.864 and 27.004/31.910 ms for
Copilot, 28.044/31.711 and 27.245/30.455 ms for Gemini, and 25.368/27.525 and
24.713/28.139 ms for Codex. 135 of 147 cases had positive candidate deltas in
both pairs; writers were about 3 to 8 ms slower. Previous failed candidates and
the final comparison remain evidence, not replaced by this experiment.

## Design

Python recompiles a script executed as the main program on each invocation.
The standard module-cache behavior is documented in [Python compiled modules](https://docs.python.org/3/tutorial/modules.html#compiled-python-files).
Moving provider-neutral policy into an ordinary imported provider-local helper
allows normal Python module bytecode caching. This change uses no custom cache,
cache deletion in live homes, payload evaluation, policy shortcut, or new runtime
dependency. The import runs before every input inspection. Cache-unavailable
execution still imports and compiles the complete source.

The canonical policy stays in `hooks/families/tool_guard.py`. It renders
byte-identical `helpers/tool_guard_policy.py` files into Copilot, Gemini, and
Codex trees. The five functions that depend on provider keys or native schemas
stay in each entrypoint: `read_tool_name`, `_read_tool_input_value`,
`read_tool_input`, `_native_tool_shape`, and `read_tool_scan_inputs`. Explicit
imports re-export every original policy function, class, and constant. The
entrypoint's `main` continues to resolve its own adapter bindings, including the
existing injected `read_json_input` failure tests. Missing or invalid local
policy imports emit the native internal-error deny response in both block and
warn modes.

The initial static audit found no `TOOL_PROVIDER`, `TOOL_NAME_KEYS`,
`TOOL_INPUT_KEYS`, or `SCRIPT_DIR` dependency in the neutral helper. All 48
original policy function and class ASTs remain exactly equal after extraction.
Of the original 72,290 policy bytes, 65,072 move to the helper. The adapter
portion, including explicit imports, is 9,069 bytes. Security matchers, nested
budgets, strict fallbacks, native operations, banners, redaction, and allowlist
logic keep their complete original bodies.

The ownership manifest adds three generated targets. Both Codex installers add
the helper to their exact copy lists; disposable-home installer tests require
the installed helper to match source. Copilot and Gemini deliver it through
their existing tree-copy paths. The helper has the same local trust assumptions
as the existing common and audit modules.

## Validation and evidence

The missing/corrupt local-helper E2E tests reproduced allow behavior before
extraction and now deny in block and warn modes across all three providers.
The Python 3.14.6 suites passed: generator 25 tests and deterministic check of
29 artifacts, shell/data 12, native 13, limits 16, banners 13, and public corpus
144. All three ordinary provider security shell suites passed. Bash and
PowerShell disposable-home installers passed, including actual installed
entrypoint allow/deny smoke checks. Native Windows was unavailable; the
PowerShell run on macOS skipped its junction check and establishes no native
Windows result.

The forced-reader Copilot/Gemini fixtures needed to copy the new dependency;
their original injected-reader failure and banner assertions remain intact.
The installed Gemini smoke initially shared a regular-file log path with
Copilot; distinct provider log paths repaired fixture setup. An initial
PowerShell fixture ran while generator tests deliberately mutated generated
outputs; serial execution passed. Generator mutation tests, installation
fixtures, and retained timing were subsequently serialized. No assertions
were removed, weakened, or bypassed.

The first frozen full B/C/C/B reports contain all 147 cases with correct actual
and expected decisions. Source and helper hashes stayed equal before and
after; normal helper bytecode started absent and was then populated by ordinary
imports. All 147 warm median deltas improved in both pairs. These reports and
the original strict zero-regression failure remain historical evidence.
The parent interruption for a user question cancelled that continuation;
it did not finish or establish cold acceptance.

The user subsequently agreed per-case warm limits of +2 ms median/+5 ms p95,
fresh zero-provider-bytecode cold limits of +5 ms median/+10 ms p95, and a
500 ms finite resource limit. The separately retained initial 36 clean/writer
fresh-copy observations are diagnostic, not full-corpus acceptance.

`startup-module-cold-25.json` retains 7,350 launches: all 147 scenarios, 25
independent fresh copies for baseline and candidate. Every launch checked zero
provider bytecode, matching copied source hashes, exact payload and expected
permission contracts, and a fresh disposable log home using the maintained
runner. The full cold matrix failed six cases. The 300-launch repeat of those
six scenarios also retains all raw observations. Three median violations
persist: Gemini writer-after +5.391 ms, Codex writer-before +5.147 ms and
writer-after +5.344 ms. Every repeated p95 delta was within +10 ms. The original
six failures remain retained, and overall cold acceptance remains FAIL.

The three warm p95 outliers were repeated with B/C/C/B 25 samples/3 warmups.
Hard reset, privileged command and Gemini actual-newlines writer improved
both median and p95 in both pairs. Exact reports and a frozen manifest are
retained under `startup-module-targeted-*`.

The resource matrix passed all 90 cases with 25 samples/3 warmups, exact
expected decisions, a maximum observed 43.097 ms and peak RSS 22,331,392 bytes.
The macOS RSS query ran under approved sandbox escalation. Its fingerprints
include the new helper. Native macOS Python 3.13.14 passed the public corpus,
shell/data, native/data, limits and security banner suites. The first validation
command used two mistaken script filenames; failed invocations remain in the
initial report, and the corrected existing suites passed in the repair report.
All 39 frozen source paths remain hash-identical after all measurements and
correctness checks. Source remains frozen.

## Remaining repair proposal

The persistent cold writer gap warrants a follow-up under this original node.
Concrete candidates include direct next-quote search for POSIX single-quoted
shell words while preserving raw consumer spelling and strict unsupported
provenance, and replacing the per-character quoted-literal scan in
Python preflight with a linear delimiter search that preserves escaped-quote
parity, triple quotes, malformed-input rejection, token/depth budgets and
complete inspection. It needs public red/green reproduction and security
coverage before implementation, followed by a new frozen cold matrix. No
source repair is inferred accepted from import profiles or the warm result.

Formal final `.agents` documentation synchronization remains root's session
responsibility. No real installation or global setting change was performed.
