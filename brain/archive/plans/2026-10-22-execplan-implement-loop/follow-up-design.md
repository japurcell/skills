# Follow-up policy and readiness facts

- Scope: Gemini CLI 0.65.0 only; checked 2026-10-28. Current executable contract is D1-D5 in [ExecPlan](ExecPlan.md#follow-up-contracts-t7-t12).
- Pinned [CLI config](https://github.com/google-gemini/gemini-cli/blob/v0.65.0/packages/cli/src/config/config.ts) declares `--policy` as additional files/directories, comma-separated or repeated; maps argv into policyPaths. Runner deliberately supports one reviewed regular file and rejects commas to avoid provider splitting.
- Same source says headless policy translates ASK_USER to DENY and excludes the human-question tool. The runner must not launch a paid prompt to discover capability.
- Pinned [policy docs](https://github.com/google-gemini/gemini-cli/blob/v0.65.0/docs/reference/policy-engine.md) warn workspace `.gemini/policies` is nonfunctional/disabled. They describe user/admin/extension precedence and global denied-tool pruning. An explicit CLI file is distinct from implicit workspace discovery; file readability does not establish effective grants.
- Docs contain inconsistent illustrative tier numbers; do not reproduce priority calculations in the runner. Let pinned Gemini enforce policy and surface explicit failures.
- Historical [workarounds](evidence/workarounds-and-issues.md) used a global allow policy and alternative Python I/O. Preserve evidence, but recommend explicit caller-reviewed input and alternatives only within already-authorized paths. Actual permission boundaries remain blockers.
- Historical [blocked report](evidence/live-report.json) and [resumed report](evidence/resume-report.json) show blocked worker/result versus failed iteration, then successful resume. T9 must reproduce and fix new records without rewriting these files.
- Doctor can verify versions, skill files, Git state, explicit TOML syntax/hash and known caveats. Authentication/trust/effective permission remain unknown without an authorized provider outcome. No known local blocker is not ready or authorization.
- No new live-provider proof or paid request was performed for this design. [Optional provider fields](provider-observations.md) have separate pinned source research.
