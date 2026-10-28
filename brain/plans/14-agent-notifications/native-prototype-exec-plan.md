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
- [ ] [milestone-3] Run the experiment on actual Windows, Ubuntu desktop, and WSL2 sessions and reconcile findings before accepting cross-platform feasibility.

## Surprises & Discoveries

- Only a macOS desktop is presently available to this agent. The user specified Ubuntu/WSL2 requirements, not remote machine access. Windows/Linux runtime results must remain pending until those desktop environments run the prototype.
- Existing browser acceptance covers interaction only. Native focus, compositor positioning, audio devices, and runtime resource use are unproven.
- Native computer-use permission is unavailable. User directly confirmed macOS visibility and pleasant audible previews; own-window diagnostics reported visible/inactive. No desktop screenshot or keyboard walkthrough is claimed.
- Quit initially crashed in Qt/Python signal teardown. `app.quit()` could enter native termination before Python-owned widget cleanup. Using `app.exit(0)` followed by explicit native cleanup passed an audio-active process reproducer and the user's actual Quit-button retry. See [native evidence](phase-4-native-desktop-prototype.md).

## Decision Log

- Keep all planning/research/evidence notes under `brain/plans/14-agent-notifications/`. At the user's request, the fetchable source kit now lives in `prototypes/agent-notifications/`; historical runtime artifacts stay in the visualization directory. No runtime data or environment belongs in Git.
- Use PySide6 6.12.0 / Qt 6.12 for this experiment after comparing Avalonia and Electron. Qt provides native top-level widgets and a documented direct WAV API in one dependency. This is not production architecture approval.
- User authorized real native popup/sound prototypes. Project-local dependency restoration is allowed for this experiment; system app installation, login registration, real hooks, and remote delivery are outside this work.
- Use manual CLI/UI checks for this throwaway experiment, consistent with the prototype skill. Do not add regression tests for removal of retained history.

## Outcomes & Retrospective

Research/scaffolding and a portable source kit are complete. User confirmed native macOS popup/audio and clean Quit after the reproduced crash fix. Broader native interaction acceptance and Windows/Ubuntu/WSL2 desktop proof remain pending. This is a prototype checkpoint, not production implementation or cross-platform acceptance. User has quit the fixed app; leave it closed until explicitly reopened.

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

T4 depends on T3. Produce runnable Windows and Ubuntu artifacts where toolchains permit, with concise commands and dependency checks. WSL2 must cover a local Windows-host executable invocation via interoperability and assess WSLg Linux GUI/audio as a separate path. These are local-computer paths, not remote notification delivery. Do not claim cross-published binaries ran on those hosts.

Complete evidence notes and handoff with exactly what ran on each platform, retained logs/screenshots, unresolved compositor/audio behavior, and the first native checks the owner must perform. No packaging pass establishes cross-platform runtime acceptance by itself.

## Concrete Steps

Next owner action: fetch branch `codex/notify-app` on a real Windows or Ubuntu/WSL2 desktop, enter `prototypes/agent-notifications/`, and follow [the run guide](native-platform-run-guide.md). Use separate Windows/Linux clones. The macOS user has already confirmed the fixed Quit button. Do not reopen the app automatically after explicit Quit.

Completed local commands from the artifact `native-alert-prototype/` directory: `.venv/bin/python native_alerts.py open`, `status`, and `stop`; `.venv/bin/python -m py_compile native_alerts.py`; `sh -n run.sh`; `.venv/bin/python -m pip check`. Real desktop/audio execution required sandbox escalation but ran as the same user, without admin privileges. The source kit contains no virtual environment or user state. Its `START-HERE.txt` supplies no-admin launch commands.

## Validation and Acceptance

Use `sh run.sh send success --agent Codex --repo skills` (Windows: `run.cmd send success --agent Codex --repo skills`), inspect the popup, then exercise controls. `status` reports PID, pending count, playback count, source readiness, own-window visibility/activation, and Qt platform. `stop` uses the same shutdown handler as Quit prototype. To reproduce shutdown with output capture, run `sh run.sh serve --show --data-dir PROTOTYPE-quit-check` in one terminal, then send an alert and `stop` with the same data directory from another. Expect receiver exit 0 and both shutdown log markers; -11/139 indicates failure. User confirmed the actual button now exits without error.

Remaining observations: full focus/keyboard behavior, correct content under bursts, stack/Undo controls, mute/no-device feedback, and target compositor behavior. Windows, Ubuntu, and WSL2 require real interactive desktop runs; source portability, headless rendering, or a successful import are not substitutes. No quiet-hours scheduler or login registration was implemented in this native feasibility scope.

## Idempotence and Recovery

Keep all prototype state in its isolated artifact folder and use a prototype-specific instance identity. Closing the experiment must not affect real agents. Keep original browser artifact intact. No login items, tray installation, global shortcuts, or real hook configuration may be changed. Retain source and diagnostics if a dependency or platform fails; document the limitation and continue independent work. Cleanup applies only to the prototype process and its own isolated data.

## Interfaces and Dependencies

Use PySide6 6.12.0: QWidget for a top-level stack, WA_ShowWithoutActivating to avoid initial activation while preserving intentional keyboard interaction, QSoundEffect for low-amplitude local WAVs, and QLocalServer/QLocalSocket for same-user CLI delivery. Required boundaries: bounded JSON event input over local IPC, one resident window, pending-only JSON store, transient Undo, and explicit audio status/device diagnostics. No TCP listener, shell evaluation, raw prompts, secrets, or real agent logs. Cap event context and frame size; display summaries as plain text.
