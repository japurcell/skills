# T3b, migrate the readers

Once the T3a matrix exists and corrected M2 outputs are integrated, render a single readiness/chunk/completion implementation from `hooks/families/common.py` into the family outputs and standalone Codex executable. Pass a consumer policy for completion, whitespace, limits and deadline behavior. Return original bytes or a classified read failure to the consumer. Preserve the bounded reader's incremental state across chunks. Use `hooks/manifest.py` and the generator for newly rendered output. Migrate one reader at a time against the captured streams, then exercise all three from the integrated checkout. Stop after the suites and native Windows/POSIX comparison.

The hook implementer owns the rendered byte reader, its three consuming adapters, generated files and parity checks. Use the captured T3a reference as the oracle. Begin after the corrected M2 outputs are integrated. Stop after regenerating and exercising the cases and commands in the milestone. Record Windows gaps separately.

Use the [milestone contract and verification commands](3-hook-input.md) and the [integration plan](../ExecPlan.md). Record results and remaining evidence here.
