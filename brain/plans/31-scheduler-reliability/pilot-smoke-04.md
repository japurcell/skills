# P04 native smoke outcomes

Historical frozen payload `T4-focused-pilot-04/run-01`, source `b0eae21c26605a4edc7d9ee64524658c9f061196`, manifest SHA-256 `84afa64e639923595014fe45092c8debd257ea1519c6818a2c4f5ff0c23d6894`. Neither automated smoke passed. No scored session ran. [Source binding](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-pilot-04/source-binding.json), [manifest](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-pilot-04/run-01/manifest.json) and [slot ledger](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-pilot-04/slot-ledger.json).

## Launch and budget accounting

Three wrapper invocations include one initial prelaunch PATH-order mismatch and two actual phase attempts/native evaluation sessions. The prelaunch failure stopped before attempt/session creation, consumed no model session and is preserved in `launches/*prelaunch-01`. Parent then invoked the exact prepared PATH without altering provider-owned HOME or controls. The ledger preserves this reconciliation. Four old scored slots were not started and are superseded by the new four-scored-session task. Four sessions remain from the eight-session budget after two P03 and two P04 sessions. No additional smoke or retry is authorized. [Prelaunch stderr](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-pilot-04/launches/codex-baseline-smoke-prelaunch-01.stderr), [ledger](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-pilot-04/slot-ledger.json).

## Actual observations

| Provider | Actual native session | Native exit | Provider execution plus evidence seconds | Automated qualification |
| --- | --- | --- | --- | --- |
| codex | `01a1d059-c7e9-7923-a013-479600938e0e` | 0 | 24.073 | Invalid |
| copilot | `1c777571-d765-4581-b452-cc3d6d90f078` | 0 | 12.138 | Invalid |

Both sessions observed `gpt-6.1-sol` with `medium`. Codex executed all three real helper operations and produced the exact smoke output. It prepended Python to the frozen direct-executable helper, so literal helper-prefix matching recognized zero child receipts and invalidated qualification. Copilot attempted Python-prefixed helper commands, including a help/cat compound and register. Narrow executable-helper permission denied the two commands and no helper receipt was produced. [Codex run](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-pilot-04/run-01/cells/codex-baseline/evidence/smoke/run.json), [Codex stdout](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-pilot-04/run-01/cells/codex-baseline/evidence/smoke/stdout.jsonl), [Copilot run](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-pilot-04/run-01/cells/copilot-baseline/evidence/smoke/run.json) and [Copilot stdout](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-pilot-04/run-01/cells/copilot-baseline/evidence/smoke/stdout.jsonl).

Timing values above are provider execution plus evidence collection elapsed. The original ledger records complete wrapper elapsed separately. The frozen receipts retain invalidity even where raw child execution succeeded. No paired score or scheduler efficacy conclusion is established.

## Approved follow-up

The [F2-D contract](ExecPlan.md#f2-d---independent-scored-phases-and-narrow-helper-invocation) removes redundant separate-smoke/prior-phase-success prerequisites, clarifies an extensionless directly executable `invoke-scheduler`, and supports only the known pinned Codex interpreter prefix with exact remaining helper/scheduler argv and real receipts. Copilot retains its narrow executable-only grant. Every fresh scored phase independently proves required inputs, identity, execution, canonical readbacks/state and rubric. [Read-only reproduction](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-four-scenario-fix/readonly-repro.json).

After focused checks, final affected-suite proof, minimal independent review and a verified fresh payload, run only the four remaining scored sessions. Preserve P04 unchanged. No extra smoke/retry, new provider calls during the source fix, or repeat approval question is added.

## Evidence identities

- codex-baseline_run SHA-256 `dc4f5ed5295c7debfccd899897923552f8356a0e343bd942b6c354cb15129736`.
- copilot-baseline_run SHA-256 `44efb625191d9d5d2c047ffc827719f190844c96602a20f8351f869fc00e6619`.
- codex-baseline_stdout SHA-256 `d41732e9816bd324d7e6c08eeffea271ed6c8e9774b03f061de6d9f9a2b474f2`.
- copilot-baseline_stdout SHA-256 `09518abb505a913ce3050ef50b415afdafcdb86942148cad4d469e95bfd4ed08`.
