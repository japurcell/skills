# Resource and latency validation

Milestone 4 acceptance is open. This document records the public hook boundaries,
measurement method, and observed failures. Unfinished checks are not passing evidence.

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
128. Native aggregate data is provisionally 65536 UTF-8 bytes including destination
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
The proposed final-form byte maximum is 32768. It is provisional until correctness
and complete subprocess resource checks pass.
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
before enforcing its node bound. Source repairs await exclusive canonical-source
ownership after milestone 3 integration. The public response may already deny a
large list; that alone does not prove bounded auxiliary inspection work.

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
Subsequent optimizations and paired reports remain outstanding.

For raised limits, run the exact generated scripts in full subprocesses on accepted
and rejected boundary inputs, repeated tokens, nested structures, quotes,
normalization expansion, decoded Python strings, and malformed prefixes. Record
elapsed runtime and complete-process peak resident memory with the operating
system resource collector. Select and enforce a ceiling based on the measured
existing workload plus documented margin, then compare it with configured
deadlines. Parser-only timings cannot establish this ceiling.

Codex's registered guardian deadline is 10 seconds; Copilot's is 10 seconds.
Gemini's guardian registration has no explicit timeout, so this document does not
invent one. Complete hook subprocess timing excludes provider launch and delivery.
Native Windows execution is unavailable on this macOS host. Simulated branches
and PowerShell skips do not establish native Windows public-envelope acceptance.
No real installation or installed-provider timing is performed.
