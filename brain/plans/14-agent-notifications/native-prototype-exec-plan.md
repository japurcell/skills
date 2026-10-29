# Prototype native alert windows and gentle sounds

## Purpose / Big Picture

Move the accepted browser interaction into a disposable real desktop-window experiment on Windows, Ubuntu desktop, WSL2, and macOS. Verify native window presentation and direct WAV playback without installing real hooks or login items. The prototype must identify unsupported desktop/audio conditions instead of reporting silent success.

## Progress

- [x] (2026-10-21) [milestone-1] Confirm local host: macOS 26.7 arm64, .NET SDK 10.0.401. User named Ubuntu desktop and WSL2 as Linux targets.
- [x] (2026-10-22) [milestone-1] Resolve toolkit research and create isolated Qt/PySide 6.12 source, pinned requirements, WAV assets, and local launchers.
- [x] (2026-10-22) [milestone-2] Exercise macOS native CLI/receiver/audio; user confirmed visible popup and gentle success/failure previews.
- [x] (2026-10-22) [milestone-2] Reproduce Quit SIGSEGV (-11), correct event-loop/object teardown, verify audio-active exit 0, and obtain user confirmation that the actual button quits without error.
- [ ] [milestone-2] Complete native keyboard/focus, stack/Undo, mute, no-device, and desktop-space checks; computer-use permission is unavailable here.
- [x] (2026-10-22) [milestone-3] Produce portable source kit and Windows/Ubuntu/WSL2 instructions without system/admin installation steps.
- [x] (2026-10-28) [milestone-3] Add the verified source kit to `prototypes/agent-notifications/` for Git-based transfer, excluding environments, logs, app bundles, and pending alerts.
- [x] (2026-10-22) [milestone-3] Record evidence, limits, and recovery in the native phase note and run guide.
- [x] (2026-10-29) [milestone-3] Exercise the Linux WSL2/WSLg source-kit path; window/audio API and shutdown diagnostics passed.
- [x] (2026-10-29) [milestone-3] Run the Windows source kit: pinned dependencies restored locally, native receiver/CLI and clean shutdown exercised in isolated state.
- [x] (2026-10-29) [milestone-3] Increase Windows action-button label room and contrast; user confirmed labels fit in populated and empty states.
- [x] (2026-10-29) [milestone-3] Style disabled Windows controls distinctly; user confirmed labels stay legible, controls look disabled, and clicks do nothing.
- [x] (2026-10-29) [milestone-3] Compare Windows QSoundEffect, QMediaPlayer, and winsound using the same WAV; QMediaPlayer/winsound were audible, QSoundEffect was not at its maximum 0.50 volume.
- [ ] [milestone-3] Owning agent: decide and apply any Windows audio-backend change; rerun manual audible acceptance.
- [ ] [milestone-3] Continue WSLg audio investigation and complete remaining keyboard/focus/audio-device checks plus Ubuntu desktop run.

## Surprises & Discoveries

- WSL2 WSLg is available on this host (Arch Linux, Wayland). Qt reports effects Ready and playback start/finish, but the user heard only the initial sound and heard nothing from Preview or Replay controls. API diagnostics are not proof of audible output; root cause remains unknown.
- Windows runtime succeeded with one receiver PID, visible-window and Ready-device diagnostics, success/failure sends, offline queue/reopen, and clean stop. The user's audible report varied by interaction session: initially Replay was audible and Preview was not; later neither was audible, even at maximum QSoundEffect gain. Playback signals are not proof of audible output.
- The Windows screenshot `prototypes/agent-notifications/windows-cutoff-buttons.png` shows alert actions disabled under “Stack clear” with labels reported hard to read/cut off. The user chose to keep these actions visible and disabled, rather than hide them.
- The final Windows button styling keeps disabled text legible and visually distinct; the user confirmed disabled controls do nothing. The intermediate failure is preserved in `prototypes/agent-notifications/windows-buttons-not-disabled.png`; the original legibility report is `prototypes/agent-notifications/windows-cutoff-buttons.png`.
- At Windows QSoundEffect volume 0.50, the user heard neither Replay nor Preview, although the effects were Ready and Qt logged playback. The same WAV was audible via `winsound` at gains 1.0, 0.50, and 0.25, and via Qt QMediaPlayer/QAudioOutput at volume 0.25. This points to QSoundEffect-specific behavior, not a proven driver cause.
- Existing browser acceptance covers interaction only. Native focus, compositor positioning, audio devices, and runtime resource use are unproven.
- Native computer-use permission is unavailable. User directly confirmed macOS visibility and pleasant audible previews; own-window diagnostics reported visible/inactive. No desktop screenshot or keyboard walkthrough is claimed.
- Quit initially crashed in Qt/Python signal teardown. `app.quit()` could enter native termination before Python-owned widget cleanup. Using `app.exit(0)` followed by explicit native cleanup passed an audio-active process reproducer and the user's actual Quit-button retry. See [native evidence](phase-4-native-desktop-prototype.md).

## Decision Log

- Keep all planning/research/evidence notes under `brain/plans/14-agent-notifications/`. At the user's request, the fetchable source kit now lives in `prototypes/agent-notifications/`; historical runtime artifacts stay in the visualization directory. No runtime data or environment belongs in Git.
- Use PySide6 6.12.0 / Qt 6.12 for this experiment after comparing Avalonia and Electron. Qt provides native top-level widgets and a documented direct WAV API in one dependency. This is not production architecture approval.
- User authorized real native popup/sound prototypes. Project-local dependency restoration is allowed for this experiment; system app installation, login registration, real hooks, and remote delivery are outside this work.
- Use manual CLI/UI checks for this throwaway experiment, consistent with the prototype skill. Do not add regression tests for removal of retained history.
- For the Windows empty state, keep alert actions visible but disabled and improve their legibility. The user approved a GUI-level empty-to-populated state check; manual listening remains separate from Qt playback diagnostics.
- Disabled styling must remain visibly distinct from active buttons while keeping text legible. System-palette text/window/mid roles now pass the real Windows GUI check.
- Do not change the Windows audio backend in this task. The user asked to record the comparison findings for the owning agent to decide and implement any needed change.

## Outcomes & Retrospective

Research/scaffolding and a portable source kit are complete. User confirmed native macOS popup/audio and clean Quit after the reproduced crash fix. Windows runtime/lifecycle checks passed. The user manually verified legible, visibly disabled, inactive empty-state controls. Windows QSoundEffect remained inaudible at maximum gain, while the same WAV was audible through winsound at 0.25/0.50 and QMediaPlayer at 0.25. No audio backend change was made because the user delegated that decision to the owning agent. WSL2/WSLg has an unresolved manual audibility mismatch; Ubuntu remains unrun. Keyboard/focus and other visual checks remain open. This is a prototype checkpoint, not production implementation or cross-platform acceptance.

## Context and Orientation

Current product contract is `phase-3-deletion-and-undo.md`: all alert types persist until dismissed; Snooze cycles to the back; Dismiss and Dismiss all delete with brief Undo; pending records survive restart; no separate history. Sounds play once per new event, with explicit replay, independent mute/quiet control, no automatic replay on cycling/reopening. The native experiment prioritizes actual window/audio delivery; any omitted product behavior must be visibly labeled and recorded.

The canonical source kit is `prototypes/agent-notifications/`, with launchers, pinned requirements, Python source, and three gentle WAV assets. Runtime `.venv`, `PROTOTYPE-*/`, logs, and `.app` bundles are ignored there. The original macOS runtime evidence remains under `/Users/adam/.codex/visualizations/2026/10/22/01a16214-d358-76a3-b29a-244a36c7786e/native-alert-prototype/`. No real installed logs or session state may be used.

## Plan of Work

### Milestone 1: Select and scaffold a bounded experiment
Status: done
Acceptance: met

T1 research is closed with primary-source findings. T2 created `native_alerts.py`, `requirements.txt`, launchers, generated WAVs, and an isolated virtual environment. Requirements pin Essentials/Addons/Shiboken 6.12.0; the initial local meta-package install also included unused Qt components, while the portable kit restores only required package families. No global packages, templates, or workloads were installed. Import, syntax, and `pip check` passed.

### Milestone 2: Exercise native popup and sound on macOS
Status: in progress
Acceptance: not met

T3 depends on T2. Implement one real persistent native alert window with topmost requested and focus activation disabled for background alerts. Preserve stack, Snooze, deletion/Undo, and explicit replay. Generate short, low-amplitude, gently faded WAVs with distinct success/failure motifs. Route audio through an explicit platform adapter that reports player errors, never an abrupt beep fallback. A simple CLI must submit events to one resident UI instance, with clear diagnostics and isolated data. Do not build provider adapters or production notification installation.

Observed: real Qt cocoa receiver and QSoundEffect playback; user confirmed visible popup and gentle audible success/failure previews. Source WAV duration/peaks, first/warm CLI samples, visible/inactive diagnostics, offline queuing, and clean Quit evidence are recorded in the phase note. Remaining checks require user interaction because native computer use is not granted. Do not substitute internal state for keyboard, compositor, or screen-reader proof.

### Milestone 3: Package cross-platform experiments and reconcile evidence
Status: in progress
Acceptance: not met

T4 depends on T3. Produce runnable Windows and Ubuntu artifacts where toolchains permit, with concise commands and dependency checks. The Windows source kit runs with local PySide6 6.12.0 wheels and isolated state. One PID served live success/failure sends; offline send queued while stopped; reopening restored three pending alerts without playback; stop exited cleanly. The user approved and manually verified the Windows action-button legibility/disabled-state correction. Audio remains unaccepted: QSoundEffect was inaudible at 0.50, while the same WAV was audible via winsound at 0.25/0.50 and QMediaPlayer/QAudioOutput at 0.25.

Keep the empty-state actions visible but make disabled labels legible, as the user requested. The user approved checking the real GUI transition from empty to populated state; this is the regression seam, while actual audio audibility must still be confirmed by listening. WSL2 must cover a local Windows-host executable invocation via interoperability and assess WSLg Linux GUI/audio as a separate path. These are local-computer paths, not remote notification delivery. Do not claim cross-published binaries ran on those hosts.

Complete evidence notes and handoff with exactly what ran on each platform, retained logs/screenshots, unresolved compositor/audio behavior, and the first native checks the owner must perform. No packaging pass establishes cross-platform runtime acceptance by itself.

## Concrete Steps

Next action (owning agent): decide whether to use the verified audible QMediaPlayer/QAudioOutput path for Windows while retaining QSoundEffect elsewhere, then implement and test only if authorized. On 2026-10-29 the user could not hear QSoundEffect Preview/Replay at its maximum 0.50 gain; the same WAV was audible through winsound at 1.0, 0.50, and 0.25, and through QMediaPlayer/QAudioOutput at 0.25. This isolates an observable QSoundEffect-path difference but not its internal cause. User explicitly asked this coordinator to record findings and leave audio changes to the owning agent. The revised disabled button style passed the approved GUI check: labels are legible and distinct, and disabled actions do nothing. The original screenshot is `prototypes/agent-notifications/windows-cutoff-buttons.png`; `prototypes/agent-notifications/windows-buttons-not-disabled.png` records the intermediate style failure. Windows evidence and repeat commands are in [the run note](windows-native-run-2026-10-29.md). The isolated data/log is outside the repository at `C:\Users\jeffreypurcell\.copilot\session-state\527b7ff6-948d-4594-9e39-1cbe9b154ee9\files\PROTOTYPE-windows-20261029\`; all Windows receiver PIDs were stopped. Do not install system packages or bypass policy.

Completed local commands from the artifact `native-alert-prototype/` directory: `.venv/bin/python native_alerts.py open`, `status`, and `stop`; `.venv/bin/python -m py_compile native_alerts.py`; `sh -n run.sh`; `.venv/bin/python -m pip check`. Real desktop/audio execution required sandbox escalation but ran as the same user, without admin privileges. The source kit contains no virtual environment or user state. Its `START-HERE.txt` supplies no-admin launch commands.

## Validation and Acceptance

Use `sh run.sh send success --agent Codex --repo skills` (Windows: `run.cmd send success --agent Codex --repo skills`), inspect the popup, then exercise controls. `status` reports PID, pending count, playback count, source readiness, own-window visibility/activation, and Qt platform. `stop` uses the same shutdown handler as Quit prototype. To reproduce shutdown with output capture, run `sh run.sh serve --show --data-dir PROTOTYPE-quit-check` in one terminal, then send an alert and `stop` with the same data directory from another. Expect receiver exit 0 and both shutdown log markers; -11/139 indicates failure. User confirmed the actual button now exits without error.

Observed Windows run on 2026-10-29 from the source-kit directory with isolated state outside the repository. Pinned Windows PySide6 6.12.0 wheels restored in `.venv`; `py_compile` and `pip check` passed. Live success/failure sends shared PID 10504; stop persisted two pending alerts, offline `approval` queued a third, reopen used PID 8236 and restored three without autoplay, and final stop reported `running=false`, `paused=true`, `pending=3`. Runtime log ended with `event-loop-stopped` and `objects-destroyed`. User verified the final empty/populated action UI: labels fit, disabled actions look disabled and do nothing. User reported QSoundEffect Preview/Replay inaudible at maximum gain; status still showed Ready and a playback count, which does not establish audibility. In separate checks the same WAV was audible via built-in `winsound` at gains 1.0, 0.50, and 0.25, and via `QMediaPlayer`/`QAudioOutput` at 0.25. Qt docs: [QMediaPlayer](https://doc.qt.io/qt-6/qmediaplayer.html), [QAudioOutput](https://doc.qt.io/qt-6/qaudiooutput.html); `winsound` docs: https://docs.python.org/3/library/winsound.html. User said the owning agent should apply any needed audio change; this task did not change the audio backend. Isolated data/log: `C:\Users\jeffreypurcell\.copilot\session-state\527b7ff6-948d-4594-9e39-1cbe9b154ee9\files\PROTOTYPE-windows-20261029\`. User screenshots `prototypes/agent-notifications/windows-cutoff-buttons.png` and `windows-buttons-not-disabled.png` remain untracked.

Observed WSL2/WSLg run on 2026-10-29 from the repository root, using isolated data directory `PROTOTYPE-wslg-check-20261029`: `sh prototypes/agent-notifications/run.sh open --data-dir PROTOTYPE-wslg-check-20261029`, followed by success and failure sends, `status`, and `stop`. Host reported WSL2 kernel `6.18.54.1-microsoft-standard-WSL2`, Arch Linux, `DISPLAY=:0`, `WAYLAND_DISPLAY=wayland-0`, and PulseAudio at `/mnt/wslg/PulseServer`. Receiver used Qt `wayland`; one PID served open and both sends; `window_visible=true`; it became inactive after sends; all sounds reached `Ready`; output was available and both sound calls logged `playing=true` then `playing=false`. Qt warned it could not load PipeWire symbols and used FFmpeg. `stop` reported paused/not running with two queued test alerts; the process exited and logged both shutdown markers. Log: `prototypes/agent-notifications/PROTOTYPE-wslg-check-20261029/runtime.log`. These diagnostics do not prove a person saw the popup or heard gentle audio.

User's later listening feedback on the open WSLg preview: heard sound when app first opened, but none after clicking any Preview button or Replay sound. Latest queried status still showed effects Ready, window visible/active, `audio_play_count=21`, `pending=0`; runtime log records repeated playback signals but also PipeWire resolver warnings and `Failed to get sink information: "Timeout"`. Log: `prototypes/agent-notifications/PROTOTYPE-wslg-feedback-20261029/runtime.log`. The receiver state might have changed after this observation; check before interaction. This audible/manual path is not accepted.

Remaining observations: owning agent to decide and implement any Windows audio-backend change; resolve WSLg manual audibility; complete full focus/keyboard behavior, correct content under bursts, stack/Undo controls, mute/no-device feedback, and target compositor behavior; run Ubuntu desktop checks. Source portability, headless rendering, or a successful import are not substitutes. No quiet-hours scheduler or login registration was implemented in this native feasibility scope.

## Idempotence and Recovery

Keep all prototype state in its isolated artifact folder and use a prototype-specific instance identity. Closing the experiment must not affect real agents. Keep original browser artifact intact. No login items, tray installation, global shortcuts, or real hook configuration may be changed. Retain source and diagnostics if a dependency or platform fails; document the limitation and continue independent work. Cleanup applies only to the prototype process and its own isolated data.

## Interfaces and Dependencies

Use PySide6 6.12.0: QWidget for a top-level stack, WA_ShowWithoutActivating to avoid initial activation while preserving intentional keyboard interaction, QSoundEffect for low-amplitude local WAVs on the existing path, and QLocalServer/QLocalSocket for same-user CLI delivery. A Windows comparison found QMediaPlayer/QAudioOutput audible where QSoundEffect was not; the owning agent must decide whether to adopt that platform-specific path. Required boundaries: bounded JSON event input over local IPC, one resident window, pending-only JSON store, transient Undo, and explicit audio status/device diagnostics. No TCP listener, shell evaluation, raw prompts, secrets, or real agent logs. Cap event context and frame size; display summaries as plain text.
