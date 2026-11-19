# N2. Compare deadline detection and the last native write

Status: in progress
Acceptance: not met

The [scheduling research](../scheduler-research.md) identifies a missing observation. A bounded parent wait can return while native work continues. An interrupt can end the worker turn while a shell descendant continues to write. The runtime implementer owns the reproducible heartbeat probe, focused test and native replay directions. Use the integrated caller sources at abfe9cd5, the authenticated Copilot 1.0.114 setup in the [native replay guide](../../../scripts/tests/orchestration/native-lifecycle.md), and two fresh projects with identical fixture and timings. Test delegate and ExecPlan under the same host first. Include one native Codex interrupt comparison if feasible. Do not change the routing experiment, router policy, or provider configuration.

Dispatch one silent job and one job writing timestamped heartbeats at a fixed short interval. Both must have a real, short assignment deadline. Make the writer outlive its deadline and checkpoint window absent intervention, but give the disposable process its own finite safety limit. Keep raw control and write timestamps outside actor-editable records where practical. Let the parent use its ordinary documented host controls. Retain each assignment deadline, detection time, stop request, independent native interruption or terminal evidence, writer PID/liveness when observable, final write, observation horizon and any transfer. Distinguish steady progress from a timely response with an ETA. Grade deadline latency separately from writes after the stop request or confirmation, and a missing hard-stop capability separately from unsafe reassignment. Verify that the silent case remains covered. A clean provider exit, delivered stop message, or brief quiet interval alone cannot prove shutdown. Preserve all misses and record how to reproduce them. Claude and Gemini remain research references.

## Observed shutdown evidence

The 2026-11-19 UTC trials used independent write timestamps and a separate PID-terminal observer. Each writer remained alive and wrote after the native interruption. The registry applied scoped `SIGTERM`; no work was transferred. The observations demonstrate why a delivered stop or worker-turn completion cannot be treated as writer shutdown.

- **Codex 0.170.0, delegate.** Deadline 05:01:48.359; status check 05:02:07.441; interrupt 05:02:10.526; terminal worker turn 05:02:10.529. PID 69009 wrote sequence 93 at 05:02:34.248081, 24 writes over 23.719 seconds after interruption; PID absent at 05:02:35.273362. Registry applied scoped SIGTERM.
- **Codex 0.170.0, ExecPlan.** Deadline 05:07:43.861; status check 05:08:01.433; interrupt 05:08:07.516; worker reported interrupted at 05:08:07.520. PID 31399 wrote sequence 150 at 05:09:29.047626, 82 writes over 81.528 seconds after interruption; PID absent at 05:09:29.729751. Registry applied scoped SIGTERM.
- **Copilot 1.0.114, delegate replay 5.** Deadline 05:11:52.438; status check 05:12:09.584; checkpoint deadline 05:12:18.236; stop request 05:12:33.723. PID 91346 wrote sequence 180 at 05:14:21.498697, 108 writes over 107.776 seconds after stop; PID absent at 05:14:21.833959. The outer timeout occurred afterward. No transfer occurred.
- **Unsuccessful Copilot setup attempts.** ExecPlan replay 5 could not launch the heartbeat because native command permission was denied. Replay 6 lacked route38 setup. The parent owns Copilot replay 7. These attempts are setup failures, not passing deadline trials.

## Current result and next action

The probe and its focused public CLI tests are ready; the tests pass 3/3. The native guide describes safe probe installation and evidence collection. Shutdown acceptance is not met: all three valid trials show post-stop writes, and Copilot ExecPlan plus any required paired control remain outstanding. The parent owns the last Copilot replay and final integration verdict. Do not start additional native workers from this task.
