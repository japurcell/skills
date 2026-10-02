# Independent optional optimization validation

This evidence compares frozen variants of the final milestone 4 policy at
`f47d51ddd6a9d05956f24f5f18ee59c4bbf3e60b`. No represented operation is
executed. Only provider Tool Guardian entrypoints receive inert JSON inputs.

The common-helper comparison substitutes the three provider `helpers/common.py`
files from `5f1aa7e` into otherwise identical final provider trees. The suffix
comparison substitutes only `_match_recursive_rm_target` and `_match_git_push`
from the trusted canonical policy literal at `9bcc6ff5`. Both comparisons retain
the final quote-aware shell representation and cached segment provenance.

The public seam is each provider's stdin JSON event and native permission JSON
response. Candidate decisions for all 144 corpus cases and targeted role,
quoting, Windows-launcher, option-terminator, and dangerous controls gate timing.
The intended timing protocol is two alternating before/after passes, 25 samples
and three warmups, separate providers and cases, identical disposable log homes,
first-process observations, and four-worker clean concurrency. Raw samples and
source fingerprints must remain alongside the result.

Token reuse is required architecture: it preserves quote and Windows semantic
provenance across rules. No performance claim will be fabricated by adding
unused work to an artificial uncached comparator. The overall fixed-corpus
latency gate remains separate from attribution of optional optimizations.

At 2026-10-01 23:39Z the root granted this worker an exclusive measurement
window. The definitive correctness report passes 594 checks: each of three
variants passes all 144 corpus decisions, including malformed JSON, plus 54
targeted and growth controls. All provider payloads and expected decisions are
identical across variants. The manifest proves that only the three intended
common helpers or the three matcher-bearing entrypoints differ.

The exploratory first report contains nine failures from an incorrect initial
expectation for a quoted Git configuration-value example. Every variant denied
that unsupported command consistently. The established contract retains strict
fallback for unsupported constructs, so its definitive expectation is deny.
The report is preserved as `optimization-correctness-exploratory.json`, not
silently discarded. Both removal option-terminator controls pass identically;
the initial static concern about their suffix semantics was not reproduced.

All three initial variants pass 594 checks. The additional Git-only variant
retains final removal summaries, quote-aware cached segments, and final helpers,
substituting only `_match_git_push`. It and the final variant pass 432 checks:
144 corpus decisions and 72 targeted/growth controls per variant.

The common and combined suffix reports each retain 204 scenario runs, 5,100 raw
warm samples, 204 first observations, and 12 four-worker clean batches. Their
51 provider/case scenarios run in before/after/after/before order, with 25
samples after three warmups. The additional Git-only report retains 72 scenario
runs and 1,800 samples covering safe and dangerous adjacent git/push arguments
at 64, 128, and 250 tokens. Each invocation is a complete subprocess through
the existing benchmark `invoke` API, using Python 3.14.6 and identical inputs
and log conditions. Operating-system file caches are not cleared.

`optimization-comparison.json` keeps provider/case results separate, including
both paired median changes, p95, MAD, first observations, and raw concurrency.
Its explicit conservative screening rule calls a median benefit or regression
clear only when both paired changes exceed the largest per-run MAD or repeated
same-variant median span. This is a screening rule, not a statistical confidence
interval or the overall acceptance gate.

The common helper has 31 clear benefits, zero clear regressions, and 20 noisy
or inconclusive comparisons. Clean Copilot medians change from 33.865/33.142 ms
to 30.375/30.986 ms; Gemini changes from 33.010/33.898 to 30.930/31.837 ms.
Codex changes from 30.668/32.630 to 28.933/28.063 ms, but the first pair is inside
the observed repeated-run span. These independent results support retaining
lazy common imports. They do not establish the complete candidate latency gate.

Removal summaries have a strong repeated-token benefit. At 250 tokens the two
paired gains are 7.352/6.998 ms for Copilot, 8.595/9.166 ms for Gemini, and
9.071/6.252 ms for Codex. The original Git configuration-value workload chiefly
stresses the unchanged `push_index` traversal and supplies no repeatable suffix
benefit. The separate Git-only adjacent-head workload reaches each push head
immediately and exposes the actual old repeated suffix traversal without
adding artificial unused work. At 250 safe tokens, Gemini improves 2.503/3.879
ms and Codex 3.525/2.971 ms beyond observed noise. Copilot's 2.677/1.006 ms gains
remain inconclusive against its 1.702 ms repeated-run span. The Git-only report
has six clear benefits, zero clear regressions, and 12 inconclusive results.
Small or neutral cases are not claimed as speedups.

The combined suffix report also records an unresolved Codex JSON-survey median
regression: 28.858/28.942 ms before versus 30.431/29.973 ms after, beyond its
0.995 ms observed noise. Preserve this finding; the growth gains cannot offset
a frequent-path slowdown. Source compilation and startup cost remain possible
causes to investigate with a separately frozen repair. These results support
the individual growth optimizations but do not accept the combined candidate.
The root separately reports a failed fixed-corpus latency gate.

No clean uncached comparator was introduced: the available original tokenizer
loses quote and Windows provenance, so replacing it would measure different
policy semantics. Token reuse remains a correctness obligation, with acceptance
through the public corpus and overall latency gate, rather than an invented
independent speedup.

To reproduce from the proof checkout, run `python3
scripts/benchmark-tool-guard-optimizations.py prepare` with a new
`--variant-parent` and `--evidence` directory. Then run the `validate`, `measure
--group common`, `measure --group suffix`, `prepare-git`, `validate-git`,
`measure-git`, and `compare` phases sequentially. Do not overlap hook probes or
other measurements. Manifests retain every maintained provider Python SHA256,
trusted reference revisions, and the exact construction method. Fresh variant
preparation refuses existing roots, and a changed fingerprint prevents timing.
The helper's syntax, help, and stale-fingerprint CLI checks pass, with no hook
subprocesses invoked by those checks.

Status at 2026-10-01 23:53Z: all optional evidence collected and measurement
windows released. No installed hook, canonical policy, generated output, or
shared test registry was changed. Overall candidate acceptance remains open.

The interrupted worker checkpoint was saved by root, reviewed for source fingerprints, sample counts and CLI evidence, and integrated at `d602bbe1` after a conflict-free rebase. The frozen policy content tested at historical private revision `f47d51dd` is retained on the topic history at `84eae394`. For replay after later policy-helper extraction, create a disposable Git worktree at `84eae394`, then invoke this benchmark helper from the topic checkout with `--root` pointing to that worktree and fresh variant/evidence directories. The current extracted entrypoints are not the original ablation source. The worker reached its runtime deadline before committing; that timed-out status is not final candidate approval.
