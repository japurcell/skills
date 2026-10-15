# R1 T11 Spec supplement

Independent review on 2026-10-14 at `8f250431`: **no actionable findings.** T11 matches D3's scheduling contract without changing acceptance criteria.

The warm loop now follows pair, exact case, call index, then prescribed source order. Both homes and rows exist before invocation; matching IDs/payloads are required. Each full row retains first process, three warmups, 25 measured samples, invocation timestamps, and 29 completed-log checks.

Independent per-condition medians and p95 values remain unchanged, with each pair gated separately. There is no pooling, pairwise-difference quantile, budget relaxation, or case exclusion. Failed decisions and missing logs preserve partial rows and invocation evidence; timestamps do not replace maintained inner elapsed values.

Six targeted semantic tests passed, covering full-count adjacency, asymmetric quantile arithmetic, mismatched/missing/duplicate cases, public inert-script mechanics, cold-copy/logging behavior, and second-label failures.

Runtime, runners, and corpus are unchanged. Cold/resource/concurrency paths retain their prior behavior, supporting scoped reuse of resource evidence. Historical T10 failures remain rejected; T11 does not establish that they were noise. A new complete timing run is still required.

Original P1/P2 remain closed. All probes have finished; none remain running. The worktree is clean. No performance benchmark or RSS gate ran during this review. Native Windows and authenticated provider delivery remain unverified.
