# Resource and latency validation

Milestone 4 acceptance is not met: correctness and the finite resource workload
pass, but the paired fixed-corpus latency gate fails. This document records the
public hook boundaries, measurement method, and retained evidence.

The maintained limits suite uses the generated provider stdin/stdout interface. It
passes represented operations as JSON and never executes them. Every accepted
maximum must allow silently. The immediately larger input must deny in both block
and warn modes with its actual count, threshold, and unit. Structural, token, parser,
and encoding cases also supply a valid exact matching allowlist entry whose input
is at most 8192 characters. A dangerous-operation control proves that the same
allowlist encoding actually matches. Oversized byte fixtures cannot supply a valid
allowlist entry and do not claim to prove that precedence.

## Selected resource bounds

The candidate retains 32768 bytes/characters for strict text, 128 executable
commands, 256 total executable tokens, structural depth 32, nodes 256, and strings
128. Native aggregate data is 65536 UTF-8 bytes including destination
and dictionary keys. The preserved 46899-byte patch occupies 71.6% of that budget,
leaving 18637 bytes before key accounting. Native body line count does not consume
the executable command limit. Parser work is separately bounded before parsing:
syntax nesting 32 and lexical tokens 1024; after parsing, AST depth 32, nodes 2048,
literal bytes 32768, and resolved-string bytes 32768. Recursive executable
inspection uses depth 16 and aggregate normalized bytes 32768.

The 2048 AST-node guard and 32768 literal-byte guard may be dominated by earlier
syntax-token and aggregate executable-byte limits on this public interface. Exact
maximum/first-rejected claims for these guards require a reachable fixture, or a
documented proof of the earlier limiting boundary. They must not be represented
as tested merely because their constants exist. The syntax depth fixture uses
parentheses to avoid consuming AST depth; the AST depth fixture uses a flat
operator chain to avoid consuming syntax nesting.

Normalized native operation paths need a separate bound on their final NFKC,
casefolded form. This only bounds inspected metadata; it does not inspect native
body text as executable code or introduce destination policy. The test fixtures
include ASCII, U+FDFA compatibility expansion, and U+0390 casefold expansion.
The validated final-form byte maximum is 32768. Correctness and full subprocess
resource checks pass for the maintained finite workload.
The budget is aggregate across all inspected delete/move paths in one patch;
several separately bounded paths must not multiply normalization work. Patch
allowlist entries contain escaped newline separators and are invalid under the
existing allowlist contract, independently of their size. These operation-boundary
cases therefore exercise warn precedence without claiming valid allowlist proof.

## Reproduced resource gaps

On 2026-10-01 at 22:49 UTC, the native-only candidate allowed a delete-patch path
whose ASCII normalized form was 32769 bytes in block and warn modes. It also
allowed 32769-byte final forms created by U+FDFA compatibility expansion and
U+0390 casefold expansion. Accepted 32768-byte forms allowed. The public limits
test reproduced six overflow failures before source changes.

Static review additionally found Copilot search-list schema checks traversing all
items before structure validation and structure traversal pushing every child
before enforcing its node bound. The repair validates schema cardinality before
scanning lists and traverses structures through lazy iterators. The public response may already deny a
large list; that alone does not prove bounded auxiliary inspection work.
Static Python preflight review found the quoted-literal branch increments its
token counter and then continues without checking the threshold. Adjacent string
literals ending at EOF can exceed 1024 syntax tokens while parsing to a single
constant. The public suite includes 1024 and 1025 adjacent literal tokens.

After milestone 3 integration, the public interface also reproduced quoted
unproved argument overflows across all three providers in block/warn modes, and
an adjacent literal-token overflow in a proven fixed writer. The latter fixture
includes prefix tokens so its total preflight counts are exactly 1024/1025.
Inspection now charges flattened strict matcher tokens, redirection operands,
unproved heredocs, unsupported shell/Python source, constants, and SQL operands
against the aggregate 256-token budget while crediting already counted lexical
slots. Proven data remains excluded. The public limits suite reports 16 passed;
the fixed incident/protection corpus reports 144 checks passed. Shell, native,
and security-banner suites report 11, 13, and 13 passed respectively.
Generator freshness covers 26 outputs and its suite reports 25 passed. All three
provider Bash guard suites exit zero. The benchmark CLI suite reports two passed;
the aggregate registry contract reports 14 passed. Copilot/Gemini Bash fixtures
also print existing readonly observability-database diagnostics; their guardian
assertions pass. This is not evidence of installed observability correctness.

Structural limits bound inspection after provider JSON decoding. Existing common
readers do not provide a universal raw-envelope byte limit before decoding;
Codex's reader has no explicit total raw-byte cap. A 30000-node resource fixture
therefore measures that finite envelope only. Its RSS result cannot establish a
universal memory ceiling for arbitrarily large raw JSON. A raw-reader limit is
separate work outside this canonical classifier repair.

## Comparison method and acceptance

Retain paired, sequential baseline/candidate reports in alternating order B/C/C/B
or B/C/B/C, with the same frozen script versions, runner, corpus, Python executable,
logging paths and conditions, 25 measured samples, three discarded warmups, and
four workers. Do not run correctness suites or other hook probes during timing.
Every invocation starts a new Python process. Retain raw per-case samples,
expected/actual decisions, first-run samples, and concurrency batches. First-run
means a fresh log home with uncleared operating-system caches, not a fully cold
process launch.

Compare each provider and scenario separately, including formerly denied
legitimate operations. Report median and p95 changes, within-run median absolute
deviation (MAD), and variation between repeated baseline medians. Keep repeated
first runs and four-worker clean batches separate from sequential samples. Two
runs provide descriptive variation rather than confidence intervals. A repeatable
positive latency delta fails the gate. A result overlapping variation is
inconclusive until repeated evidence supports no measurable regression. Do not
pool providers or workloads or exclude correctness fixes from the comparison.

The first frozen milestone 3 exploratory report failed the no-regression gate
for clean calls and Python writers. It is failure evidence, not acceptance.
The final paired reports also fail, as recorded below. Further optimization and
new frozen measurements are required before acceptance can be met.

For raised limits, run the exact generated scripts in full subprocesses on accepted
and rejected boundary inputs, repeated tokens, nested structures, quotes,
normalization expansion, decoded Python strings, and malformed prefixes. Record
elapsed runtime and complete-process peak resident memory with the operating
system resource collector. Select and enforce a ceiling based on the measured
existing workload plus documented margin, then compare it with configured
deadlines. Parser-only timings cannot establish this ceiling.

`scripts/benchmark-tool-guard-resources.py` implements this separate resource pass.
It uses the same direct `sys.executable` script launch as the fixed corpus runner
for elapsed samples, then starts a separate `/usr/bin/time -l` process for peak
resident memory. The time wrapper is excluded from elapsed samples. Default
sampling is 25 measured launches and three discarded warmups. Its required
`--ceiling-ms` argument must have a documented measured basis. It fingerprints
entrypoints, local Python helpers, and canonical source before/after and rejects
source mutation during the run. Results preserve every raw elapsed sample and
peak RSS in macOS bytes. The approved completed resource run is retained as
`docs/tool-guardian-tuning/evidence/final-resources.json`.

The final combined source also passes focused correctness on native macOS Python
3.13.14: 144 corpus checks, 11 shell tests, 13 native tests, and 16 resource tests.
Final generation freshness confirms 26 outputs. This cross-version check does
not establish native Windows acceptance.

The retained final measurement sequence is `final-baseline-1.json`,
`final-candidate-1.json`, `final-candidate-2.json`, `final-baseline-2.json`, all under
`docs/tool-guardian-tuning/evidence/`. Each report completed with 147 scenarios,
25 measured samples, three discarded warmups, and four-worker clean concurrency.
Both baseline runs use the immutable snapshot; both candidate runs use the final
combined classifier and startup helper. Performance interpreter is Python 3.14.6
at `/Users/adam/.pyenv/versions/3.14.6/bin/python3`. No hook probes overlapped these
measurements. `final-candidate-scripts.sha256.json` fingerprints final scripts,
helpers, and canonical classifier source. Final timing finished at 23:27 UTC.

## Retained resource result

The approved resource CLI run completed 90 scenarios with 25 measured samples,
three discarded warmups, and a separate peak-RSS pass for each scenario. Every
expected decision and the 500 ms runtime ceiling passed. The report's script and
helper fingerprints match `final-candidate-scripts.sha256.json`, identifying the
exact source frozen for the original `f47d51dd` checkpoint.

The maximum elapsed sample or first run was 60.986583 ms for
`gemini.resources.strict-max`. Maximum peak resident memory was 28229632 bytes for
`copilot.resources.native-wide-paths-overflow`. These are full subprocess
measurements of the 90 finite fixtures after normal provider JSON decoding;
they do not bound arbitrary raw envelopes or provider launch/delivery.

The first sandboxed collector attempt failed when macOS `/usr/bin/time -l`
could not perform its kernel `sysctl` resource query. That failed collection is
not passing evidence. An approved retry against the same frozen source completed
successfully and produced the retained report. No source repair was needed for
the collector permission issue.

The 500 ms ceiling is 3.72 times the maximum observed existing retained workload
sample, 134.263375 ms (`codex.guard.large` in `baseline-1.json`), and below both
configured 10-second deadlines. Passing that resource ceiling does not establish
the separate no-added-latency requirement.

## Failed paired latency gate

`docs/tool-guardian-tuning/evidence/final-comparison.json` preserves all 147
provider/scenario rows with paired median deltas, p95 values, within-run MAD,
baseline median span, repeated first runs, and all four concurrency batches.
The report describes variation rather than claiming inferential significance.
Both paired median deltas are positive in 135 of 147 rows. Formerly denied
legitimate inputs remain included in that same-input comparison.

The clean-call regression is reproducible across all three providers. The
candidate-minus-baseline median deltas exceed the baseline median span and the
individual within-run MAD values:

| Provider | First paired delta (ms) | Second paired delta (ms) | Baseline median span (ms) | Within-run MAD range (ms) |
| --- | ---: | ---: | ---: | ---: |
| Copilot | +3.053 | +4.906 | 0.807 | 0.187-0.697 |
| Gemini | +3.667 | +3.210 | 0.799 | 0.111-0.694 |
| Codex | +2.157 | +3.426 | 0.655 | 0.151-0.592 |

Clean-call p95 is also higher in both candidate runs for every provider. Repeated
first runs and the noisy four-worker batches remain separately retained; they
are not pooled to obscure these slower sequential paths. The no-measurable-
regression gate therefore fails. Resource success and corrected false positives
do not waive that failed gate. Milestone 4 and full implementation acceptance
remain not met pending optimization and another frozen paired comparison.

Codex's registered guardian deadline is 10 seconds; Copilot's is 10 seconds.
Gemini's guardian registration has no explicit timeout, so this document does not
invent one. Complete hook subprocess timing excludes provider launch and delivery.
Native Windows execution is unavailable on this macOS host. Simulated branches
and PowerShell skips do not establish native Windows public-envelope acceptance.
No real installation or installed-provider timing is performed.
