# Native desktop popup and sound experiment

- Status: native macOS window/audio and corrected Quit verified. Windows runtime/lifecycle and empty-state controls were manually checked; QSoundEffect audio remains inaudible to the user. WSL2/WSLg manual Preview/Replay sound is also unconfirmed. Ubuntu desktop remains pending.
- User accepted deletion/Undo browser interaction and requested native prototypes. Linux targets are Ubuntu desktop and WSL2. User has no admin access.
- [Runnable source bundle](../../../../../../visualizations/2026/10/22/01a16214-d358-76a3-b29a-244a36c7786e/native-alert-prototype.zip)
- [Tracked source kit](../../../prototypes/agent-notifications/README.md) is the canonical fetchable copy on branch `codex/notify-app`. It includes only source, launchers, pinned requirements, and gentle WAV assets; no environments, logs, pending alerts, or local app bundles.
- [Prototype source](../../../prototypes/agent-notifications/native_alerts.py)
- [Platform run instructions](native-platform-run-guide.md)
- [Windows run and audio comparison](windows-native-run-2026-10-29.md)
- [Native ExecPlan](native-prototype-exec-plan.md)
- [Toolkit research](research/native-toolkit-feasibility/findings.md)

## Implemented experiment

- PySide6/Qt 6.12.0 real desktop window. Windows now defaults to QMediaPlayer/QAudioOutput; Linux/macOS retain QSoundEffect, with `--audio-backend media|soundeffect` for explicit comparison. This is an experiment, not production framework approval.
- One resident receiver via local IPC; bounded event context, plain-text labels, per-user endpoint protection, and isolated `PROTOTYPE-data/pending.json`.
- Real first-send startup, warm reuse, persistent pending stack, Snooze, deletion/10-second memory-only Undo, bulk deletion, replay, mute, and sound level.
- Quit persists paused state and exits. Later CLI sends queue offline without launching a popup or playing audio. Open restores pending alerts silently.
- Three generated 1.1-second WAV motifs: success, failure, and attention. Peak source levels are about -24.4 to -25.0 dBFS; default playback gain is 0.25. These figures do not establish acoustic loudness.
- No system install, real hooks, login items, global shortcut, network listener, or remote delivery. Dependencies live in the project virtual environment. Python 3.10+ and existing desktop/audio prerequisites are required.
- Quiet-hours schedules, temporary mute durations, sound-file picking, login registration, and full visual-stack styling are not implemented in this bounded native experiment.

## Authorized media-backend revision (2026-10-29)

- User accepted switching Windows to QMediaPlayer/QAudioOutput and comparing that path on WSLg. `auto` selects media on Windows and QSoundEffect elsewhere. Backend selection applies only to receiver startup; `status` identifies the actual selection.
- Existing sound files, volume range/default, manual previews/replay, automatic mute, and explicit Qt teardown remain. Muting cancels queued/loading automatic playback; manual previews remain available.
- Local macOS offscreen CLI checks passed for both backends: four separate events produced four playback starts, all sources became Ready, stop during playback reached both cleanup markers, offline send queued without launching, and reopen restored six alerts with zero playback. Retained logs: `/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/agent-alert-final-media-tpdj25vi/runtime.log` and `agent-alert-final-soundeffect-sxy3d18y/runtime.log` in the same parent directory. These are API/process checks, not human listening or Windows/WSLg proof.
- [Run guide](native-platform-run-guide.md) now gives a novice coding agent exact commands, isolated state, expected results, backend restart/recovery, human listening questions, and a reporting checklist. New integrated Windows/WSLg listening acceptance remains pending.

## Observed macOS evidence

- Host: macOS 26.7 arm64, Python 3.14, Qt cocoa platform. Dependencies restored from official PyPI wheels.
- First successful CLI request started PID 77118; reported 590.8 ms within the CLI process. Warm status request reached the same PID in 0.4 ms. These are single observations, not p95 latency or full shell-start measurements.
- All sound sources became Ready; QSoundEffect reported a complete playing/finished cycle. User explicitly confirmed the popup was visible and success/failure previews were audible and gentle.
- Later reopen reported `window_visible=true`, `window_active=false`, all sounds Ready, and 331.8 ms CLI handling. This is own-window state evidence, not full focus behavior across applications/spaces.
- Native computer-use permission was unavailable, so no OS screenshot, keyboard walkthrough, or pixel-level inspection was performed. User confirmation supplies direct visual/listening evidence only for the stated checks.
- Syntax compilation, POSIX launcher syntax, and `pip check` passed. These checks do not prove native UI/audio behavior. The Windows run is documented separately; Ubuntu remains unrun and WSLg audibility is unresolved.

## Observed WSL2 / WSLg audio feedback

- Host: Arch Linux under WSL2, WSLg, Qt `wayland`, PulseAudio server configured at `/mnt/wslg/PulseServer`.
- On 2026-10-29, user reported hearing a sound when the app first opened, but hearing nothing after clicking any Preview button or Replay sound. This is direct user listening feedback; do not treat Qt playback state as proof the user heard it.
- Test receiver PID 1469090 used isolated directory `prototypes/agent-notifications/PROTOTYPE-wslg-feedback-20261029/`. Qt reported all effects `Ready`, available output, visible/active window, and `playing=true` then `playing=false` for requests. After user interaction, status reported `audio_play_count=21`, `pending=0`. Thus native API playback and audible user outcome disagree.
- The runtime log also has PipeWire symbol-resolution warnings and later `Failed to get sink information: "Timeout"` diagnostics. These are observed alongside the issue; root cause is not established.
- Keep this as an unresolved audio-delivery defect. Further diagnosis must distinguish button handler/play invocation, Qt output-device/backend state, and audible WSLg output. Preserve the user's observation; do not claim manual preview works based only on `QSoundEffect` status/signals.

## Quit crash and correction

- User reported a Python error after clicking Quit prototype. macOS crash report showed SIGSEGV in `PySide::SenderSignalDeletionTracker::senderDestroyed`, during QWidget/Python binding teardown.
- Reproduced through the public stop command, which calls the same Quit handler: receiver exited -11. [Before-fix log](../../../../../../visualizations/2026/10/22/01a16214-d358-76a3-b29a-244a36c7786e/native-alert-prototype/quit-before.log).
- Explicit object cleanup after `app.quit()` alone was insufficient when sound was active; native termination could occur before that cleanup executed.
- Fix: exit the Qt event loop with `app.exit(0)`, stop timers/audio/socket activity, then destroy owned Qt objects while Python binding machinery remains alive. Also replace a delayed callback against a destroyed socket with a parent-owned timer and live-socket check.
- Audio-active reproducer then exited 0 and logged both event-loop stop and object destruction. [After-fix log](../../../../../../visualizations/2026/10/22/01a16214-d358-76a3-b29a-244a36c7786e/native-alert-prototype/quit-with-audio-after.log). User retried the actual Quit prototype button and confirmed no error.
- The user previously quit the macOS prototype after verifying its Quit button. Current WSLg receiver state is tracked in the active handoff; do not infer it is stopped from the older macOS observation.
- Reflection: task-specific findings stay here. Explicit Qt/Python lifetime cleanup and actual process exit checks are required before trusting native shutdown; no unrelated skill files were edited.
