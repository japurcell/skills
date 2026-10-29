# Native desktop popup and sound experiment

- Status: native macOS window/audio and corrected Quit verified. Windows media-backend listening, controlled mute, keyboard/stack/Undo observations, both existing output devices, desktop behavior, and clean shutdown passed the documented follow-up checks; no-output and multi-monitor coverage remain untested. For the current WSL2/WSLg media receiver, the user confirmed automatic success/failure audio, repeated manual Preview/Replay attempts, good quality, silent automatic delivery with mute checked, and audible manual Replay with mute checked. Automatic mute and manual Replay override are accepted for WSLg media; manual sound is expected because the checkbox mutes automatic sounds only. WSLg offline silent restore, audio-active Quit, old soundeffect A/B, and runtime-log assessment remain pending. Ubuntu desktop remains pending.
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
- [Run guide](native-platform-run-guide.md) gives exact commands, isolated state, expected results, backend restart/recovery, human listening questions, and a reporting checklist. Integrated Windows media checks and limited WSLg media listening acceptance are recorded below.

## Integrated Windows media-backend check (2026-10-29)

- The user heard separate automatic success/failure, all three previews, and repeated Replay; confirmed the level control worked, the alert did not steal focus, and Quit during Replay closed cleanly.
- Automatic mute remained inconclusive by ear; playback count did not increase for the muted test event. The user heard a fresh automatic failure after unmuting.
- Offline send queued while stopped; reopen restored two pending alerts silently on a new PID. Final status was stopped with both shutdown markers in the isolated runtime log. Full details are in [the Windows run note](windows-native-run-2026-10-29.md).

## Windows remaining-check follow-up (2026-10-29)

- This is additive to the earlier Windows runs above and in [the Windows run note](windows-native-run-2026-10-29.md); it does not replace their observations. On revision `d1c97146`, the fresh isolated media receiver passed the controlled automatic-mute/unmute check with direct listening confirmation. Manual Preview/Replay stayed audible while muted; older muted alerts did not replay after unmuting.
- The user confirmed the A/B/C stack stayed unchanged for 30 seconds; silent Snooze rotation, single and batch Dismiss/Undo ordering, 11-second Undo expiry, empty-state disabled controls, reactivation, and Ctrl+Z Undo all behaved as expected. All buttons were reachable and Space activated controls. Tab/Shift+Tab were reported to work; visible focus and Enter were not separately detailed.
- With user approval, Preview and automatic events were audible after switching to LG Display Audio and after restoring the Realtek speakers. No device was removed or disabled, so missing-output handling remains untested.
- On the single LG display (2560x1440, DPR 1.5), the popup appeared while another app retained typing focus, stayed readable and fully on-screen, and appeared above a full-screen app without taking its focus. On an alternate virtual desktop, it remained on the original desktop while the other app retained focus. Multi-monitor behavior is unavailable.
- The Windows receiver stopped cleanly (`running=false`, `paused=true`, `pending=6`); the isolated log contains both shutdown markers and no traceback, exception, crash, failed operation, or non-empty audio error. Full details and log path are in the Windows run note.

## Observed macOS evidence

- Host: macOS 26.7 arm64, Python 3.14, Qt cocoa platform. Dependencies restored from official PyPI wheels.
- First successful CLI request started PID 77118; reported 590.8 ms within the CLI process. Warm status request reached the same PID in 0.4 ms. These are single observations, not p95 latency or full shell-start measurements.
- All sound sources became Ready; QSoundEffect reported a complete playing/finished cycle. User explicitly confirmed the popup was visible and success/failure previews were audible and gentle.
- Later reopen reported `window_visible=true`, `window_active=false`, all sounds Ready, and 331.8 ms CLI handling. This is own-window state evidence, not full focus behavior across applications/spaces.
- Native computer-use permission was unavailable, so no OS screenshot, keyboard walkthrough, or pixel-level inspection was performed. User confirmation supplies direct visual/listening evidence only for the stated checks.
- Syntax compilation, POSIX launcher syntax, and `pip check` passed. These checks do not prove native UI/audio behavior. Windows and WSLg media evidence is recorded separately; Ubuntu remains unrun and historical QSoundEffect behavior remains distinct from the user-confirmed media-backend checks.

## Observed WSL2 / WSLg audio feedback

- Host: Arch Linux under WSL2, WSLg, Qt `wayland`, PulseAudio server configured at `/mnt/wslg/PulseServer`.
- On 2026-10-29, user reported hearing a sound when the app first opened, but hearing nothing after clicking any Preview button or Replay sound. This is direct user listening feedback; do not treat Qt playback state as proof the user heard it.
- Test receiver PID 1469090 used isolated directory `prototypes/agent-notifications/PROTOTYPE-wslg-feedback-20261029/`. Qt reported all effects `Ready`, available output, visible/active window, and `playing=true` then `playing=false` for requests. After user interaction, status reported `audio_play_count=21`, `pending=0`. Thus native API playback and audible user outcome disagree.
- The runtime log also has PipeWire symbol-resolution warnings and later `Failed to get sink information: "Timeout"` diagnostics. These are observed alongside the issue; root cause is not established.
- Keep the historical QSoundEffect path as an unresolved audio-delivery defect. Further diagnosis must distinguish button handler/play invocation, Qt output-device/backend state, and audible WSLg output. Preserve the user's observation; do not claim QSoundEffect manual preview works based only on status/signals.

## Current WSLg media-backend checkpoint (2026-10-29)

- The receiver uses PID `1658470`, isolated data directory `/tmp/agent-alert-wslg-media.ZTWz4x`, `audio_backend=media`, and Qt platform `wayland`. Keep it open and unchanged; do not stop, restart, send more audio, switch backends, or change source.
- All three sources reported `Ready`; initial status was `pending=0`, `audio_play_count=0`. Success and failure events were sent three seconds apart. Latest status was `pending=2`, `audio_play_count=2`, `window_visible=true`, and `window_active=true`.
- Human listening: user confirmed hearing both automatic success/failure sounds, all manual Preview and Replay attempts (each repeated twice, two seconds apart), and described quality as "sounds good." The user confirmed the muted approval alert appeared silently; parent CLI status changed from pending `0`/playback `14` before send to pending `1`/playback `14` after two seconds. User also confirmed Replay is audible while "Mute automatic sounds" remains selected. Automatic mute and manual Replay override are accepted for WSLg media; Replay is expected to remain available because the checkbox suppresses automatic sounds only. Offline silent restore, audio-active Quit, and old soundeffect A/B remain pending. Keep human observation separate from Qt status and playback signals.
- The runtime log is retained at `<data-dir>/runtime.log`; log errors were not assessed in this documentation checkpoint.

## Quit crash and correction

- User reported a Python error after clicking Quit prototype. macOS crash report showed SIGSEGV in `PySide::SenderSignalDeletionTracker::senderDestroyed`, during QWidget/Python binding teardown.
- Reproduced through the public stop command, which calls the same Quit handler: receiver exited -11. [Before-fix log](../../../../../../visualizations/2026/10/22/01a16214-d358-76a3-b29a-244a36c7786e/native-alert-prototype/quit-before.log).
- Explicit object cleanup after `app.quit()` alone was insufficient when sound was active; native termination could occur before that cleanup executed.
- Fix: exit the Qt event loop with `app.exit(0)`, stop timers/audio/socket activity, then destroy owned Qt objects while Python binding machinery remains alive. Also replace a delayed callback against a destroyed socket with a parent-owned timer and live-socket check.
- Audio-active reproducer then exited 0 and logged both event-loop stop and object destruction. [After-fix log](../../../../../../visualizations/2026/10/22/01a16214-d358-76a3-b29a-244a36c7786e/native-alert-prototype/quit-with-audio-after.log). User retried the actual Quit prototype button and confirmed no error.
- The user previously quit the macOS prototype after verifying its Quit button. Current WSLg receiver state is tracked in the active handoff; do not infer it is stopped from the older macOS observation.
- Reflection: task-specific findings stay here. Explicit Qt/Python lifetime cleanup and actual process exit checks are required before trusting native shutdown; no unrelated skill files were edited.
