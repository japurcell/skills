# R1 T11 Standards supplement

Independent review on 2026-10-14: **no new required findings** on immutable `8f250431`, reviewing `51064b2b...8f250431`.

The adapter implements D3's schedule: pair, exact case, call index, then fixed `ORDER[pair]`. Both conditions are prepared before invocation. Full rows retain one first process, three warmups and 25 measured samples; mechanics counts remain unchanged. Exact IDs and payload bytes are checked while native expectations remain condition-specific.

Invocation timestamps bracket the maintained call without replacing its inner elapsed measurement. Both rows exist before execution; decision and logging failures retain partial results and invocation evidence. Independent median/p95 subtraction and separate pair gates are unchanged.

Independent checks:

- **12 bounded semantic/mechanics tests passed**, covering adjacency/counts, ID/payload rejection, sample boundaries, inner elapsed/default behavior, second-condition failure evidence, independent quantiles, isolated pair failures, all 156 cases, legacy logging exceptions, source mutation and output preservation.
- Confirmed an empty runtime, maintained runner, corpus and registry diff.
- Inspected unchanged cold, concurrency, resource and `warm_run` paths. Their default `checked_invocation` behavior remains intact, supporting reuse of prior resource evidence for unchanged interactions.

No new structural heuristic warrants a finding. The earlier optional trusted-launch formatting duplication suggestion remains separate and nonblocking.

Historical rejected timing results remain rejected. This review establishes neither a performance pass nor an explanation for those failures; V1 still requires the new complete timing run. Native Windows and authenticated provider delivery remain unverified.

No timing/RSS benchmark ran. Worktree is clean, and all reviewer test/probe processes have stopped.
