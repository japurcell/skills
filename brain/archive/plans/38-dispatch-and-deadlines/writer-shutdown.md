# N2. Compare deadline detection and the last native write

Status: done
Acceptance: met for the measurement. Exact deadline shutdown failed in every observed case.

The [scheduling research](../../../plans/scheduler-research.md) identifies a missing observation. A bounded parent wait can return while native work continues. An interrupt can end the worker turn while a shell descendant continues to write. The runtime implementer owns the reproducible heartbeat probe, focused test and native replay directions. Use the integrated caller sources at abfe9cd5, the authenticated Copilot 1.0.114 setup in the [native replay guide](../../../../scripts/tests/orchestration/native-lifecycle.md), and two fresh projects with identical fixture and timings. Test delegate and ExecPlan under the same host first. Include one native Codex interrupt comparison if feasible. Do not change the routing experiment, router policy, or provider configuration.

Dispatch one silent job and one job writing timestamped heartbeats at a fixed short interval. Both must have a real, short assignment deadline. Make the writer outlive its deadline and checkpoint window absent intervention, but give the disposable process its own finite safety limit. Keep raw control and write timestamps outside actor-editable records where practical. Let the parent use its ordinary documented host controls. Retain each assignment deadline, detection time, stop request, independent native interruption or terminal evidence, writer PID/liveness when observable, final write, observation horizon and any transfer. Distinguish steady progress from a timely response with an ETA. Grade deadline latency separately from writes after the stop request or confirmation, and a missing hard-stop capability separately from unsafe reassignment. Verify that the silent case remains covered. A clean provider exit, delivered stop message, or brief quiet interval alone cannot prove shutdown. Preserve all misses and record how to reproduce them. Claude and Gemini remain research references.

## Measured outcomes

All times are UTC on November 19, 2026. Each run launched a silent worker and a separate one-second writer. The deadline and checkpoint columns refer to the writer. The parent sent the status request to its native worker ID. For Codex, count writes after the native interrupted-turn event. For Copilot, count them after the parent's `write_agent` stop request. A separate observer checked the writer PID until it disappeared. None of the four parents transferred ownership.

| Host and caller | Deadline | Status request | Checkpoint deadline | Stop action | Last write | First observed PID absent | Writes after action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Codex 0.170.0, delegate | 05:01:48.359 | 05:02:07.441 | 05:02:08.359 | interrupt 05:02:10.526, confirmed 05:02:10.529 | 05:02:34.248081 | 05:02:35.273362 | 24 over 23.719 s |
| Codex 0.170.0, ExecPlan | 05:07:43.861 | 05:08:01.433 | 05:08:03.861 | interrupt 05:08:07.516, confirmed 05:08:07.520 | 05:09:29.047626 | 05:09:29.729751 | 82 over 81.528 s |
| Copilot 1.0.114, delegate | 05:11:52.438 | 05:12:09.584 | 05:12:18.236 | message 05:12:33.723 | 05:14:21.498697 | 05:14:21.833959 | 108 over 107.776 s |
| Copilot 1.0.114, ExecPlan | 05:21:31.984 | 05:21:51.434 | 05:21:51.984 | message 05:22:10.858 | 05:24:04.240 | 05:24:04.662 | 113 over 113.382 s |

Codex delegate's registry records a subsequent scoped SIGTERM against PID 69009. Codex ExecPlan's PID 31399 reached the finite 150-write bound. The Copilot writers, PIDs 91346 and 99204 respectively, reached 180 writes before the outer observer timed out the parent. The ExecPlan heartbeat worker completed at 05:24:07.339. Its silent partner was separately checkpointed at 05:21:20.583, asked to stop at 05:21:35.521 and reported complete at 05:23:47.067. An outer timeout or successful tool receipt adds no evidence of earlier shutdown.

The N1 [quiet-wait controls](native-replay.md) demonstrated timely action within checkpoint grace on each workflow. This N2 workload found late stop actions in all four cases and a live writer after each one. The comparison supports checking descendants before reassignment. It does not isolate how much the scheduler script changed latency. The delegate helper durably records deadlines and suppresses routine checks. The parent still owns host actions and quiescence evidence.

## Reproduction and retained failures

Use the [native replay guide](../../../../scripts/tests/orchestration/native-lifecycle.md). The probe's three CLI tests pass offline. For Copilot, preflight `route38 --help`, `route38 --work bounded` and `clock38` in the fresh project. Give the heartbeat profile access to its allowed command and the plan reader. The earlier trials recorded alias, scratch-path, profile-argument and permission errors. ExecPlan replay 5 launched its worker but never started a heartbeat. Replay 6 lacked the router executable and never dispatched. Each remains a setup failure with no write-latency verdict.

Private run directories under `/private/tmp/todo38-1795057091956` hold the timestamped writer stream and independent observations. Each pair below fingerprints those two files.

| Run directory | Writer SHA-256 | Observer SHA-256 |
| --- | --- | --- |
| `codex/heartbeat-stop` | `49b322d7d53f7f6efe85f127502995a2be5bbcea5009efd150330ec15e7ccdfd` | `440913e6ff3c1b8a734f653d9907b687392fbb7f88e6d8bf62cdf88306381dc3` |
| `codex/heartbeat-execplan` | `03eea039871f1098603a5ae8fda2d70ded47a1bde1d3d76e1822ecba7048102d` | `1672675c6a9b8fab91478fe3d8ac98bb1ba11852d68b739fbdeb2fde46a0a990` |
| `copilot/heartbeat-n2/replay5/delegate` | `41376ae7eda9d7f45da0f6c4384097ef2e7f88ae352e6d07852ff117817385b3` | `7cc5153bb9580328c23ba3148b76711c5f92eb2b0fc020a3e7680f2e1af6ea9f` |
| `copilot/heartbeat-n2/replay7/execplan` | `4dafca0dfc1b0dcc7635f3cad4a9c5808f857c9e6ec1727194aac339e60e4b22` | `f10e0aa249713fd4e36c65e63d1be9d1f884c901aea0effa1e4e74b032b666ad` |
