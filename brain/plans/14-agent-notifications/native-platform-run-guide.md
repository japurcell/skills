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

Expect two pending alerts and the same PID. Perform the human checklist below, then perform the Windows lifecycle sequence:

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

## Ubuntu desktop, macOS, or WSLg: shell

Check `python3 --version`. On Ubuntu, record release, desktop (GNOME/KDE), and session (`echo "$XDG_SESSION_TYPE"`). On WSL2, record distribution, `uname -r`, `echo "$WAYLAND_DISPLAY"`, and `echo "$PULSE_SERVER"`. WSLg GUI/audio must already work; headless WSL2 cannot display a popup itself. The earlier WSLg run used Arch Linux, so it does not establish Ubuntu desktop support.

Keep this terminal open so `$data` retains its value. Create isolated state outside Git:

```sh
data=$(mktemp -d /tmp/agent-alert-prototype.XXXXXX)
sh run.sh open --data-dir "$data" --audio-backend media
sh run.sh status --data-dir "$data"
```

This explicitly tests the new media path, including on WSLg. Expect `audio_backend: "media"`, a PID, and a visible window. Repeat status after two seconds if sources are loading. Opening an empty stack should be silent.

Send alerts at least two seconds apart:

```sh
sh run.sh send success --agent Codex --repo demo --summary 'Media success audio check' --data-dir "$data"
sh run.sh send failure --agent Gemini --repo demo --summary 'Media failure audio check' --data-dir "$data"
sh run.sh status --data-dir "$data"
```

Expect two pending alerts and the same PID. Complete the human checklist, then verify lifecycle:

```sh
sh run.sh stop --data-dir "$data"
sleep 1
sh run.sh status --data-dir "$data"
sh run.sh send approval --agent Copilot --repo demo --summary 'Queued while stopped' --data-dir "$data"
sh run.sh open --data-dir "$data" --audio-backend media
sh run.sh status --data-dir "$data"
```

After stop, expect `running: false`, `paused: true`. Offline send must queue silently without starting a receiver. Open must restore pending alerts silently with a new PID and `audio_backend: "media"`.

For WSLg comparison, stop first, wait one second, then reopen the same pending stack using the old path:

```sh
sh run.sh stop --data-dir "$data"
sleep 1
sh run.sh open --data-dir "$data" --audio-backend soundeffect
sh run.sh status --data-dir "$data"
```

Expect `audio_backend: "soundeffect"`. Repeat the listening checklist with identical system volume and output device. Record each backend separately. Do not claim a backend fixed WSLg without human listening confirmation.

Finish with `sh run.sh stop --data-dir "$data"`, wait one second, then run `sh run.sh status --data-dir "$data"`. Inspect `tail -n 40 "$data/runtime.log"`; expect both shutdown markers and no traceback/crash. Keep state/logs outside Git for diagnosis. A compositor may ignore placement/topmost requests; record the visible result instead of assuming support.

## Human checklist for each backend

1. With another app focused, send a new alert. Does the popup appear while the other app keeps focus? Record monitor/full-screen behavior. Can the human intentionally click and Tab through controls?
2. Hear automatic success and failure sounds separately. Are they gentle and distinct? Click Preview success, Preview failure, and Preview attention twice each, allowing two seconds between clicks. Can the human hear every attempt?
3. With an alert present, click Replay sound twice, two seconds apart. It should replay each time. Change Sound level and compare the audible level.
4. Check Mute automatic sounds, then send a new alert. The alert must appear silently. Manual Preview and Replay must still work. Uncheck mute, send another alert, and confirm sound returns without replaying older alerts.
5. With multiple alerts, Snooze must move the front alert to the back without sound. Dismiss must delete one; Undo within ten seconds must restore it. Dismiss all must clear the stack; Undo must restore the batch. Nothing should automatically dismiss.
6. Click Quit prototype during playback. Confirm no Python error. Query status in the terminal: expect stopped/paused. Reopen with the same explicit backend; pending alerts must return silently. Finish by stopping the receiver.

Only perform output-device removal/switching if the human can safely do so. Record whether the app reports an unavailable output and whether sound resumes after restoring it. Otherwise mark this check pending. No abrupt beep fallback is allowed.

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

Earlier macOS QSoundEffect popup/audio and corrected Quit were confirmed by the user. Earlier Windows QSoundEffect was inaudible while the same WAV was audible through QMediaPlayer/QAudioOutput at 0.25 and winsound. Earlier WSLg Preview/Replay was inaudible despite playback signals. These observations justify this comparison; they do not establish acceptance of the new integrated path. Ubuntu desktop remains unrun.

See [Windows comparison](windows-native-run-2026-10-29.md), [native evidence](phase-4-native-desktop-prototype.md), [Qt 6.12 QMediaPlayer](https://doc.qt.io/qt-6.12/qmediaplayer.html), and [Qt 6.12 QAudioOutput](https://doc.qt.io/qt-6.12/qaudiooutput.html).
