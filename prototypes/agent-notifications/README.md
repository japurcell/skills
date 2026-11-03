# Native agent notification prototype

Disposable cross-platform popup and sound experiment. Requires Python 3.10+ and an existing graphical desktop/audio session.

From this directory:

- Windows: `run.cmd open`
- Ubuntu/macOS/WSLg: `sh run.sh open`
- Send an event: `run.cmd send success --agent Codex --repo skills` (use `sh run.sh` on Unix).
- Inspect or quit: `run.cmd status` / `run.cmd stop` (same Unix substitution).

The launcher installs pinned Qt wheels in a local `.venv`; no admin privileges or system configuration changes are required. Package downloads and existing OS libraries remain prerequisites. Use separate clones for Windows and Linux so environments and pending-alert stores are not shared.

The kit includes source and the generated gentle WAVs used in the macOS experiment. Environments and local app bundles are ignored. Keep new pending-alert stores and logs outside Git using the run guide; do not rely on ignore rules to protect runtime state. Earlier disposable WSLg artifacts were committed only by explicit request. Nothing registers real agent hooks or login items.

See the [platform run guide](../../brain/plans/14-agent-notifications/native-platform-run-guide.md) for WSLg and native-platform validation steps. macOS popup/audio and corrected Quit were verified. Windows defaults to QMediaPlayer/QAudioOutput; integrated listening confirmed automatic success/failure, all previews/replays, volume adjustment, focus retention, and Quit during playback. The later Windows controlled-mute and keyboard-focus follow-ups passed; Enter did nothing on the two audio controls tested. Missing-output and multi-monitor coverage remain conditional.

All WSLg checks authorized for the Arch/WSLg environment are complete within safe limits. The user confirmed media playback and lifecycle behavior, full-screen foreground focus, and silent Dismiss/Ctrl+Z restoration. The Preview-label clipping found during WSLg checks was fixed in this disposable prototype and verified by a real-widget regression test and live screenshot. A distinct pending-alert run passed +30/+120/+300-second machine sampling. The earlier human-confirmed five-minute listening run still has a missed +30-second sample; its separate human acoustic result is retained without relabeling that checkpoint. The process-local no-output fixture verifies only the software no-output path, not physical-device removal or recovery. Another WSLg desktop/display was unavailable and retired for this environment only.

The current macOS run confirms all three Preview labels fit, alert and Preview/Replay audio on the current default output, visible Tab/Shift+Tab focus and Space activation, stack/Snooze, single/bulk Undo and expiry, controlled mute/manual Replay/no-catch-up, fresh automatic-event audio on MacBook Pro speakers and LG HDR 4K, audible low/high Sound level change, repeated Preview/Replay, and silent Dismiss + Command+Z restoration. The preferred OS output was restored; final volume was 0.41 at the user's choice. Ordinary/full-screen laptop/LG desktop checks passed within the reported scope; another desktop Space and physical output removal/recovery were unavailable or unverified. The final receiver stopped cleanly with eight synthetic alerts retained. Final Cocoa/offscreen suites (2 each) and source/launcher/dependency/diff checks passed. Ubuntu-specific behavior was not tested; a separate live Ubuntu run is not required. Windows Preview/focus smoke remains open. The shared Preview sizing changed in `a06fe4a4`; the latest shared focus fix still needs a focused Windows smoke. The optional WSLg QSoundEffect A/B is unrequested. Linux/macOS retain QSoundEffect by default. Stop the receiver before changing backends; `status` reports the actual audio_backend. See the [run guide](../../brain/plans/14-agent-notifications/native-platform-run-guide.md) and [Windows evidence](../../brain/plans/14-agent-notifications/windows-native-run-2026-10-29.md).
