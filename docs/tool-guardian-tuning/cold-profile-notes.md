# Measured cold startup repair

The previous quoted-literal scan experiment did not establish an attributable
full-hook gain. Root restored that runtime diff and retained its public
characterizations, rejected patch and failed reports. This node began from the
exact extracted checkpoint and preserves all historical evidence.

The profile ran 25 alternating fresh-copy complete guardian launches for clean,
8787-character writer and dangerous writer-before/after cases across all three
providers, against the immutable original baseline and exact checkpoint.
Every launch had zero provider bytecode and checked the exact expected response,
payload hash and copied source hashes. Standard importtime and cProfile complete
entrypoints plus trusted-source compile observations are diagnostic only.
Profiler preload and main-source compilation exclusion are recorded explicitly.

The actual cold observations reproduced writer median gaps. Pure public `ast`
startup measured about 0.20 to 0.24 ms, so no private AST shortcut was selected.
The checkpoint policy helper's trusted-source compilation measured about 7 ms,
plus about 1.2 ms for its entrypoint, versus about 3.7 ms for the original
entrypoint. Cold denial formatting measured about 3.7 ms in cProfile, including
about 1.1 ms in tool-name sanitization from first-use regex compilation. These
instrumented figures identify a cause; they are not performance acceptance.

The approved repair is an exact tool-name sanitizer prerequisite. After the
same NFKC normalization of the first 4096 characters, an ASCII letters/digits/
underscore identifier has no separator required by URL, query, header,
assignment or flag credential patterns. Its characters are all regex word
characters, so token patterns can only start at its beginning. Case-insensitive
gh[pousr]_ and AKIA prefixes always use the original sanitizer. Every other
string, including Unicode, punctuation and whitespace, retains all original
regexes. The exact 160-character clipping remains unchanged. Action redaction,
policy inspection, AST parsing, budgets and all quote handling are unchanged.

Public banner/log characterization passed before source changes. Expanded
14-test controls pass with token prefixes, long token names, clipping, fullwidth
normalization, Unicode IGNORECASE variants, URL credentials, query values,
headers, assignment values and flags. Both native macOS Python 3.14.6 and 3.13.14
passed banners, shell/data13, native13, limits16 and corpus144. Generator25
passed on both versions and deterministic 29-file freshness is green. A freshness
command initially overlapped the Python 3.13 generator suite's deliberately
mutated fixture output; after serial completion it passed. No assertions were
removed or weakened. Native Windows was unavailable.

Root's aggregate fixture repairs were given serialized validation slots between
phases. They do not affect guardian source or the retained measurements. All
actual timing phases run alone on frozen source, with ordinary cache state for
warm comparisons and fresh zero-bytecode copies for cold comparisons.

Focused attribution and agreed-budget gate results are recorded separately
below after each phase. No parser-only, profile-only, pooled-provider or partial
matrix result establishes acceptance. Root owns the final formal agent-doc pass.
No real installation, push or global cache/configuration mutation occurred.

## Attribution on complete entrypoints

The frozen checkpoint/candidate comparison retained 600 fresh-copy launches,
25 per condition for each of 12 writer/provider cases. Every median improved,
by 0.318 to 0.570 ms. The original failing cases improved by 0.318 ms for Gemini
writer-after and 0.354/0.355 ms for Codex writer-before/after. The larger Copilot
writer improved 0.563 ms. These are attributable complete-hook observations
against the exact checkpoint, independent of the original-baseline budget gate.
They are small gains; remaining cold failures are not inferred fixed. All
actual/expected decisions, payload/source hashes and zero-bytecode preflights
are retained. Source remains frozen for the full cold and resource phases.
## Frozen gate checkpoint

The full cold matrix retained 7,350 independent fresh-copy launches, all 147
cases with 25 samples per condition. All decisions, source/payload hashes and
zero-provider-bytecode preflights passed. The raw matrix initially failed three
cases: Copilot writer-after (+5.228 ms median, +5.349 ms p95), Gemini recursive
remove current (+1.780, +10.664 ms), and Codex writer-before (+5.031, +5.250 ms).
That FAIL report remains unchanged. The exact three-case repeat retained 150
launches and passed: respectively +4.584/+4.758 ms, +1.738/+1.889 ms, and
+4.650/+4.884 ms. Root acknowledged this satisfies the agreed repeat procedure;
no failed observation was removed or pooled.

The separate 90-case resource CLI, 25 samples and 3 warmups, passed all expected
decisions and the 500 ms ceiling. Maximum observed elapsed time was 49.086 ms;
maximum native peak RSS was 22413312 bytes. The approved native macOS collector
ran alone. Source hashes before and after all measurements are identical.

The full matched warm B/C/C/B 147-case 25/3 comparison was not started in this
bounded dispatch and remains required before overall acceptance. Historical
zero-budget failures and the rejected quote-scan evidence remain historical
failures. No runtime process remains active at checkpoint. The exact repaired
snapshot is `/private/tmp/tool-guardian-profile-candidate`; the original baseline
is `/private/tmp/tool-guardian-baseline`. The maintained prepared warm driver is
`/private/tmp/tool-guardian-profile-warm.py`, with its retained source in
`evidence/cold-profile-warm-driver.txt`. Root will finish remaining verification
against these exact frozen hashes after integration.

## Final root validation

After conflict-free integration at 1a4610ad, root independently matched all 39 frozen source hashes against the committed manifest and candidate snapshot. Root ran the retained adapted warm driver without concurrent probes. Both complete 147-case pairs pass: maximum median deltas -1.841/-0.727 ms and maximum p95 deltas +1.618/+2.445 ms. All responses and source hashes match. The final comparison preserves the original cold failures and passing exact repeats.

The original four-worker diagnostics retain one isolated Gemini p95 increase with only four observations in the first pair; the second pair improves. A separate B/C/C/B repeat ran 25 four-worker batches per provider/condition after three discarded batches, retaining 1,200 measured public calls. Every provider's individual and batch median/p95 improves in both pairs. Sources remain frozen. Raw observations, repeated batches and comparisons are preserved rather than pooled or relabeled.

All source, correctness, latency and resource gates now meet the agreed criteria. Final canonical documentation remains the delivery step. Native Windows validation and real installed-hook validation remain unavailable or user-owned, respectively.
