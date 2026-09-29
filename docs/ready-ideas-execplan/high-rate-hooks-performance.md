# Retained high-rate hook performance on macOS

Milestone 23 source evidence, 2026-09-29. This report covers the integrated M17-22 registration graph at `9ef9e8e5` and the scanner wait change on `codex/ready-hook-performance`. It does not claim installed provider delivery or native Windows timing.

## Complete high-rate inventory

"Per tool or faster" includes hooks that may run during each tool call, model request, tool selection, or streamed model chunk. A clean security pass and telemetry capture still launch their executable. The source scope and matcher below come from the checked-in registrations, not inferred provider activity.

| Provider and source scope | Event and matcher | Entrypoint | Expected call rate |
| --- | --- | --- | --- |
| Copilot user `.copilot/hooks/hooks.json` | `preToolUse`, event-wide | `send-event.py` | Once per pre-tool delivery |
| Copilot user `.copilot/hooks/hooks.json` | `preToolUse`, event-wide | `tool-guard.py` | Once per pre-tool delivery, including allowed no-op |
| Copilot user `.copilot/hooks/hooks.json` | `preToolUse`, event-wide | `scan-secrets.py` | Once per pre-tool delivery, including clean no-op |
| Copilot user `.copilot/hooks/hooks.json` | `postToolUse`, event-wide | `send-event.py` | Once per successful tool completion |
| Copilot user `.copilot/hooks/hooks.json` | `postToolUseFailure`, event-wide | `send-event.py` | Once per failed tool completion |
| Copilot user `.copilot/hooks/rtk-rewrite.json` | `preToolUse` and `PreToolUse`, event-wide variants | `rtk-hook-copilot.py` | Once per delivered pre-tool event, including non-shell no-op |
| Gemini user `.gemini/global-settings.json` | `BeforeTool`, `*` | `send-event.py`, `tool-guard.py`, `scan-secrets.py` | Each executable once per matched tool call |
| Gemini user `.gemini/global-settings.json` | `BeforeTool`, `run_shell_command` | `rtk-hook-gemini.py` | Once per matched shell call, including no rewrite |
| Gemini user `.gemini/global-settings.json` | `AfterTool`, event-wide | `send-event.py` | Once per completed tool call |
| Gemini user `.gemini/global-settings.json` | `BeforeToolSelection`, event-wide | `send-event.py` | Once per tool-selection pass, which may exceed tool calls |
| Gemini user `.gemini/global-settings.json` | `BeforeModel`, event-wide | `send-event.py` | Once per model request |
| Gemini user `.gemini/global-settings.json` | `AfterModel`, event-wide | `send-event.py` | Potentially once per streamed model chunk |
| Codex user template `.codex/global-hooks.json` | `PreToolUse`, `Bash\|apply_patch\|Edit\|Write` | `scan-secrets.py`, `tool-guard.py` | Each executable once per matched tool call |

Repo-local `.github/hooks/hooks.json` and `.codex/hooks.json` add startup, prompt, or turn-end handlers, not per-tool handlers. Codex has no automatic RTK or telemetry hook. Copilot `sessionEnd`, Gemini `SessionEnd`, and Codex `Stop` scanners are retained at lower call rates and are outside this high-rate inventory.

## Reproduction and measurement limits

From the repository root on macOS, run:

    rtk test python3 scripts/benchmark-high-rate-hooks.py --samples 25 --warmups 3 --output /private/tmp/high-rate-hooks.json

The script invokes checked-in Python entrypoints directly with provider-shaped JSON. It creates three synthetic Git repositories and one disposable home per case under the system temporary directory, then removes them. The scanner's finding fixture is an unmistakably fake identifier that matches its pattern. No provider CLI runs, no live tool command executes, and no real home is installed or changed. `HOME`, XDG paths, audit paths, observability logs, guard logs, and secret-scan logs point into the disposable tree. The host's real RTK 0.50.0 runs only its hook processor with fake JSON.

Each case has one first-call "cold" sample with a fresh log home, three discarded warmups, and 25 sequential warm subprocess samples in the same log home. "Cold" does not clear the OS file cache, Python bytecode cache, or Git executable cache. Wall time uses `perf_counter_ns` around the whole subprocess, including Python startup, input/output, RTK and Git children, synchronous logging, and response creation. Warm p95 uses nearest rank; MAD is the median absolute deviation from the warm median. A separate four-process batch shares each handler's log home and is directional concurrency evidence, not a statistically stable p95. The minimal Python JSON subprocess control measures the launch and parse floor. Handler-only time cannot be precisely separated without changing instrumentation or the synchronous log and child-process work being measured; subtraction from this control is only a rough residual.

Host: macOS 26.7 arm64, Python 3.14.6, Apple Git 2.50.1, RTK 0.50.0. The same 25-sample command produced the baseline and post-change runs. The final post-change run also included the additional event-specific telemetry cases. OS scheduling produced occasional high p95 outliers despite low MAD. The benchmark checks that synthetic guard and scanner findings still deny, scanner malformed input reports incomplete, and all expected JSON envelopes parse.

## Results

All times below are milliseconds for whole subprocesses. The scanner table shows before and final after. Each triplet is warm median / p95 / MAD; cold is one first-call sample.

| Scanner case | Before cold | Before warm | After cold | After warm |
| --- | ---: | ---: | ---: | ---: |
| Copilot clean | 212.3 | 225.1 / 236.8 / 5.4 | 109.3 | 110.3 / 111.7 / 0.5 |
| Copilot finding | 222.2 | 223.9 / 234.8 / 4.4 | 110.8 | 111.1 / 112.3 / 0.6 |
| Copilot large file | 253.5 | 263.5 / 270.6 / 4.9 | 144.1 | 145.0 / 147.3 / 0.9 |
| Copilot malformed input | 37.2 | 38.0 / 38.7 / 0.1 | 38.1 | 37.3 / 38.3 / 0.4 |
| Gemini clean | 204.7 | 216.4 / 225.6 / 3.3 | 103.1 | 102.3 / 103.4 / 0.6 |
| Gemini finding | 216.8 | 217.0 / 227.6 / 2.4 | 102.4 | 102.3 / 104.1 / 0.6 |
| Gemini large file | 255.1 | 253.7 / 259.7 / 4.6 | 140.1 | 136.8 / 139.3 / 1.1 |
| Gemini malformed input | 29.3 | 28.9 / 29.4 / 0.1 | 29.1 | 29.1 / 29.4 / 0.1 |
| Codex clean | 212.8 | 216.4 / 225.9 / 3.5 | 103.0 | 103.6 / 107.8 / 1.6 |
| Codex finding | 204.8 | 215.1 / 224.3 / 3.2 | 103.0 | 102.9 / 104.2 / 0.8 |
| Codex large file | 249.1 | 253.2 / 261.9 / 3.2 | 138.9 | 138.0 / 139.8 / 0.8 |
| Codex malformed input | 30.7 | 30.0 / 31.9 / 0.4 | 29.8 | 29.5 / 30.3 / 0.2 |

The final post-change run measured the other handlers and the process control. Each row is cold / warm median / p95 / MAD in milliseconds.

| Case | Cold | Median | p95 | MAD |
| --- | ---: | ---: | ---: | ---: |
| Copilot guard clean / finding / 24 KiB | 35.6 / 37.0 / 78.1 | 34.5 / 35.6 / 77.7 | 35.4 / 36.4 / 78.3 | 0.5 / 0.1 / 0.3 |
| Gemini guard clean / finding / 24 KiB | 27.8 / 28.6 / 113.2 | 26.8 / 28.1 / 113.5 | 27.2 / 28.7 / 116.2 | 0.1 / 0.2 / 0.6 |
| Codex guard clean / finding / 24 KiB | 27.2 / 28.4 / 113.5 | 26.9 / 28.3 / 114.3 | 39.8 / 28.8 / 117.8 | 0.2 / 0.2 / 0.9 |
| Copilot RTK clean / 24 KiB / malformed | 49.7 / 44.2 / 32.0 | 42.4 / 44.9 / 32.0 | 42.8 / 45.7 / 32.4 | 0.3 / 0.5 / 0.1 |
| Gemini RTK clean / 24 KiB / malformed | 44.1 / 46.4 / 24.2 | 43.5 / 45.3 / 24.3 | 44.7 / 46.6 / 24.6 | 0.2 / 0.8 / 0.1 |
| Copilot telemetry pre / success / failure | 36.4 / 36.7 / 35.2 | 35.0 / 34.8 / 35.0 | 35.4 / 35.3 / 35.5 | 0.2 / 0.1 / 0.1 |
| Gemini telemetry selection / before model / chunk | 29.9 / 28.0 / 27.3 | 27.2 / 27.0 / 27.2 | 28.1 / 27.5 / 30.8 | 0.5 / 0.2 / 0.3 |
| Gemini telemetry 24 KiB chunk / before tool / after tool | 40.6 / 28.7 / 26.8 | 28.0 / 27.2 / 27.9 | 28.5 / 28.1 / 28.8 | 0.3 / 0.2 / 0.4 |
| Python JSON process control clean / 24 KiB | 12.7 / 12.3 | 12.2 / 12.1 | 12.5 / 12.3 | 0.2 / 0.1 |

Malformed telemetry input exits 1 before a JSON response, with warm p95 26.1 ms for Copilot and 26.2 ms for Gemini. Guard malformed-input denials had p95 34.2, 26.3, and 25.7 ms for Copilot, Gemini, and Codex. The guard, RTK, and telemetry medians stayed within baseline noise after the scanner change.

One four-process shared-log batch after the change took 241 ms for Copilot scan, 204 ms for Gemini scan, and 235 ms for Codex scan; the pre-change batches took 355, 282, and 283 ms. Other clean-handler batches took 31-103 ms after the change. Concurrency includes process contention and serialized owner-only logging; one batch cannot establish a durable contention budget.

## Bottleneck, change, and budgets

`hooks/families/scan_secrets.py` launched separate Git processes to verify repository context and HEAD, list staged/worktree/untracked paths, and sometimes fetch changed content. Those distinct operations preserve the scanner's fail-closed and completeness checks. `run_git` polled a fast child and then slept as long as 20 ms before checking again. Replacing that sleep with `Popen.wait(timeout=...)` wakes when Git exits while retaining the 20 ms cap for the next output-size/deadline check. No scan, limit, denial, audit, or descendant-process check was removed. The three generated provider scanners received the same canonical change. A clean scan improved by 106-115 ms median, much more than baseline MAD (3-5 ms) or between-run post-change median movement (under 2 ms). Malformed-input failure time did not improve because it does not run Git.

The following local macOS budgets were set after observing the baseline and the configured 8-second scanner deadline, Codex 10-second scanner timeout, Copilot 30-second scanner timeout, and 5-second RTK registration timeout. They are review targets for this host and fixture, not provider-wide guarantees or CI thresholds.

| Workload | Warm p95 target | Observed final p95 |
| --- | ---: | ---: |
| Clean scanner | 180 ms | 103-112 ms |
| 512 KiB scanner candidate | 190 ms | 139-147 ms |
| Malformed scanner input | 60 ms | 29-38 ms |
| Clean Tool Guardian | 50 ms | 27-40 ms |
| 24 KiB Tool Guardian input | 150 ms | 78-118 ms |
| RTK forwarding, including 24 KiB | 70 ms | 43-47 ms |
| Telemetry tool/model/chunk, including 24 KiB | 50 ms | 28-38 ms |

The remaining clean scanner cost is about 100-110 ms whole-process, including a 12 ms minimal Python process floor, multiple bounded Git captures, and synchronous owner-only audit. Reducing the Git query count or log durability would need separate safety evidence. Large Tool Guardian input takes 78-118 ms because bounded structured and text inspection scales with payload size; the configured input limits remain intact. Gemini `AfterModel` telemetry costs about 27 ms per direct chunk invocation, but provider chunk frequency and startup-to-entry are not measured, so aggregate stream cost cannot be estimated here. RTK forwarding includes a child RTK process. No other change beat noise or presented a safe, demonstrated hot-path defect.

The scanner public suites for all three providers, `scripts/generate-hooks.py --check` (26 outputs), and all 25 generator tests passed after the change. The scanner suites cover Git timeout, partial and oversized output, HEAD verification failure, and descendant cleanup separately from this benchmark's malformed-input failure workload. Generator mutation tests needed scoped write access to this worktree's lock file; five initial sandbox errors disappeared under that access. Native Windows behavior, installed provider delivery, live input rates, and provider startup latency remain later milestones.
