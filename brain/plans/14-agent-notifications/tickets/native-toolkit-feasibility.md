# Native toolkit feasibility

**Type:** research
**Status:** closed
**Claimed By:** subagent-native-research
**Blocked By:** none
**Research Dir:** ../research/native-toolkit-feasibility

## Question

Which toolkit should the disposable native popup/audio prototype use across Windows, Linux, and macOS? Compare Avalonia, Qt/PySide, and Electron against small native top-level persistent windows, no focus stealing, stacking/Snooze/deletion/Undo, direct gentle WAV playback, shared CLI invocation, and resource use. Do not assume a final production architecture.

Use current official docs and select a bounded experiment with exact package/API versions and runnable build recommendations. Avalonia is an initial candidate because .NET is installed on the macOS host. Verify stable release compatibility, Linux X11/Wayland limitations, macOS activation behavior, tray limitations, and a simple cross-platform audio approach without undocumented APIs. Prefer built-in platform playback or a small maintained binding; explain dependency/install requirements and distinguish runtime proof from source evidence. No system installations, settings changes, or product code.

## Resolution

Recommend an isolated PySide6 6.12.0 prototype, not a production framework decision. A normal interactive QWidget with `WA_ShowWithoutActivating` can appear without initial activation while remaining eligible for later mouse and keyboard interaction. `QSoundEffect` supplies local WAV playback and per-effect gain; `QLocalServer`/`QLocalSocket` can route CLI events to one resident process. Wayland placement/topmost and cross-platform focus handoff still require runtime validation. See [native toolkit feasibility findings](../research/native-toolkit-feasibility/findings.md) for the sourced comparison, APIs, WSLg and WSL interop options, diagnostics, and runtime limits.
