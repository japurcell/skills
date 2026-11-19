# Replay a two-worker lifecycle

Use a disposable Git project and a provider account that can start background workers. Keep the parent CLI version and model, caller, workload, clock, worker controls and deadlines fixed within a comparison. Run each arm in a new directory. Record the Git revision, exact argv and elapsed wall time. The raw provider stream can contain private conversation data. Keep it locally and share the worker IDs, public tool actions, times and outcomes.

## Codex CLI

Copy the complete caller and `subagent-model-router` directories from the revision under test into the project's `.agents/skills/`. Include the complete `exec-plans` directory when testing `execplan-implement`. Initialize a fresh Git repository. Give the parent the following local plan, naming the caller under test.

> Start SILENT first and then QUICK as overlapping native background assignments. QUICK waits eight seconds and writes exactly `QUICK` into quick.txt. SILENT waits 150 seconds without routine progress and then writes exactly `SILENT` into silent.txt. Workers can use the host's interruptible wait. Set SILENT's deadline 70 seconds after its start with 35 seconds of checkpoint grace. Record the actual start, deadline, work product and terminal event for each assignment. End after one lifecycle per worker.

Save the task as `BaselinePlan.md`. Save a prompt naming the project-local caller and asking it to execute both assignments as `prompt.txt`. From the project run the authenticated CLI with persistent session recording.

```sh
rtk proxy codex exec --enable multi_agent_v2 --sandbox workspace-write --json - \
  < prompt.txt > ../events.jsonl 2> ../stderr.txt
```

On Codex 0.170.0 find the parent ID in the JSONL `thread.started` event. In its saved session, correlate native `spawn_agent`, `SubAgentActivity`, messages and timer returns with the child IDs and the parent's assignment registry. Verify the actual marker bytes. The stdout event stream alone omitted child starts in a successful positive control. A persistent session allowed the child to attach. Keep `--enable multi_agent_v2` local to the run.

## GitHub Copilot CLI

Copy the complete caller and router into `.github/skills/` in a clean Git project. Create `.github/agents/baseline-quick.agent.md` with `name: baseline-quick`, a description, and instructions to compute 17 + 25 + 31 without tools. Create `baseline-silent.agent.md` with `name: baseline-silent`, a description, `tools: [bash]`, and instructions to run `sleep 145` and then return `SILENT_CASE_DONE`. Use the same available worker model for both profiles and record it. The original profiles specified `model: gpt-6-luna` and `modelPolicy: required`. Supply valid YAML frontmatter between `---` delimiters.

For the matched completion-delivery fixture, run two fresh projects per caller and revision. In both, start SILENT first and launch QUICK concurrently; use 50 seconds of checkpoint grace and ask for one outcome per assignment, records in `coordination.json` and delegate helper state in `scheduler.json`. In the positive control use SILENT's deadline at 120 seconds and QUICK's at 35 seconds. In the inverse arm use SILENT's deadline at 35 seconds and QUICK's at 120 seconds. Confirm the actual registered absolute deadlines and overlapping lifetimes; intended durations alone do not prove ordering. QUICK must finish before SILENT's deadline in the inverse arm. Apply the same two-arm ordering to the Codex plan above, adjusting both deadlines explicitly.

The native runs exposed the frozen CLIs through three narrow PATH commands. `route38` forwards its arguments to the selected revision's `subagent-model-router/scripts/route.py`. `scheduler38` forwards to `delegate-to-subagents/scripts/scheduler.py` and accepts only `--state scheduler.json` resolved in the disposable project. `clock38` prints current Unix time, or that time plus its numeric argument in seconds. The first prompt-mode pilot denied broader compound Python shell invocations. Use the ordinary login and one-session folder trust.

From the disposable project, create the launchers and export their directory for that terminal session. When running the ExecPlan caller, the scheduler launcher is optional.

```sh
rtk proxy python3 - <<'PY'
from pathlib import Path

project = Path.cwd()
bin_dir = project / "bin"
bin_dir.mkdir(exist_ok=True)
for name, script in [
    ("route38", "subagent-model-router/scripts/route.py"),
    ("scheduler38", "delegate-to-subagents/scripts/scheduler.py"),
]:
    target = project / ".github/skills" / script
    if not target.is_file():
        continue
    lines = ["#!/usr/bin/env python3", "import os, sys", "from pathlib import Path"]
    if name == "scheduler38":
        state = str(project / "scheduler.json")
        lines += ["if len(sys.argv) < 3 or sys.argv[1] != '--state' "
                  f"or Path(sys.argv[2]).resolve() != Path({state!r}):",
                  "    sys.exit('Use --state scheduler.json')"]
    lines.append(f"os.execv(sys.executable, [sys.executable, {str(target)!r}, *sys.argv[1:]])")
    tool = bin_dir / name
    tool.write_text("\n".join(lines) + "\n")
    tool.chmod(0o755)
clock = bin_dir / "clock38"
clock.write_text("#!/usr/bin/env python3\nimport sys, time\n"
                 "print(time.time() + (float(sys.argv[1]) if len(sys.argv) == 2 else 0))\n")
clock.chmod(0o755)
PY
export PATH="$PWD/bin:$PATH"
```

```sh
rtk copilot --trust-folder --no-auto-update --disable-builtin-mcps --no-ask-user \
  --model gpt-6-luna --output-format json \
  --allow-tool 'shell(route38:*)' --allow-tool 'shell(scheduler38:*)' \
  --allow-tool 'shell(clock38:*)' --allow-tool 'shell(sleep:*)' \
  --allow-tool "write($PWD/**)" \
  -p 'Carry out both assignments in the local plan using the project caller and router. Read their local SKILL.md files. Use route38 for routing, scheduler38 --state scheduler.json for helper commands, and clock38 for the live clock. Keep writes inside this project.' \
  > ../events.jsonl 2> ../stderr.txt
```

In CLI 1.0.114 track native `task` arguments, `subagent.started`, `subagent.completed`, `system.notification`, the parent's bounded wait, checkpoint and follow-up. The host can deliver an idle notification after the child has already completed. Record both timestamps. Reconcile the durable deadline, helper event when applicable, native parent action, and worker's result. A process exit of zero alone does not establish the lifecycle outcome.

## Compare a wait timeout with writer shutdown

For an active writer, record the registered deadline, the first expiry action, the stop request, the native terminal event, the last heartbeat and an independent process-exit observation. Report these intervals separately. A Codex 0.170.0 child produced 24 more writes after its turn was interrupted. The final write arrived 23.719 seconds after the interruption. The parent retained ownership until it confirmed the writer had exited. Ordinary Copilot delegation exposes a status read and worker messaging. GitHub documents killing a selected worker through the interactive task view. When the parent lacks a stop control or cannot verify descendant shutdown, keep ownership with that worker and record the missing observation. [Codex worker tools](https://github.com/openai/codex/blob/rust-v0.170.0/codex-rs/core/src/tools/handlers/multi_agents_spec.rs) · [Copilot task controls](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/speed-up-task-completion#monitoring-progress)

## Acceptance

There must be two overlapping real workers. Record both registrations and deadlines, QUICK's native completion and parent consumption times, re-arming, SILENT's deadline action and both terminal states. In the inverse arm, prompt delivery is demonstrated only if the parent consumes QUICK before SILENT's earlier deadline and still services SILENT on expiry. Verify QUICK's result and early closure. During quiet time, check for gratuitous status reads, repeated setup or another dispatch. Require a real silent-worker deadline and a bounded response. Permit at most one extension based on a timely ETA. When ownership transfers, verify both the old worker and any write-producing operations have stopped. Report missing observations as unknown. Keep failed attempts, setup failures and successful host/caller combinations separately identifiable. An offline simulation is not native evidence.

## Bounded heartbeat writer for shutdown comparisons

Use `heartbeat_probe.py` for a harmless synthetic writer when a native worker can start project-local commands. Copy the probe into the disposable project, then expose a narrow launcher in the worker profile. It writes one fsynced JSONL record per interval, including sequence number, wall and monotonic timestamps, and its PID. It refuses paths outside the current project, refuses to overwrite an existing file, and stops after at most 240 seconds. Each case must use a fresh project and output path.

For Copilot profiles that receive `--profile <name>` when the command is invoked, the launcher may accept only the exact expected profile argument, either bare or as two tokens, then `exec` the probe. Do not silently discard arbitrary arguments. Keep the silent worker as a separate bounded `sleep` command. Register an absolute deadline from the live clock immediately before each dispatch, then record the checkpoint and native stop actions independently from the worker output.

Observe `heartbeat.jsonl` and the writer PID from outside the disposable actor's editable records. A final heartbeat timestamp, worker completion notification, or parent CLI exit is not process-terminal proof. Record the first independent PID-terminal observation and the later no-new-write horizon. If the CLI cannot dispatch, a wrapper rejects host-added arguments, no writer PID appears, or the observer cannot establish process liveness, classify that attempt as setup failure or missing evidence. Do not call a no-worker wait a passing deadline trial.
