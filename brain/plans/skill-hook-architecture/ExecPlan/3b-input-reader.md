# T3b, migrate the readers

Once the T3a matrix exists and corrected M2 outputs are integrated, render a single readiness/chunk/completion implementation from `hooks/families/common.py` into the family outputs and standalone Codex executable. Pass a consumer policy for completion, whitespace, limits and deadline behavior. Return original bytes or a classified read failure to the consumer. Preserve the bounded reader's incremental state across chunks. Use `hooks/manifest.py` and the generator for newly rendered output. Migrate one reader at a time against the captured streams, then exercise all three from the integrated checkout. Stop after the suites and native Windows/POSIX comparison.

The hook implementer owns the rendered byte reader, its three consuming adapters, generated files and parity checks. Use the captured T3a reference as the oracle. Begin after the corrected M2 outputs are integrated. Stop after regenerating and exercising the cases and commands in the milestone. Record Windows gaps separately.

Use the [milestone contract and verification commands](3-hook-input.md) and the [integration plan](../ExecPlan.md). Record results and remaining evidence here.


## Result and evidence

On 2026-11-19, Darwin 27.2.0 arm64 and Python 3.14.6, the candidate renders one shared readiness, collection and completion implementation into the bounded common reader, RTK wrappers and standalone Codex required-skills hook. Policies retain the common incremental structural scanner, byte/depth/marker and total-deadline checks, RTK's original bytes and object admission, and Codex's byte limit and diagnostics. The standalone Codex hook is now a manifest-owned generated target. Its runtime remains self-contained.

`rtk proxy python3 scripts/tests/hooks/test-input-baseline.py` passed against the archived `069b3f22` processes after each reader migration and on the combined tree. The matrix includes a buffered scalar split at the 4096-byte boundary: before the fix Codex produced `trailing data`, while the original reparsed and reported `expected a JSON object`; it now matches. The exact NBSP, held-open pipe, delayed chunks, UTF-8, limits, malformed cases and RTK byte-forwarding outcomes remain those recorded in [T3a](3a-input-baseline.md).

The following exited 0 on the combined candidate: `bash scripts/tests/hooks/test-hooks-rtk.sh`, `bash scripts/tests/hooks/test-gemini-hooks-rtk.sh`, `bash scripts/tests/hooks/test-codex-hooks-startup.sh`, `python3 scripts/tests/tooling/test_helpers.py` (8 tests), `python3 scripts/tests/hooks/test-brain-hooks.py` (27 tests, one skipped), `python3 scripts/tests/hooks/test-generate-hooks.py` (12 tests), and `python3 scripts/generate-hooks.py --check` (16 current files). All were invoked with `rtk proxy`. A simulated Windows idle-pipe check in both RTK suites passed; this is not native Windows proof. Native Windows pipe and full integrated acceptance remain pending. Reflection found no additional durable note or skill improvement; the boundary is encoded in the fixture and existing hook-testing guidance.
