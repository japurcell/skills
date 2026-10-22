# Native toolkit feasibility findings

**Research date:** 2026-10-21  
**Scope:** A disposable, local-only native window and audio experiment. This does not choose a production framework.

## Recommendation

Use **PySide6 6.12.0** for the next native prototype, installed only into a project virtual environment. Qt has direct APIs for a normal interactive top-level widget that initially appears without activation, low-latency local WAV feedback with per-effect gain, and local IPC for a single resident process. Its Linux Wayland placement and stacking behavior still needs an actual desktop test.

The 6.12 release was published on 2026-10-09. The macOS universal2 wheel supports ARM64 and x86-64 from macOS 14, and is tagged `cp310-abi3`, which matches the host's Python 3.14 ABI. The PyPI release also publishes Linux x86-64 and ARM64 wheels. Qt lists Ubuntu 22.04 and 24.04 x86-64 as desktop targets; its ARM desktop target is Ubuntu 24.04. [Qt for Python 6.12 release](https://www.qt.io/blog/qt-for-python-release-6.12-is-here), [PySide6 6.12.0 wheel metadata](https://pypi.org/project/PySide6/6.12.0/), [Qt 6.12 supported platforms](https://doc.qt.io/qt-6.12/supported-platforms.html)

For an experiment, create `.venv` with the installed Python and install the pinned package there:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install PySide6==6.12.0
```

On Windows, use `.venv\Scripts\python.exe -m pip install PySide6==6.12.0`. Installing the PySide6 meta-package brings its Essentials, Addons, and Shiboken packages, including the Qt binaries in that environment. This avoids a system-wide install, but is not a small dependency footprint. [Qt for Python package details](https://doc.qt.io/qtforpython-6/package_details.html)

## Window, focus, and display behavior

Use an ordinary, focusable `QWidget` with a frameless and topmost hint. Set `WA_ShowWithoutActivating` before the initial `show()`:

```python
window.setWindowFlags(
    Qt.WindowType.Window
    | Qt.WindowType.WindowStaysOnTopHint
    | Qt.WindowType.FramelessWindowHint
)
window.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
window.show()
```

**This preserves later intentional interaction.** `WA_ShowWithoutActivating` describes how the widget is shown: without making it active. It does not permanently reject focus. Keep ordinary focusable buttons and test that a deliberate click activates the stack and that Tab/Shift+Tab and keyboard shortcuts then work. Do not use `WindowDoesNotAcceptFocus` for this prototype: Qt documents that flag as telling the window system the window should not receive input focus, which conflicts with keyboard-accessible buttons. The Qt API describes the intended behavior, but actual focus handoff still needs verification on each window manager/compositor.

`WindowStaysOnTopHint` is a request to the window system. Qt documents an X11 window-manager caveat: some managers require `X11BypassWindowManagerHint` too. Do not add that bypass flag to force stacking; test the normal hint and record the result. Qt also warns that some window systems cannot set or query top-level coordinates, and specifically notes that `setPosition` is unsupported on platforms such as Wayland. A precise bottom-right stack position or guaranteed always-on-top behavior is therefore not portable to standard Wayland. Let the compositor place the initial window there, or test a standard-window fallback instead of depending on arbitrary global coordinates. [Qt 6.12 Qt namespace flags](https://doc.qt.io/qt-6.12/qt.html), [Qt 6.12 QWindow positioning and activation](https://doc.qt.io/qt-6.12/qwindow.html)

On macOS, avoid using the `Qt.Tool` window type for the alert stack: Qt documents tool windows as hidden while the application is inactive by default, unless `WA_MacAlwaysShowToolWindow` is set. A regular frameless top-level widget is the better experiment. Verify the app does not become frontmost when the alert is delivered, then verify it can be deliberately clicked and keyboard-operated. Qt 6.12 officially supports macOS 14.4 and later, including macOS 26, on arm64.

For Linux, treat X11 and Wayland as separate cases. Under X11, the window manager decides how topmost hints and placement behave. Under Wayland, compositor policy limits client placement and activation. The experiment should record whether the system preserves the user's current focus, where it places the widget, and whether the topmost hint is honored. Do not report placement as proven by a successful Qt API call.

WSLg is a local bridge option for WSL2. Microsoft documents that its system distro runs an X server, Wayland server, and PulseAudio server, projecting their sockets and setting `DISPLAY`, `WAYLAND_DISPLAY`, and `PULSE_SERVER` in the user distro. This enables Linux UI and audio paths to be tested, while leaving window placement/focus subject to the WSLg compositor and Windows host. If the requirement is specifically a Windows-native popup from WSL, WSL interoperability also allows launching a Windows executable by name with the `.exe` suffix; it runs as the active Windows user and appears in Windows Task Manager. That can be a local-only bridge to a Windows-native alert host, not remote delivery. [Microsoft WSLg architecture](https://github.com/microsoft/wslg), [Microsoft WSL interoperability](https://learn.microsoft.com/en-us/windows/wsl/filesystems#run-windows-tools-from-linux)

## Audio and CLI path

Use one reused `QSoundEffect` instance. Set a local file URL, call `setVolume(0.1)` as an initial experiment setting, and call `play()` when a new alert arrives. Qt describes `QSoundEffect` as suited to low-latency feedback from uncompressed files, typically WAV. Its gain is **per effect/application playback**, linearly scaled from 0.0 to 1.0, not a control over the OS mixer or a promise of perceived loudness. Keep a user-visible mute and volume control, use a quiet source asset, and listen at realistic system volumes. The documented status values include `Ready` and `Error`; inspect that status, `QMediaDevices.defaultAudioOutput`, and actual playback. If no output device is available or the sound fails, keep the visual alert working and report audio as unavailable rather than claiming it played. [Qt 6.12 QSoundEffect](https://doc.qt.io/qt-6.12/qsoundeffect.html), [Qt 6.12 QMediaDevices](https://doc.qt.io/qt-6.12/qmediadevices.html)

`afplay` on macOS, Windows `System.Media.SoundPlayer` or `PlaySound`, and Linux `paplay` or `aplay` are possible platform-specific fallbacks, but they are not a single consistent API and command availability varies. Do not make them the primary cross-platform route. If a fallback is tested, check executable/API availability before invoking it, capture the result and error output, and keep the UI explicit that sound is unavailable when the requested playback cannot be confirmed. The Qt route supplies the same gain API on each toolkit target.

For a shared CLI entry point, keep one resident GUI process and pass event data to it over `QLocalServer`/`QLocalSocket`. Qt documents the local socket as a named pipe on Windows and a local-domain socket on Unix. A CLI helper can connect, send one bounded event message, wait for an acknowledgement, and exit without spawning a second GUI. Keep the endpoint local and validate message shape before displaying it. Qt also documents that Unix socket permission flags are not honored on macOS, so do not treat those flags alone as an access boundary there. [Qt 6.12 QLocalServer](https://doc.qt.io/qt-6.12/qlocalserver.html), [Qt 6.12 QLocalSocket](https://doc.qt.io/qt-6.12/qlocalsocket.html)

`QSystemTrayIcon` can remain an optional reopen/quit path. Qt lists Windows, macOS, and Linux desktops implementing StatusNotifierItem or XEmbed, and provides `isSystemTrayAvailable()`. Do not make the prototype depend on a tray being present; GNOME Shell may also omit tray activation reasons unless shell extensions are installed. [Qt 6.12 QSystemTrayIcon](https://doc.qt.io/qt-6.12/qsystemtrayicon.html)

## Alternatives

| Toolkit | Current stable API check | Fit for this prototype |
| --- | --- | --- |
| **Avalonia** | Avalonia 12.1.4 was the latest release on 2026-10-21. Its `Window.ShowActivated` property directly expresses whether the first show activates the window. | A credible C# UI candidate and the installed .NET SDK makes it easy to start. The official Linux guide calls the Wayland backend early-stage, says `UsePlatformDetect()` does not select it, and requires explicitly adding `Avalonia.Wayland` and calling `UseWayland()`. That is a weak fit for a Linux desktop experiment where Wayland behavior matters. [12.1.4 release](https://github.com/AvaloniaUI/Avalonia/releases/tag/12.1.4), [Window API](https://docs.avaloniaui.net/api/avalonia/controls/window), [Linux and Wayland guide](https://docs.avaloniaui.net/docs/platform-specific-guides/linux) |
| **Qt / PySide6** | PySide6 6.12.0 is current stable and has exact APIs for initial no-activation, sound, and local IPC. | Best bounded experiment. Native widget/window and audio APIs are all in the same pinned package family. Wayland z-order and placement still require runtime evidence. [6.12.0 release and wheel](https://pypi.org/project/PySide6/6.12.0/), [Qt 6.12 window flags](https://doc.qt.io/qt-6.12/qt.html), [QSoundEffect](https://doc.qt.io/qt-6.12/qsoundeffect.html) |
| **Electron** | Electron 45.0.0 was the stable release on 2026-10-21, released the day before; it bundles Node.js 24.22.0. | Easy to reuse HTML/CSS, but the documented `showInactive()`, always-on-top, top movement, and position APIs are unsupported on Wayland. This misses the no-focus, placed stack target on a likely Ubuntu desktop session. Electron's Chromium and Node runtime also make it a poorer disposable native-window test. Do not infer comparative memory numbers without measuring equivalent builds. [Electron stable release list](https://releases.electronjs.org/), [BrowserWindow API](https://www.electronjs.org/docs/latest/api/browser-window) |

No resource benchmark was run. Compare cold start and idle resident memory only if resource data is needed to choose a production framework. Electron brings Chromium and Node; PySide installs Qt native libraries, bindings, and Shiboken in the environment; Avalonia uses the .NET desktop runtime. Those facts do not substitute for measurements of equivalent alert workloads.

## Prototype checks and evidence boundary

Run the same minimal event on macOS 26 arm64, Ubuntu under X11, Ubuntu under Wayland, and WSL2 with WSLg. Record: whether the previously active app keeps focus; alert visibility, position, topmost behavior, and click-through; click-to-focus; Tab/Shift+Tab and keyboard shortcuts; WAV audible output, perceived loudness, mute/volume changes, no-device behavior, and load/play errors; repeated CLI event delivery to one process; and clean explicit quit/reopen behavior. Also try a Windows-native `.exe` from WSL2 if WSLg does not provide the desired Windows desktop focus/stack semantics.

**Not runtime proof:** The host inventory supplied for this research is macOS 26 arm64 with .NET SDK 10.0.401, Node 24, Python 3.14, and no Cargo. A `dotnet new list avalonia` observation showed no Avalonia templates and printed a first-run ASP.NET HTTPS development-certificate notice. That text alone does not prove the certificate was installed or that any system certificate state changed. No toolkit was installed and no prototype was launched in this research task. Window focus, sound, and resource behavior remain unverified.
