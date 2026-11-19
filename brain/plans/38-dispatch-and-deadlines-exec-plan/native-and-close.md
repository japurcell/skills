# Milestone 4. Verify the integrated result on both hosts

Status: in progress
Acceptance: not met

The native operators own each [N1 caller replay](native-replay.md). The integration coordinator owns [I1 verification and reviews](integration.md). Compare the four host/caller pairings against the same observable contract. Each needs early completion, a quiet wait and action at the real remaining deadline. Preserve failed attempts and fixture differences. A verified control for one caller cannot satisfy the other.

## Progress

- [x] [milestone-4] At 5f2892ab, the Codex ExecPlan replay verified early completion, an absolute deadline, a timely checkpoint, one extension and both terminal work products.
- [x] [milestone-4] The first Copilot replays showed a quick worker completing before the parent received the notification and a late checkpoint. See the [R2 assignment](wait-delivery.md).
- [x] [milestone-4] Codex delegate exercised the real nearest deadline, verified early completion and stopped the silent worker in time. Durable shutdown confirmation lagged the decision deadline by 19.5 seconds. See the [N1 trace verdict](native-replay.md).
- [ ] [milestone-4] Verify both Copilot callers after R2 and check the combined revision for affected host behavior.
- [ ] [milestone-4] Integrate the [P1 wording verdict](paired-dispatch.md), run focused suites and independent reviews, and reconcile todo 38 against the accepted scope.
