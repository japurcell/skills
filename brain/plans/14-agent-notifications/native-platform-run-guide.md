# Run the native alert prototype

## Scope and acceptance

This guide is for a coding agent operating with a human tester. Run the disposable source kit on one local computer. Do not install real agent hooks, register login startup, install system packages, change PowerShell policy, or request admin access. Do not use real prompts, credentials, or agent logs as test input.

Windows now defaults to QMediaPlayer/QAudioOutput (`media`). macOS and Linux still default to QSoundEffect (`soundeffect`). WSLg must explicitly select `media` for the comparison below. `--audio-backend` affects a new receiver only. Stop the receiver before changing it; an existing receiver keeps its backend. `status` reports the actual `audio_backend`.

The coding agent checks commands, state, logs, and process exit. The human checks visibility, focus, controls, and sound. Ask the human whether each sound was heard. A playback count, Ready status, or successful command does not prove audibility. Mark each unobserved check pending rather than passed.

## Get the source and check prerequisites

Use a separate clone for Windows and Linux. Never share `.venv` or pending-alert stores between operating systems. In an existing clean clone of `https://github.com/japurcell/skills.git`, run:

```sh
git fetch origin
git switch codex/notify-app
git pull --ff-only
```

If the worktree has changes, the branch cannot switch, or the pull cannot fast-forward, stop and report the condition. Do not reset, clean, overwrite, or stash someone else's work. For a new clone, run `git clone --branch codex/notify-app https://github.com/japurcell/skills.git`, then `cd skills`.

Enter `prototypes/agent-notifications` from the repository root. All later commands run in that directory. After every launcher command, check its exit code (`$LASTEXITCODE` in PowerShell, `$?` in shell). Stop on a nonzero exit or JSON `ok: false`; preserve the error before continuing. If a stopped-status check still returns a PID, wait and retry for up to five seconds before reporting shutdown failure.

Confirm `native_alerts.py`, `run.cmd`, `run.sh`, `requirements.txt`, and `sounds/` exist.

Requires existing user-accessible Python 3.10+, a graphical desktop, an audio output, and permission to download pinned binary wheels from PyPI. First launch creates `.venv` locally and installs the pinned PySide6 6.12.0 packages. This is a source kit, not a standalone signed executable. If Python, downloads, virtual environments, or Linux desktop libraries are unavailable, report the missing prerequisite. Do not bypass corporate policy.

## Choose the remaining work for this platform

These are checkpoints from the 2026-10-29 evidence, not live receiver status. Do not rerun accepted checks by default. Run the relevant remaining checks below only when asked to perform platform testing. This guide itself does not authorize starting, stopping, or changing a receiver; follow the user's current request. The authorized WSLg media lifecycle below was completed in an isolated session-files directory and the receiver is now stopped. The previous `/tmp` session remains untouched; do not treat any saved PID as live.

Evidence commits: `4bae34c2` (WSLg lifecycle), `12a58123` (Windows follow-up), and `97c22ecd` (Windows visible-focus and limited Enter check). These runs tested source revision `d1c97146`. The [Windows run note](windows-native-run-2026-10-29.md) retains the per-run observations. The table separates verified behavior, observed limitations, and remaining coverage; it does not establish production readiness.

| Platform / backend | Verified behavior and observed limitations | Remaining checks, in order |
| --- | --- | --- |
| Windows / `media` | Automatic/manual audio, volume, controlled mute/unmute, stack/Snooze/deletion/Undo, visible focus at every enabled control using Tab/Shift+Tab, Space activation, Enter does nothing on Replay sound and Preview success (two controls only), two existing outputs, ordinary/full-screen focus retention, offline restore, clean Quit | Missing-output recovery if safely available; multiple monitors if available. Both are unavailable on the tested host. No routine focus/Enter retest remains; broader Enter behavior needs a separate requirement or test request. |
| WSLg on Arch / explicit `media` | Prior media listening, mute/manual override, offline restore, controlled silent relaunch, Quit, keyboard/stack, and normal-window focus checks remain accepted. The earlier Ctrl+Z sequence was human-reported silent, but the playback counter later increased from 5 to 6; cause and audibility remain unresolved. The separate 2026-10-29 zero-event idle check had a human response of `Unsure`, so it does not establish acoustic silence or pending-alert persistence. In the fresh 2026-10-30 pending-alert idle run, one success remained pending with the same PID and event ID, `audio_play_count=1`, and one play-start marker at actual +119.246s, +120s, and +300s. The human initially reported “Visible with the pending alert” and “Heard once”; later they confirmed listening throughout the five-minute idle and hearing no further sound. The five-minute no-replay acoustic outcome is accepted for this WSLg run only. The planned +30s sample was missed and remains unverified; the later sample is not a substitute. PID `2766170` was stopped cleanly with one pending event preserved. | Output switching/no-device remains a human safe skip (`Cannot safely change outputs now`); only `RDPSink` was available and no device was changed. Desktop fields were blank twice; record unreported/untested without another prompt. No remaining mandatory keyboard test is open. Do not reopen any saved receiver without current authorization. |
| Ubuntu desktop / explicit `media` experiment | No real Ubuntu desktop result yet | Full first-run checklist, including prerequisites, audio, input/stack, mute, lifecycle, devices, and desktop coverage. |
| macOS / `soundeffect` | Visible popup, gentle success/failure previews, corrected Quit | Keyboard/stack/Undo; controlled mute/manual replay; human-observed focus and silent restore; output changes/missing-output; Spaces/full-screen/multiple monitors where available. |

### Windows: remaining coverage after the 2026-10-29 follow-up

- The original PID `37976` `media` follow-up completed the controlled mute/unmute check with direct listening confirmation, keyboard/stack/Undo and Ctrl+Z checks, approved switching between the existing LG and Realtek outputs, focus/full-screen/virtual-desktop observations, and clean shutdown. Detailed additive results are in [the Windows run note](windows-native-run-2026-10-29.md); earlier QSoundEffect and media findings remain intact.
- In the original PID `37976` follow-up, Tab/Shift+Tab navigation was reported to work, all buttons were reachable, and Space activated controls; visible focus and Enter were not itemized in that run.
- A fresh isolated Windows check on PID `9840` completed the keyboard focus and limited Enter observations. The human confirmed visible focus at every enabled control with Tab/Shift+Tab. Enter did nothing on focused `Replay sound` and `Preview success`; Space played `Replay sound`. Record these two per-control outcomes only; do not infer Enter support or lack of support for every button.
- The alert stayed on the original desktop when another virtual desktop was active. One physical display was available, so multi-monitor behavior is untested. No output device was removed or disabled, so missing-output handling is also untested.
- Review outcome: visible focus passed at every enabled control. Enter was observed to do nothing on two non-destructive controls; this is a recorded behavior, not a pass for Enter activation and not evidence about other buttons. No universal Enter requirement was agreed, so this documentation review authorizes no keyboard-source change. Use Space for the verified button activation path.
- The fresh-session open/status, visible-focus, and limited Enter checks are complete. Do not rerun them by default. Existing LG/Realtek output switching and single-display full-screen/focus checks need no routine repeat.
- Remaining Windows coverage is conditional: use [output-device checks](#output-device-checks) for missing-output recovery only if safely available, and [desktop coverage](#desktop-coverage) for multiple monitors only if equipment is available. Both cases were unavailable on the tested host. If that remains true, report them as unavailable and finish without opening a new receiver. Do not repeat accepted tests, disable devices, or change drivers to manufacture coverage.
- If a future request specifically asks for broader Enter coverage, test each named control in a fresh synthetic session and record its actual behavior separately. Do not infer results for Dismiss, Dismiss all, Undo, or Quit from the two audio controls, or activate destructive controls in preserved queues.
- Record the virtual-desktop observation as a limitation: the popup remained on its original desktop. Do not describe this as following the user across desktops.
- The original PID `37976` follow-up ended stopped/paused with six synthetic alerts in its isolated temporary directory. Preserve that data. The separate PID `9840` focus/Enter follow-up ended stopped/paused with one synthetic alert and its own isolated log. No production default or delivery guarantee is established by these checks.

### WSLg on Arch: current state and remaining checks

- Use explicit `media`; do not switch backend or run the optional QSoundEffect comparison in this continuation. Earlier WSLg media listening/mute acceptance and the separate lifecycle run remain accepted; detailed history is in the ExecPlan. The first attempt's six playback completions and the later missing-directory cause remain unexplained, with no audibility or root cause inferred.
- The human-authorized Quit ended old PID `2224490`; one post-Quit read found its old session-state directory still empty. No old queue or log was recovered or copied.
- Interaction state is preserved at `/home/adam/.local/state/agent-alert-prototype/wslg-acceptance-20261029-2126-p2224490/`, outside Git. PID `2258035` was identity-checked (prototype command, exact directory, explicit `media`, Qt `wayland`, repository cwd), then stopped through the public CLI. Within about one second status was `running=false,paused=true,pending=1`, `/proc/2258035` was absent, and `pending.json` retained success/Codex/demo `Ctrl+Z check` (ID `52799709-dd70-49c0-9dd6-4fe4bba50ef2`, `muted=false`, volume `0.25`). The human accepted Tab/Shift+Tab, staged Snooze/Dismiss/Undo, normal-window other-app focus, silent Space/Snooze, empty-state Undo expiry with inert disabled controls, and Dismiss/Ctrl+Z restoration.
- Status before shutdown showed `audio_play_count=6`. It was 5 immediately after sending the event; the runtime log later recorded another success playback start. Human reports the Dismiss/Ctrl+Z action itself was silent. Cause/timing and audibility of the extra playback remain unresolved; do not attribute it to Undo or infer audibility from the counter.
- A separate fresh zero-event idle session was authorized by an explicit human `Yes` at `/home/adam/.local/state/agent-alert-prototype/wslg-idle-20261029-2200/`, PID `2341179`, with no copied state or sent alerts. From 22:01:48 to 22:06:49 (301 seconds), status at ~30 seconds, 2 minutes, and 5 minutes remained `pending=0`, `audio_play_count=0`, same PID, and sources Ready; its 1,567-byte `runtime.log` had no playback entries. Default output was `RDPSink` (suspended), system mute off at 100%, app unmuted at volume `0.25`. Human idle-sound response was `Unsure`; acoustic silence is unverified, and this run does not establish pending-alert persistence.
- The explicitly authorized cleanup of PID `2341179` returned `running=false,paused=true,pending=0` within about one second; `/proc/2341179` was absent and `pending.json` still has an empty event list. The 2026-10-29 interaction and idle runtime logs contain `event-loop-stopped` and `objects-destroyed` (interaction lines 54/56; idle lines 19/20), with no `Traceback` or `Exception`. Both state and log files are preserved; their `instance.lock` files were removed on clean shutdown. Do not reopen those saved runs unless specifically requested.
- Output switching/no-device remains an untested safe skip because the human cannot safely change outputs; only `RDPSink` was enumerated and no device was switched or disabled. OS mute is not a no-device test. Desktop checks were unreported twice; record untested without prompting again.
- The guide's evidence fields include OS/distribution/session, source commit, Python version, backend, receiver PID reuse, each human result, offline/reopen behavior, and shutdown markers. For this host, baseline was Arch Linux, WSL2 kernel `6.18.54.1-microsoft-standard-WSL2`, Python `3.13.0`, repo HEAD `c67c2c98d08d5afacc1f80bb547ec142bd5ce169`, `WAYLAND_DISPLAY=wayland-0`, and `PULSE_SERVER=unix:/mnt/wslg/PulseServer`; `XDG_CURRENT_DESKTOP` and `XDG_SESSION_TYPE` were unset in the coordinator shell, while receiver status reported Qt `wayland`. The normal-window focus check is human-accepted; do not infer it from `window_active`. The separate 2026-10-29 zero-event run remains acoustically inconclusive (`Unsure`). In the 2026-10-30 pending-alert run, machine samples at actual +119.246s, +120s, and +300s showed the same event pending and playback count at one, with only the initial play-start marker. The human later confirmed listening throughout the five-minute idle and hearing no further sound. This meets the five-minute no-replay outcome for this WSLg run only. The planned +30s sample remains unverified; the run guide requires retaining that gap but does not define a missed intermediate checkpoint as failure of the five-minute outcome. The three-point sampling procedure is incomplete. Broader WSLg coverage remains open because output/device was safely skipped and desktop checks are unreported.

- Fresh pending-alert idle follow-up (2026-10-30): on Arch Linux under WSL2 kernel `6.18.54.1-microsoft-standard-WSL2`, Python `3.13.0`, repository HEAD `c67c2c98d08d5afacc1f80bb547ec142bd5ce169`, prototype source revision `d1c97146e70ba5f76179dd807ec9486655e9b6d3`, `DISPLAY=:0`, `WAYLAND_DISPLAY=wayland-0`, and `PULSE_SERVER=unix:/mnt/wslg/PulseServer`, PID `2766170` used explicit `media` and fresh data at `~/.copilot/session-state/a9b05811-ea45-4f7e-829c-3980db499290/files/wslg-pending-idle-20261030/`. Baseline was `pending=0`, `audio_play_count=0`, all sources `Ready`, `output_available=true`, `muted=false`, and volume `0.25`; Qt logged PipeWire symbol-resolution warnings and FFmpeg 9.0.1 fallback. Exactly one success event (ID `62c54efd-f65c-47c8-bcc3-b4e017a94c6a`) was sent at wall epoch `1793375553.3609695`. At `2026-10-30T08:56:09.860-07:00`, the human reported “Visible with the pending alert” and “Heard once” for the initial success. Actual samples at +119.246s, +120.000s, and +300.000s each showed that same event pending once, the same live PID, `audio_play_count=1`, and one play-start marker. The planned +30s sample was missed and remains unverified; no later sample is labeled as that checkpoint. The full log had no further play-start marker. In a retrospective `ask_user` at `2026-10-30T09:19:05.232-07:00`, the human confirmed listening throughout the five-minute idle and responded exactly “I listened throughout and heard no further sound.” The five-minute no-replay acoustic outcome is accepted for this WSLg run only; the missed +30s sample remains missing intermediate machine evidence, and the planned three-point sampling procedure is incomplete. The exact question and answer are retained at `~/.copilot/session-state/a9b05811-ea45-4f7e-829c-3980db499290/files/wslg-pending-idle-20261030-human-observation-followup.txt`. The public `stop` command followed an exact command-line/data-path/backend identity check. Final status was `running=false,paused=true,pending=1`; `/proc/2766170` was absent; `pending.json` preserved the event; the log contains both shutdown markers and no traceback/exception. Evidence files are in the session `files/` directory with prefix `wslg-pending-idle-20261030-`, alongside the isolated data directory. This is WSLg evidence only, not native Ubuntu acceptance.

#### Historical WSLg run records (superseded by current state above)

- Detailed lifecycle, retry, and storage-anomaly evidence is retained in [the ExecPlan](native-prototype-exec-plan.md). Those process IDs and states are historical, not live. The old session-files directory and original `/tmp` state remain untouched; do not copy old state into the current persistent run.

### Ubuntu desktop: establish the first real desktop result

- No Ubuntu desktop run has been accepted. WSLg on Arch does not satisfy this platform.
- Record `cat /etc/os-release`, `echo "$XDG_CURRENT_DESKTOP"`, and `echo "$XDG_SESSION_TYPE"`. Record whether this is a physical desktop or a VM and which audio output the human will hear. Do not change the session or install packages to obtain a different result.
- Use a fresh isolated directory and `backend=media` in the shell sequence below. This is an explicit experiment; Linux `auto` still selects QSoundEffect.
- Run the full shell sequence and [full human checklist](#full-human-checklist-for-a-first-run), including the detailed controlled mute, keyboard/stack, output-device, and desktop recipes below. Confirm automatic/manual sounds, mute/unmute, focus, offline queue/silent restore, and Quit during playback. Include hardware-dependent cases only when available; mark unavailable checks pending. Finish stopped, inspect the isolated log, and report the exact Ubuntu release/desktop/session tested.
- Report missing desktop/audio libraries as prerequisites. If another Ubuntu desktop/session is available later, record it as a separate result. Do not claim all Ubuntu, GNOME, KDE, Wayland, or X11 environments passed from one session.

### macOS: retain the audible backend and finish interaction coverage

- Use `backend=soundeffect`. Popup, gentle success/failure previews, and the corrected Quit button already passed on macOS. Do not switch to media merely because Windows uses it.
- Start a fresh isolated session using the shell commands below. Complete [keyboard and stack checks](#keyboard-and-stack-checks) and [controlled mute check](#controlled-mute-check), including audible manual Replay while muted and no catch-up audio after unmuting. Then complete [output-device checks](#output-device-checks) and [desktop coverage](#desktop-coverage), including Spaces and full-screen. The earlier inactive-window diagnostic does not replace a human focus check while typing in another app.
- Verify silent offline restore if not already recorded as a human-observed macOS result. Automated/offscreen lifecycle results establish process behavior only. Rerun Quit during playback if these checks reveal a shutdown concern; otherwise preserve the existing accepted Quit result.
- Stop the isolated test receiver when finished. Do not reopen the earlier macOS prototype or alter login items. If native computer-use permission is unavailable, have the human operate the controls and report observations; do not treat internal Qt state as keyboard, focus, or Spaces proof.

## Windows: PowerShell

Use Windows PowerShell or PowerShell in Windows Terminal. Check Python with `py -3 --version`. Keep this terminal open so `$data` retains its value. Create a fresh isolated directory outside Git:

```powershell
$data = Join-Path $env:TEMP ('agent-alert-prototype-windows-' + (Get-Date -Format yyyyMMdd-HHmmss))
& .\run.cmd open --data-dir $data
& .\run.cmd status --data-dir $data
```

Expect JSON with `ok: true`, `audio_backend: "media"`, `window_visible: true`, and a PID. Audio sources may briefly load; repeat status after two seconds and record the result. Ask the human whether the window appeared. Opening an empty stack should be silent.

Send two alerts, waiting at least two seconds between commands so these test separate sounds rather than burst coalescing:

```powershell
& .\run.cmd send success --agent Codex --repo demo --summary 'Windows success audio check' --data-dir $data
& .\run.cmd send failure --agent Copilot --repo demo --summary 'Windows failure audio check' --data-dir $data
& .\run.cmd status --data-dir $data
```

For this fresh two-alert sequence, expect two pending alerts and the same PID. Use only the remaining human checks identified in the Windows section; the full checklist is for a first run or a justified repeat. Record the pending count before any lifecycle check. The Windows lifecycle sequence is:

```powershell
& .\run.cmd stop --data-dir $data
Start-Sleep -Seconds 1
& .\run.cmd status --data-dir $data
& .\run.cmd send approval --agent Gemini --repo demo --summary 'Queued while stopped' --data-dir $data
& .\run.cmd open --data-dir $data
& .\run.cmd status --data-dir $data
```

After stop, expect `running: false`, `paused: true`. Offline send must return `queued: true`, `running: false`, with no popup or sound. Open must restore the pending alerts silently with a new PID and `audio_backend: "media"`.

Finish with `& .\run.cmd stop --data-dir $data`, wait one second, then run `& .\run.cmd status --data-dir $data`. Inspect `Get-Content (Join-Path $data 'runtime.log') -Tail 40`. Expect `event-loop-stopped` and `objects-destroyed`, no traceback/crash, and stopped status. Keep this directory for evidence; do not commit it.

## Shell commands for Ubuntu desktop, macOS, and WSLg

Check `python3 --version`. On Ubuntu, record release, desktop (GNOME/KDE), and session (`echo "$XDG_SESSION_TYPE"`). On WSL2, record distribution, `uname -r`, `echo "$WAYLAND_DISPLAY"`, and `echo "$PULSE_SERVER"`. WSLg GUI/audio must already work; headless WSL2 cannot display a popup itself. The earlier WSLg run used Arch Linux, so it does not establish Ubuntu desktop support.

For Ubuntu desktop or WSLg, select:

```sh
backend=media
```

For macOS, select instead:

```sh
backend=soundeffect
```

Keep this terminal open so `$data` and `$backend` retain their values. The accepted WSLg lifecycle receiver under `wslg-lifecycle-20261029/` remains stopped with two synthetic alerts pending; do not reopen it. The original `/tmp` session remains untouched. The interaction state at `/home/adam/.local/state/agent-alert-prototype/wslg-acceptance-20261029-2126-p2224490/` is stopped with one preserved `Ctrl+Z check` event; the idle state at `/home/adam/.local/state/agent-alert-prototype/wslg-idle-20261029-2200/` is stopped and empty. Do not reopen either or send more events unless specifically authorized. Check that a data directory already exists before invoking status, since status may create a missing directory. Any future WSLg run requires current authorization and a separate isolated directory. If the execution environment prohibits `/tmp` file operations, do not run `mktemp`; use a session-files directory only when the user's request authorizes that location. Otherwise create isolated state outside Git:

```sh
data=$(mktemp -d /tmp/agent-alert-prototype.XXXXXX)
sh run.sh open --data-dir "$data" --audio-backend "$backend"
sh run.sh status --data-dir "$data"
```

If the execution environment prohibits `/tmp` file operations, do not run `mktemp`. Use a unique session-provided `files/` directory outside the repository only when the user's current request authorizes that state location. Pass its absolute path as `data`; the launcher changes to its own directory, so a relative path would resolve under the source kit. This guide alone does not authorize reopening existing state.

Expect `audio_backend` to match `$backend`, a PID, and a visible window. macOS should report `soundeffect`; Ubuntu/WSLg media experiments should report `media`. Repeat status after two seconds if sources are loading. Opening an empty stack should be silent.

Send alerts at least two seconds apart:

```sh
sh run.sh send success --agent Codex --repo demo --summary 'Platform success audio check' --data-dir "$data"
sh run.sh send failure --agent Gemini --repo demo --summary 'Platform failure audio check' --data-dir "$data"
sh run.sh status --data-dir "$data"
```

For this fresh two-alert sequence, expect two pending alerts and the same PID. Complete only the remaining checks listed for your platform; Ubuntu requires the full human checklist. Record the pending count before stopping. The shell lifecycle sequence is:

```sh
sh run.sh stop --data-dir "$data"
sleep 1
sh run.sh status --data-dir "$data"
sh run.sh send approval --agent Copilot --repo demo --summary 'Queued while stopped' --data-dir "$data"
sh run.sh open --data-dir "$data" --audio-backend "$backend"
sh run.sh status --data-dir "$data"
```

After stop, expect `running: false`, `paused: true`. Offline send must queue silently without starting a receiver. Open must restore pending alerts silently with a new PID and `audio_backend` matching `$backend`.

Only when a WSLg QSoundEffect comparison is specifically requested, stop first, wait one second, then reopen the same pending stack using the old path:

```sh
sh run.sh stop --data-dir "$data"
sleep 1
sh run.sh open --data-dir "$data" --audio-backend soundeffect
sh run.sh status --data-dir "$data"
```

Expect `audio_backend: "soundeffect"`. Repeat the listening checklist with identical system volume and output device. Record each backend separately. Do not claim a backend fixed WSLg without human listening confirmation.

Finish with `sh run.sh stop --data-dir "$data"`, wait one second, then run `sh run.sh status --data-dir "$data"`. Inspect `tail -n 40 "$data/runtime.log"`; expect both shutdown markers and no traceback/crash. Keep state/logs outside Git for diagnosis. A compositor may ignore placement/topmost requests; record the visible result instead of assuming support.

## Full human checklist for a first run

1. With another app focused, send a new alert. Does the popup appear while the other app keeps focus? Record monitor/full-screen behavior. Can the human intentionally click and Tab through controls?
2. Hear automatic success and failure sounds separately. Are they gentle and distinct? Click Preview success, Preview failure, and Preview attention twice each, allowing two seconds between clicks. Can the human hear every attempt?
3. With an alert present, click Replay sound twice, two seconds apart. It should replay each time. Change Sound level and compare the audible level.
4. Check Mute automatic sounds, then send a new alert. The alert must appear silently. Manual Preview and Replay must still work. Uncheck mute, send another alert, and confirm sound returns without replaying older alerts.
5. With multiple alerts, Snooze must move the front alert to the back without sound. Dismiss must delete one; Undo within ten seconds must restore it. Dismiss all must clear the stack; Undo must restore the batch. Nothing should automatically dismiss.
6. Click Quit prototype during playback. Confirm no Python error. Query status in the terminal: expect stopped/paused. Reopen with the same explicit backend; pending alerts must return silently. Finish by stopping the receiver.

Only perform output-device removal/switching if the human can safely do so. Record whether the app reports an unavailable output and whether sound resumes after restoring it. Otherwise mark this check pending. No abrupt beep fallback is allowed.

## Controlled mute check

Use the same isolated `$data` for every command. Ask the human to keep the output device, system volume, and Sound level fixed throughout this check. Do not use OS mute; that would hide whether the app suppresses automatic playback.

1. Uncheck Mute automatic sounds. Send `success` using the platform command below. Wait at least two seconds. Ask whether the human heard it. If not, stop the mute comparison and report a general audio failure.
2. Record `status` and its `audio_play_count`. Check Mute automatic sounds. Send `failure`. Wait two seconds, then record status again. The pending count must increase by one and playback count must remain unchanged. Ask explicitly: “Did the new alert appear, and was it silent?” Silence is accepted only with human confirmation.
3. Keep mute checked. Click Replay and a Preview button, two seconds apart. Ask whether both were heard. These manual actions should remain audible; their playback-count increases do not mean automatic mute failed.
4. Uncheck mute. Send a fresh `success`, wait two seconds, and confirm it is audible. Previously muted events must not replay automatically. Record pass, fail, or inconclusive for each part.

Windows send/status commands (substitute `failure` for the muted step; read status once before sending to establish the baseline):

```powershell
& .\run.cmd send success --agent Test --repo demo --summary 'Controlled mute check' --data-dir $data
& .\run.cmd status --data-dir $data
```

Shell send/status commands (substitute `failure` for the muted step; read status once before sending to establish the baseline):

```sh
sh run.sh send success --agent Test --repo demo --summary 'Controlled mute check' --data-dir "$data"
sh run.sh status --data-dir "$data"
```

## Keyboard and stack checks

Use only disposable test alerts. If the current queue contains real or unidentified alerts, preserve it and create a separate isolated session before these deletion checks.

- Send three distinguishable alerts using the platform send command: `success`, `failure`, and `approval`, with summaries `Stack A`, `Stack B`, and `Stack C`. Wait two seconds between sends. Record their front-to-back order. Leave the stack untouched for at least 30 seconds; none may automatically disappear.
- Capture and report the visible front alert, next alert, count, and expected order before keyboard navigation or action. Have the human click the window intentionally, then Tab and Shift+Tab through enabled controls without pressing Space/Enter. Record visible focus, readable labels, and reachability. Pause before any action key or mouse click so the initial stack remains observable.
- Test keyboard activation separately and one action at a time. Tab/Shift+Tab focus acceptance does not establish keyboard activation. If the parent authorizes this later, press Space once while Snooze is focused; expect the front alert to move to the back without sound and no playback-count increase. Check status and visible front/next labels, then pause for human confirmation before continuing. Do not combine this with the current background-focus check.
- Snooze the front alert: it must move to the back without sound. Continue until the original order returns. Dismiss one alert; Undo within ten seconds must restore it. Dismiss all; Undo must restore the entire batch in order. No separate history window should appear.
- Dismiss all again and wait more than ten seconds. Undo must expire. With the stack empty, action labels must remain legible, disabled actions must look disabled, and clicks must do nothing. Send another alert and verify controls become usable again.
- Send one new test alert, dismiss it, and test the prototype's Ctrl+Z Undo shortcut within ten seconds. Record the actual result, including on macOS; do not assume Command+Z is implemented. Never delete real alerts to perform these checks.

## Output-device checks

- Only proceed with a human-approved device change using existing OS controls. Record the initial output name, then switch to another available output. Play Preview and send a fresh event; ask which device produced sound and whether both attempts were audible. Restore the original output and repeat. Record any need to restart the prototype as a limitation.
- If the human can safely leave the system with no available output, do so and attempt Preview and a fresh send. Expect a visible unavailable-output message without a crash or abrupt beep. Restore output and verify audio recovery. OS mute alone does not simulate a missing device.
- If there is no second output or no safe way to remove all outputs, mark those checks pending with the reason. Do not change drivers, install packages, or disable hardware to force coverage.

## Desktop coverage

- Have the human type in another app while the coding agent sends an alert using the platform command. The popup should appear without taking typing focus. Record visual observation separately from `window_active` diagnostics.
- On available monitors, repeat while the other app is on each monitor. Ask whether the popup remains visible, readable, movable, and fully on screen. Record scaling/resolution and any clipped controls. One monitor cannot establish multiple-monitor support.
- Repeat with the other app full-screen. On macOS, also switch Spaces and test an existing full-screen Space. Record whether the alert appears in the current Space or remains elsewhere. On Windows/Linux, record virtual-desktop behavior if tested.
- Wayland or OS full-screen policy may prevent topmost/global placement. Record that limitation; do not alter compositor policy or infer success from a topmost flag. If hardware or permissions prevent a scenario, leave it pending.

## WSLg idle observation

Run this diagnostic only when requested, after the human agrees to an idle listening interval. It addresses the earlier increase from zero to four playback starts after 266 seconds; its cause and audibility are still unknown.

1. Create a fresh isolated shell session with `backend=media`. Use open/status only; do not send alerts or copy old pending state. Confirm `pending=0`, `audio_play_count=0`, and record the PID, timestamp, output device, mute setting, and Sound level. Leave automatic mute unchecked so it does not conceal unexpected playback.
2. For five minutes, do not click Preview/Replay, send events, or let another test use this data directory. Ask the human to note any sound and its time. Record status after approximately 30 seconds, two minutes, and five minutes, checking the same PID and pending count each time. The expected playback count remains zero. Keep the agent responsive during the interval rather than using one long blocking wait.
3. If a count changes, preserve the before/after timestamps and the full isolated runtime log. Record whether the human heard anything and whether pending count or PID changed. Do not label it audible replay unless listening supports that conclusion, or infer a cause from a playback counter alone.
4. Stop a diagnostic receiver with its exact data directory only when its cleanup is authorized; confirm stopped/paused status and shutdown markers, and leave prior test directories untouched. The completed 2026-10-29 idle run (PID `2341179`) and interaction run (PID `2258035`) were stopped under explicit authorization; both PIDs are absent and both logs contain shutdown markers. A clean five-minute observation is evidence for that interval only; it does not explain the earlier anomaly or establish pending-alert persistence. Do not edit source or change backends as part of collecting this evidence.

## WSLg pending-alert idle observation

This is separate from the zero-event diagnostic above and only applies after a specific request authorizes a fresh isolated run. The guide itself does not authorize reopening a saved receiver or sending an alert.

1. Open a fresh session with explicit `media`. Record baseline PID, backend/platform, source readiness, pending count, playback count, mute/volume, and output availability.
2. Send exactly one approved synthetic event. Record wall and monotonic command bounds, the persisted event ID/time, and the post-send state after the expected initial playback has settled. Ask separately whether the initial alert was visible and whether its sound was heard.
3. Keep the event unacknowledged for five minutes. Do not click, preview, replay, or send more events. Start a bounded sampler immediately after injection and record actual monotonic offsets for the planned +30s, +120s, and +300s status checks. At each point, verify the same PID and event ID, `pending=1`, and no playback-count increase beyond the initial event; inspect the full runtime log for extra play-start markers.
4. Record human sound reports with their time scope. Hearing the initial event once does not establish acoustic silence during idle. If a scheduled point is missed, mark that point unverified and record the actual time of the first later sample. Do not relabel a later sample or resend/repeat solely to fill a missed point without fresh authorization.
5. Before stopping, identity-check the receiver command line, exact data directory, and backend. Use the supported `sh run.sh stop --data-dir <exact-path>` command, then verify stopped/paused status, process absence, shutdown markers, and preserved pending state.

The 2026-10-30 Arch/WSLg run used PID `2766170` and one success event. Samples at actual +119.246s, +120.000s, and +300.000s all showed the same event pending once, playback count 1, and one play-start marker. The planned +30s point was missed and remains unverified. The initial human report was “Visible with the pending alert” and “Heard once.” In a retrospective report after the receiver was closed, the human confirmed listening throughout the five-minute idle and hearing no further sound. The five-minute no-replay outcome is accepted for this WSLg run only; the +30s gap remains missing intermediate evidence, not a relabeled sample. The receiver stopped cleanly with one pending event preserved. Evidence is under `~/.copilot/session-state/a9b05811-ea45-4f7e-829c-3980db499290/files/wslg-pending-idle-20261030/` and adjacent session files named `wslg-pending-idle-20261030-*`, including `wslg-pending-idle-20261030-human-observation-followup.txt`. This is WSLg evidence, not native Ubuntu acceptance.

## WSL2 to a Windows-host popup: separate optional path

This route uses Windows Python and Windows IPC. It is separate from the Linux WSLg comparison. Clone to a Windows user folder, run the Windows prerequisite checks, and choose an isolated Windows data directory. From WSL, replace both example paths with actual Windows paths:

```sh
powershell.exe -NoProfile -Command "& 'C:\Users\YOUR_NAME\skills\prototypes\agent-notifications\run.cmd' send success --agent Codex --repo demo --summary 'Local WSL2 event' --data-dir 'C:\Users\YOUR_NAME\AppData\Local\Temp\agent-alert-wsl-host' --audio-backend media"
```

Use the same launcher and `--data-dir` for subsequent Windows `status` and `stop`. Expect `audio_backend: "media"`. Ask the human about popup/audio, then stop the Windows receiver. Do not pass a Linux data directory or share state with the WSLg receiver. This requires existing Windows interoperability; it changes no execution policy and is not remote delivery.

## Failure diagnosis and evidence to return

- Wrong backend: stop the receiver with the same data directory, wait for stopped status, reopen with the explicit selection. A flag on `send` or `status` cannot replace a running backend.
- No Python, missing wheel/shared library, or blocked downloads: preserve the exact error and report an environment prerequisite. Do not install system packages.
- Receiver timeout or crash: inspect `<data-dir>/runtime.log`, record the command and exit status, and keep the data directory. Do not kill unrelated Python processes.
- Silent audio with Ready/playback diagnostics: record it as a failure. Capture backend, output device, system/app volume, which automatic/manual attempts were heard, and relevant log errors. Do not increase WAV gain or change drivers to hide the failure.
- Report OS/distribution/session, source commit (`git rev-parse HEAD`), Python version, backend, receiver PID reuse, each human checklist result, offline/reopen behavior, shutdown markers, and remaining untested checks. For every requested check use pass, fail, inconclusive, or unavailable with a reason. Preserve previously accepted evidence without presenting it as a new run. Separate human observations from API diagnostics.
- Retain logs outside Git; redact personal paths before sharing excerpts. Do not commit runtime state or environments. Update evidence notes under `brain/plans/14-agent-notifications/` only when authorized.

## Evidence baseline and API references (historical; live state is above)

Earlier macOS QSoundEffect popup/audio and corrected Quit were user-confirmed. Windows QSoundEffect was inaudible on the tested host; later Windows media listening, visible-focus, limited Enter, stack/Undo, output-switching, and desktop evidence is in [the Windows run note](windows-native-run-2026-10-29.md). Windows missing-output and multiple-monitor checks remain conditional.

WSLg media listening and the isolated lifecycle remain accepted. Historical retry and storage-anomaly details, including the unexplained six-play observation and the empty old session directory, are retained in the ExecPlan. The two WSLg receivers stopped on 2026-10-29 remain historical; the separate 2026-10-30 pending-alert run and its stopped state are recorded in the current WSLg section above. The original `/tmp` session remains untouched.

See [Windows comparison](windows-native-run-2026-10-29.md), [native evidence](phase-4-native-desktop-prototype.md), [Qt 6.12 QMediaPlayer](https://doc.qt.io/qt-6.12/qmediaplayer.html), and [Qt 6.12 QAudioOutput](https://doc.qt.io/qt-6.12/qaudiooutput.html).
