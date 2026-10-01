# Shell and Python implementation evidence

Milestone 3 remains in progress until the security review and all-provider,
per-scenario latency gates pass. This document describes the implementation in
`hooks/families/tool_guard.py` and its three generated provider entrypoints.
The root coordinator owns the living ExecPlan and the final `.agents/` doc pass.

## Public behavior and implementation

Exact observed shell envelopes receive shell classification. Unknown schemas
keep complete strict input inspection. The forward shell representation keeps
word quote and expansion provenance, command boundaries, ordered redirections,
heredoc bodies, pipeline edges and nested substitutions. Consumer recognition
uses raw spelling; NFKC remains in strict rule matching and size accounting.
Partially quoted heredoc delimiters suppress expansion, while quoted bodies
sent to interpreters remain executable language input. Unsupported grammar and
Windows launchers receive complete strict fallback. Malformed quoting, missing
heredoc terminators and unresolved required interpreter operands fail closed
before warn mode or allowlisting.

Only the supported literal `rg` option grammar obtains a search-data proof.
Unknown pipeline endpoints or wrappers retain the legacy complete pipeline
matcher. Downstream shell/Python or unknown consumers disable upstream search
proofs, including intermediary commands such as `cat`. Literal pipe operators
in quoted or escaped shell words do not become pipeline edges.

Python parsing is lazy and starts only for established inline interpreter code
or supported quoted stdin code. The source is bounded before parsing by bytes,
syntax-token count and nesting, and afterward by AST nodes/depth and decoded
constant bytes. The resolver never executes payload code or imports its modules.
Whole straight-line pathlib writers and fixed guardian surveys obtain data
proofs; unsupported constructs retain complete source and constant inspection.
Known shell/subprocess/eval/exec sinks resolve literal strings and bounded
concatenation. Exact aliases, from-imports, dynamic standard-library imports and
wrapped interpreter operands are covered. Unknown required sink arguments deny.
Wrapper classes do not receive writer or survey data exemptions.

All 21 numeric PATTERNS and RULE_DETAILS identities remain. Strict fragments
share parsed token segments across matchers. Recursive-removal and protected-push
suffix summaries avoid repeated tail scanning and copying. Ordinary shell and
writer paths avoid the now-lazy `shlex` import. SQL comment/literal masking runs
only when a DELETE word is present. Banner/excerpt formatting stays in the
existing implementation and receives the same safe rule metadata.

## Reproduction and validation

Before implementation, public JSON entrypoints denied both recorded pathlib
writers and both guardian survey forms, and allowed the protected-push command
substitution and concatenated Python execution sink. The initial focused
reproduction demonstrated the wrong decision for all three providers.

The final fixed corpus runner currently reports `144 passed, 0 failed
(candidate)`. `scripts/test-tool-guard-shell-data.py` has 11 public-boundary test
methods covering recorded fixtures, option grammar, nested substitutions,
heredocs/order, unsupported writer constructs, aliases/rebinding/dynamic imports,
parser limits, SQL arguments, Windows fallback, raw consumer spelling and pipeline
wrappers. It executes only guardian entrypoints, constructing represented
operations from the shared numeric corpus. Its latest run is green.

The independent review's SEC-001 was a true new regression: `env`/`command` at
either pipeline endpoint bypassed the semantic pipeline matcher. The focused
public test first failed 18 provider cases; all now deny, including a search
piped through wrapped intermediate consumers into an interpreter. SEC-002 was
missing known-sink coverage in a wrapped Python invocation. The frozen earlier
source allowed it for all three providers, while the repaired source denies all
three. Neither represented operation was executed.

Other completed validation: native data tests 13 green; generated-hook tests 25
green; existing Copilot and Gemini Tool Guardian shell suites exited 0. Those
shell suites emitted existing observability read-only database diagnostics in
this sandbox. Codex/shared banner validation and registry registration are left
to milestone 4/root, which already owns the known legacy numeric boundary-test
repair. The new shell suite currently needs root `scripts/` on PYTHONPATH until
the private branch is rebased onto the integrated shared-corpus commit.

## Timing ledger and remaining gates

No optional optimization is claimed accepted from source inspection alone.
The benchmark is the unchanged root `benchmark-high-rate-hooks.py` using all
147 guardian scenarios, 25 warm samples, 3 warmups, 4 concurrent workers, fresh
disposable logs per scenario and all three public provider entrypoints.
Both retained snapshot manifests record SHA-256 hashes and UTC creation time.

Failed candidate 1 is retained with its frozen snapshot manifest. It validated
all decisions but failed the latency gate. Clean median/MAD milliseconds were
Copilot 30.815/0.191, Gemini 31.159/0.142, Codex 28.420/0.135. The 8787-character
writer medians were 32.356, 32.870 and 32.606, against baseline-2 medians 27.156,
29.918 and 24.866. Large ordinary shell medians improved to 38.975, 35.952 and
33.099 from baseline-2 73.512, 118.635 and 116.468. These improvements do not
offset per-case regressions. Candidate 1 predates the final wrapper repair and
the lazy-import/SQL precheck changes.

Two exploratory runs are excluded from acceptance: one used 20 samples and 6
workers, and one used 25/3/4 while generated source changed during measurement.
Their raw reports remain outside the repository. The first frozen run attempt
also failed before timing because its provider helpers had not been copied;
the valid retry included unchanged local helpers. No guard settings, installs,
global files or disabling switches were changed.

Candidate 2 was frozen at 2026-10-01T22:50:55Z after the wrapper repairs, raw
consumer recognition and lazy-import/SQL precheck edits. Its outcome is pending
below. Source stayed fixed during measurement. Final alternating baseline and
candidate evidence, cold/first-run variance, memory and growth measurements,
native Windows proof, boundary measurements and independent security acceptance
remain milestone-4 gates. Do not mark milestone 3 complete from the corpus or
one timing run alone.

Candidate 2 completed all 147 cases correctly and still fails the per-case
latency gate. Clean median/MAD milliseconds were Copilot 32.382/0.647, Gemini
32.732/1.129 and Codex 29.908/0.723. The 8787-character writer medians were
34.226, 34.705 and 31.952. Large shell medians were 40.277, 37.145 and 34.160.
These runs are comparable methodologically but were not alternating samples;
do not infer that an optional micro-optimization succeeded from them. The
additional embedded policy's parsing and runtime work remain startup concerns.

After that frozen run, exact consumer spelling was tightened to bare `rg` and
the observed Python spellings (plus this hook's exact `sys.executable`). A path
merely ending in those names cannot obtain a data proof. Conservative known-sink
inspection still recognizes bounded versioned Python names and arbitrary paths.
Wrapper and unsupported-option Python inspection explicitly disables data proofs.
The review's SEC-003 reproduced nine public Python failures for warning/runtime
option prefixes. The shared inline-operand selector now inspects options with
values and attached values before `-c`, without granting a proof to their
unsupported invocation shape. Quote-concatenated shell words through an option
prefix likewise changed from allow on frozen candidate 2 to deny on the final
source for all three providers. The final focused suite and fixed corpus are
green after these changes. Candidate-2 hashes therefore differ from final source;
its report is evidence of the earlier failed candidate, not final acceptance.

Retained raw evidence is `evidence/shell-candidate-1.json` and
`evidence/shell-candidate-2.json`, with matching `-manifest.json` files. Repeated
token full-hook growth, memory, normalization expansion and final paired timing
are explicitly outstanding milestone-4 work. Both failed timing runs are retained.

Official decisions were checked against Python 3.14's AST/shlex documentation
and the saved shell exploration notes. Parser grammar varies across releases;
the supported node subset uses longstanding public AST types, while new shapes
fall back to complete strict scanning. Runtime observed here was Python 3.14.6.
Sources: https://docs.python.org/3/library/ast.html and
https://docs.python.org/3/library/shlex.html. Native Windows and older-runtime
validation remain unverified. The Bash redirection documentation fetch failed;
the authoritative saved exploration notes supply the ordered-heredoc contract.
