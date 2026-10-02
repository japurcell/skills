# Bounded literal scan repair

The extracted-policy checkpoint retained three repeated cold writer median
violations above the agreed +5 ms allowance: Gemini writer-after +5.391 ms,
Codex writer-before +5.147 ms and writer-after +5.344 ms. Those failed reports
remain unchanged. This follow-up changes no thresholds or policy decisions.

The public seam is the generated provider guardian receiving its ordinary JSON
stdin envelope. Before source edits, the expanded 13-test shell/data suite
passed with escaped single/double/triple Python literals, a long backslash run,
protected operations proven inert inside complete pathlib writers, subsequent
execution sinks, POSIX literal search data and malformed literals in warn mode.
This is behavior characterization; no artificial semantic failure was created.

Only two scans changed. POSIX single-quoted content has no escape or substitution
semantics, so the representation copies the span up to the next quote. Empty
spans add no word piece. Python preflight finds the next single/triple delimiter,
then counts its immediately preceding backslash run. An even run closes the
literal; an odd run skips the escaped first quote and resumes one character
later, preserving overlapping triple delimiters. Searches advance monotonically;
escape runs already passed are not revisited. Missing delimiters retain the
same incomplete-inspection failure. Entire source byte charging, syntax token
and depth charging, AST inspection and strict fallback remain complete.

All affected Python 3.14 suites passed: shell/data 13, exact limits 16, native
13, corpus 144, banners 13, generation 25 and deterministic 29-artifact check.
Native macOS Python 3.13 passed shell/data, native, limits, corpus and banners.
All three ordinary provider security shell suites passed. Existing tests retain
quoted/unquoted heredocs, substitutions, Windows strict fallback, aggregate
256/257 matcher tokens and 1024/1025 Python syntax tokens. Native Windows was
unavailable. No assertions were removed or weakened.

A diagnostic exhaustive preflight comparison over 488,281 strings found zero
outcome differences for the checkpoint and repair. This private-function check
is diagnostic only; public complete-hook suites and timings establish acceptance.

The exact checkpoint and candidate source copies were frozen before retained
measurements. Ordinary module caches are allowed for warm comparisons. Every
cold launch uses a separate fresh provider source copy with zero bytecode and a
fresh disposable log home, preserving maintained payload and decision contracts.
Focused checkpoint comparisons precede the full original-baseline comparisons.
Source inspection and diagnostic equivalence supply no performance acceptance.

Formal final agent-document synchronization remains root's session responsibility.
No real installation, push or global configuration change was performed.

## Focused attribution result

The 600 fresh-copy launches against the exact extracted checkpoint preserved
all decisions and frozen source hashes. Across the 12 writer cases, median
deltas ranged from -0.223 to +0.475 ms. The previously failing cases changed
by -0.134 ms for Gemini writer-after, -0.071 ms for Codex writer-before and
+0.072 ms for Codex writer-after. These observations do not demonstrate an
attributable gain sufficient to repair the repeated cold failures. The result
is retained honestly; full original-baseline comparisons are separate evidence.

## Rejected candidate checkpoint

The full warm B/C/C/B matrix retained all 147 correct decisions per report. One
isolated Gemini writer p95 violation remains unverified: +5.968 ms in the first
pair, with an improving second pair. The full cold matrix retained 7,350 fresh
launches, matching source hashes and correct decisions, but failed 12 cases.
The original repeated writer gaps persisted: Gemini writer-after +5.476 ms,
Codex writer-before +5.152 ms and writer-after +5.113 ms.

The machine/context clock advanced overnight past the 01:03:01 UTC dispatch
deadline. The worker stopped new runtime work on observing the advance, and
root interrupted the worker on notification. Resource validation, warm
attribution and targeted repeats did not run for this candidate. Earlier
resource results certify their earlier frozen source only.

Root verified the retained candidate hashes and cold record count. Because the
candidate demonstrates no attributable cold gain and does not meet acceptance,
root restored canonical policy and all three generated helpers to the extracted
checkpoint. The exact rejected canonical diff is retained in
`evidence/literal-repair-rejected-canonical.patch`; applying it to f6831fe0 and
regenerating reproduces the measured candidate. New public characterization
tests passed before that source change and remain useful security coverage.
Failed reports and their original fingerprints remain unchanged. This dispatch
is timed out, not completed or approved. Cold acceptance still requires repair.
