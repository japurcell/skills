**Before dispatch**
Each reviewer needs resolved assignment fields (`identifier`, `objective`, `context`, `constraints`, `deliverable`, `verification criteria`, `allowed resources`, `write ownership: none`, `dependencies: none`, `runtime limit`). Each route needs `dispatchable: true`, current valid task facts/capabilities/constraints, exact runtime-supported `model` and `reasoning_effort` (no omitted, null, inherited, placeholder, ranged, or runtime-selected values), an explicit runtime limit with monitoring, satisfied dependencies, and no pending approval. Keep complete router decisions in memory for dispatch and verification.

**Route file**
Not required. Do not write a route file or completion ledger since no user request, recovery need, or audit requirement applies.

**Chat reporting**
Announce both reviewers' roles and scope in one concise sentence. Do not ask for model/effort approval or show raw routing/audit data unless requested; report only blockers or material failures.

**Dispatch and verification**
Start both independent reviewers in parallel before waiting. Submit exact `model` and `reasoning_effort` through dispatch controls outside worker prompts. Keep workflow routing/audit metadata and self-reporting instructions out of prompts; prohibit nested delegation and state shared-codebase/read-only rules. Verify compliance by inspecting actual dispatch arguments and runtime-control state against routed values, plus runtime limit monitoring.

**Unavailable execution metadata**
Distinguish selected, submitted, and executed settings. Only runtime metadata confirms executed values; without it, record executed settings as `unconfirmed` (never rely on worker self-reports).