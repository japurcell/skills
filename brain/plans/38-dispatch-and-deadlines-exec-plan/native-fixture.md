# P0. Package the calibrated Copilot gate fixture

Status: done
Acceptance: met

The native-eval implementer owns the opt-in Copilot gate runner, trace grader, focused tests and replay instructions in `scripts/tests/orchestration/`. W1 owns the candidate texts, renderer and controlled actor evidence. Use the restriction proved in [B1](copilot-baseline.md#worker-restriction-control-for-p1). A required-profile-only control accepted the explicitly excluded model; a native project `preToolUse` hook actually denied it. Use the same hook and worker in all arms. The parent will provide a directory of rendered full SKILL.md files for each arm or use W1's renderer.

Build a fresh disposable project per host run from the frozen baseline. Provide its real router using the verified `route38` executable, which forwards to the pinned CLI. The parent must be able to see the worker policy before making the ordinary gate decision. Give it one bounded arithmetic assignment using the required project worker, with unchanged prompts and host settings in matched runs. Keep the policy in a separate file and let it reject excluded native calls. Use scoped tool permissions, normal provider login, separate sessions, exact argv and private raw logs. Keep a compact shareable result, including source fingerprints, actual router output and attempts, before/after coordination records, effective worker model/effort where exposed, and completed work. Redact private messages and unrelated data.

Run a positive and negative grader check using sanitized native event shapes. A known-excluded model attempt fails even if the host blocks it. Require a real dispatch on the permitted route, evidence of the policy being available, unchanged router output and actual worker result. Record missing evidence explicitly and score unavailable observations separately. Stop when a native run can be replayed and graded using a documented command. W1 and this fixture are prerequisites for launching P1's six pairs.

## Result

- (2026-11-18) The opt-in runner, sanitized native grader, 14 focused tests and offline replay command are in `scripts/tests/orchestration/`. The runner uses actor-written `coordination.json`; the grader checks it against route output, task arguments, matching worker output and observed pre/post writes. Native child effort/model remain unavailable when host events do not expose them.
- (2026-11-18) Frozen runner SHA-256: `0c9a3306f454423626df56782c6e5988c3bae78c0fd4fc9b967827239cc6d487`. One initial smoke retained a rejected direct-router invocation. A corrected authenticated smoke passed with zero primary attempts, one allowed fallback worker and result 73. Replay and re-grade instructions: [native-gate.md](../../../scripts/tests/orchestration/native-gate.md).
