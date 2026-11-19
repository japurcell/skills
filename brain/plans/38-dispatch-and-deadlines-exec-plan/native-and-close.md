# Milestone 4. Verify the integrated result on both hosts

Status: in progress
Acceptance: not met

The native operators own each [N1 caller replay](native-replay.md). The integration coordinator owns [I1 verification and reviews](integration.md). [N2](writer-shutdown.md) adds a native heartbeat comparison from the supplied research. Compare the four host/caller pairings against the same observable contract. Each needs early completion, a quiet wait and action at the real remaining deadline. Preserve failed attempts and fixture differences. A verified control for one caller cannot satisfy the other.

## Progress

- [x] [milestone-4] At 5f2892ab, the Codex ExecPlan replay verified early completion, an absolute deadline, a timely checkpoint, one extension and both terminal work products.
- [x] [milestone-4] The first Copilot replays showed a quick worker completing before the parent received the notification and a late checkpoint. See the [R2 assignment](wait-delivery.md).
- [x] [milestone-4] Codex delegate exercised the real nearest deadline, verified early completion and stopped the silent worker in time. Durable shutdown confirmation lagged the decision deadline by 19.5 seconds. See the [N1 trace verdict](native-replay.md).
- [x] [milestone-4] R2 Copilot delegate repeat closed QUICK early and enforced SILENT within grace.
- [x] [milestone-4] R3 matched Copilot ExecPlan repeat detected expiry and checkpointed within grace. The first ExecPlan replay reconstructed its deadlines after completion. [R3](wait-delivery.md#r3-register-an-actionable-deadline-in-execplan) makes registration explicit. The revised Codex caller also passed. See the distinct host latencies in N1.
- [ ] [milestone-4] Integrate the [P1 wording verdict](paired-dispatch.md), run focused suites and independent reviews, and reconcile todo 38 against the accepted scope.
