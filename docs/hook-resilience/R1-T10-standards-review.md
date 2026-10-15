# R1 T10 Standards supplement

Independent review on 2026-10-14: **no new required findings** on immutable `864bbda0`, reviewing `ef7a31e4...864bbda0`.

The repair follows T10/D2 and preserves the documented transport and reporting boundaries. POSIX immediate reads restore descriptor flags through `finally`; Windows retains readiness authority. Structural scanning preserves chunk-spanning escapes, container depth and completion checks while leaving `json.loads` as syntax authority. Raw charging, idle/total deadlines and bounded trailing drain remain intact. The ASCII label prefilter covers every existing regex alternative; potential credentials and non-ASCII normalized labels retain the unchanged regex authority.

Independent semantic checks passed:

- **9 transport tests:** public structural/escape splits, retained incomplete input, raw/depth/trailing rejection, descriptor restoration on success/error/timeout, EOF/EAGAIN distinction and simulated Windows adapter behavior.
- **3 reporting tests:** embedded credentials, Unicode/NFKC and clipping cases, benign trigger substrings, warning/denial/clean logging and audit-failure enforcement.
- **3,618 independent deterministic JSON/chunk oracle checks**, including malformed, truncated, trailing and depth-boundary inputs.
- Generated freshness for **38 files**. Transport collection is identical across four generated common helpers; provider-neutral scanner, diagnostics and policy-helper comparisons also passed.

No new structural heuristic warrants a finding. The earlier optional launch-renderer duplication suggestion remains separate and nonblocking. The original credential-disclosure finding remains closed.

This is bounded semantic review, not performance acceptance. Full release timing/resources, native Windows execution and authenticated provider delivery remain separate. No benchmark ran; worktree is clean, and all reviewer test/probe processes have finished.
