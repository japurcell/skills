# Native agent notification prototype

Disposable cross-platform popup and sound experiment. Requires Python 3.10+ and an existing graphical desktop/audio session.

From this directory:

- Windows: `run.cmd open`
- Ubuntu/macOS/WSLg: `sh run.sh open`
- Send an event: `run.cmd send success --agent Codex --repo skills` (use `sh run.sh` on Unix).
- Inspect or quit: `run.cmd status` / `run.cmd stop` (same Unix substitution).

The launcher installs pinned Qt wheels in a local `.venv`; no admin privileges or system configuration changes are required. Package downloads and existing OS libraries remain prerequisites. Use separate clones for Windows and Linux so environments and pending-alert stores are not shared.

The kit includes source and the generated gentle WAVs used in the macOS experiment. Environments, pending alerts, crash logs, and app bundles are ignored. Nothing registers real agent hooks or login items.

See the [platform run guide](../../brain/plans/14-agent-notifications/native-platform-run-guide.md) for WSL2 interoperability and live validation steps. macOS popup/audio and corrected Quit were verified. Windows defaults to QMediaPlayer/QAudioOutput; integrated listening confirmed automatic success/failure, all previews/replays, volume adjustment, focus retention, and Quit during playback. Automatic-mute audibility remains inconclusive. The user also confirmed WSLg media automatic success/failure, repeated Preview/Replay, sound quality, muted automatic delivery, and manual Replay while muted. WSLg offline restore, audio-active Quit, QSoundEffect A/B, and Ubuntu remain pending. Linux/macOS retain QSoundEffect by default. Stop the receiver before changing backends; `status` reports the actual backend. See the [run guide](../../brain/plans/14-agent-notifications/native-platform-run-guide.md) and [Windows evidence](../../brain/plans/14-agent-notifications/windows-native-run-2026-10-29.md).
