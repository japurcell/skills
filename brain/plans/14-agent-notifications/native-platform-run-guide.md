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

These are checkpoints from the 2026-10-29 evidence, not live receiver status. Do not rerun accepted checks by default. Run the relevant remaining checks below only when asked to perform platform testing. This guide update itself does not authorize starting, stopping, or changing an existing receiver. The WSLg receiver was explicitly left open; preserve it until the human authorizes further runtime work.

### Windows: finish mute, input, and desktop coverage

- Use `media`. Already verified: audible automatic success/failure, repeated Preview/Replay, volume adjustment, ordinary focus retention, offline queue/silent restore, and Quit during playback. Earlier button legibility and disabled-state checks also passed.
- First resolve automatic mute using [the controlled mute check](#controlled-mute-check). Previous API counts showed suppression, but the human could not confirm silence. Require an explicit listening answer; do not turn uncertainty into a pass.
- Then perform [keyboard and stack checks](#keyboard-and-stack-checks), [output-device checks](#output-device-checks), and [desktop coverage](#desktop-coverage). Record each result separately. Ordinary focus retention does not establish full-screen or multiple-monitor behavior.
- For a new isolated session, use the Windows commands below. Stop only the receiver associated with that session when finished. Previously accepted audio/lifecycle checks need rerunning only if a failure, source change, or device change affects them.

### WSLg: finish lifecycle before more backend experiments

- Use explicit `media`. Already verified by listening: automatic success/failure, repeated Preview/Replay, sound quality, silent automatic delivery while muted, and audible manual Replay while muted.
- Last saved receiver checkpoint: data `/tmp/agent-alert-wslg-media.ZTWz4x`, PID `1658470`. This may be stale. After runtime testing is authorized, set `data=/tmp/agent-alert-wslg-media.ZTWz4x`, then run `sh run.sh status --data-dir "$data"`. Confirm the backend and pending count before any send. If the directory is missing or the receiver is stopped, report that condition before deciding whether to create a fresh session. Do not assume the saved PID still belongs to this app.
- With the human ready, click Replay, then immediately Quit prototype during playback. Confirm no error and query stopped/paused status. Continue with the shell offline-send/reopen sequence below, keeping `--audio-backend media`; record the pending count before stop and expect exactly one additional offline alert after reopen, with zero playback on the new receiver.
- Inspect this session's runtime log for both shutdown markers, tracebacks, audio errors, PipeWire warnings, and sink timeouts. Record any warnings alongside the human result without claiming they caused a failure.
- Then perform keyboard/stack, focus, output-device, and desktop checks below. WSLg desktop behavior is separate from Ubuntu desktop behavior.
- QSoundEffect A/B remains a diagnostic follow-up, not a prerequisite for accepting successful media playback. Only switch when specifically requested, using the comparison commands below. Leave the working media receiver unchanged otherwise.

### Ubuntu desktop: establish the first real desktop result

- No Ubuntu desktop run has been accepted. WSLg on Arch does not satisfy this platform.
- Record `cat /etc/os-release`, `echo "$XDG_CURRENT_DESKTOP"`, and `echo "$XDG_SESSION_TYPE"`. Record whether this is a physical desktop or a VM and which audio output the human will hear. Do not change the session or install packages to obtain a different result.
- Use a fresh isolated directory and `backend=media` in the shell sequence below. This is an explicit experiment; Linux `auto` still selects QSoundEffect.
- Run the full shell sequence and all human checks: automatic/manual sounds, mute/unmute, keyboard/stack/Undo, focus, offline queue/silent restore, and Quit during playback. Include device and desktop coverage when hardware allows; mark unavailable checks pending.
- Report missing desktop/audio libraries as prerequisites. If another Ubuntu desktop/session is available later, record it as a separate result. Do not claim all Ubuntu, GNOME, KDE, Wayland, or X11 environments passed from one session.

### macOS: retain the audible backend and finish interaction coverage

- Use `backend=soundeffect`. Popup, gentle success/failure previews, and the corrected Quit button already passed on macOS. Do not switch to media merely because Windows uses it.
- Start a fresh isolated session using the shell commands below. Complete keyboard/stack/Undo and controlled mute checks, then output-device and desktop coverage, including Spaces and full-screen. The earlier inactive-window diagnostic does not replace a human focus check while typing in another app.
- Verify silent offline restore if not already recorded as a human-observed macOS result. Automated/offscreen lifecycle results establish process behavior only. Rerun Quit during playback if these checks reveal a shutdown concern; otherwise preserve the existing accepted Quit result.
- Stop the isolated test receiver when finished. Do not reopen the earlier macOS prototype or alter login items.

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

Keep this terminal open so `$data` and `$backend` retain their values. For an authorized existing WSLg session, use its verified data directory and `backend=media`, skip the fresh-session setup and initial sound sends below, and proceed to the remaining WSLg lifecycle check. Otherwise create isolated state outside Git:

```sh
data=$(mktemp -d /tmp/agent-alert-prototype.XXXXXX)
sh run.sh open --data-dir "$data" --audio-backend "$backend"
sh run.sh status --data-dir "$data"
```

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
- Ask the human to click the window intentionally, then Tab and Shift+Tab through enabled controls. Record visible focus, readable labels, reachable controls, and ability to activate buttons with Space/Enter where supported. An automatically shown alert must not prevent intentional keyboard use.
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
- Report OS/distribution/session, source commit (`git rev-parse HEAD`), Python version, backend, receiver PID reuse, each human checklist result, offline/reopen behavior, shutdown markers, and remaining untested checks. Separate human observations from API diagnostics.
- Retain logs outside Git; redact personal paths before sharing excerpts. Do not commit runtime state or environments. Update evidence notes under `brain/plans/14-agent-notifications/` only when authorized.

## Evidence baseline and API references

Earlier macOS QSoundEffect popup/audio and corrected Quit were confirmed by the user. Windows QSoundEffect was inaudible while the same WAV was audible through QMediaPlayer/QAudioOutput and winsound. Integrated Windows media checks are documented in [Windows evidence](windows-native-run-2026-10-29.md). On WSLg, the user confirmed audible automatic success/failure and repeated Preview/Replay, good sound quality, silent automatic delivery when muted, and audible manual Replay while muted. WSLg offline restore, audio-active Quit, and QSoundEffect A/B remain pending; keep the currently running media receiver unchanged until authorized. Ubuntu desktop remains unrun.

See [Windows comparison](windows-native-run-2026-10-29.md), [native evidence](phase-4-native-desktop-prototype.md), [Qt 6.12 QMediaPlayer](https://doc.qt.io/qt-6.12/qmediaplayer.html), and [Qt 6.12 QAudioOutput](https://doc.qt.io/qt-6.12/qaudiooutput.html).
