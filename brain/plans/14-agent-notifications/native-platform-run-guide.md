# Run the native alert prototype

- Extract [the source bundle](../../../../../../visualizations/2026/10/22/01a16214-d358-76a3-b29a-244a36c7786e/native-alert-prototype.zip) into a writable user folder. Keep separate extracted copies for Windows and Linux; virtual environments are not portable.
- Requires existing user-accessible Python 3.10+, a graphical desktop, and an audio output. First launch downloads pinned binary Qt wheels from PyPI into `.venv`. No admin, sudo, global package install, PowerShell execution-policy change, or login registration is performed.
- If Python, package downloads, or required Linux shared libraries are unavailable under corporate policy, stop and report the prerequisite. Do not bypass policy or install system packages.

## Windows

From Command Prompt in the extracted folder:

```bat
run.cmd open
run.cmd send success --agent Codex --repo skills --summary "Windows native popup"
run.cmd send failure --agent Copilot --repo demo --summary "Failure sound check"
run.cmd status
run.cmd stop
```

`run.cmd` uses the existing `py -3` launcher to create a user-local virtual environment. A source kit is supplied, not a standalone signed `.exe`; Windows packaging and live execution remain unverified.

## Ubuntu desktop / macOS / WSLg

From a terminal in the extracted folder:

```sh
sh run.sh open
sh run.sh send success --agent Codex --repo skills --summary 'Native popup'
sh run.sh send failure --agent Gemini --repo demo --summary 'Failure sound check'
sh run.sh status
sh run.sh stop
```

On Ubuntu, record the release and whether the session is GNOME/X11 or Wayland. A compositor may ignore requested placement/topmost behavior. Missing xcb/Wayland/audio libraries must be reported rather than addressed with admin commands.

On WSL2, the Linux route requires WSLg GUI/audio already available. Headless WSL2 cannot display a popup on its own. WSLg runtime behavior is still unverified here.

## WSL2 to a Windows-host popup

Extract the kit to a Windows user folder and use Windows Python, not Linux Python. From WSL, invoke the Windows launcher through interoperability; substitute your actual Windows path:

```sh
powershell.exe -NoProfile -Command "& 'C:\Users\YOUR_NAME\Downloads\native-alert-prototype\run.cmd' send success --agent Codex --repo skills --summary 'Local WSL2 event'"
```

This uses a local Windows process and its local IPC endpoint. It requires existing Windows interoperability and Windows Python; it is not remote delivery and changes no PowerShell execution policy. Do not run Windows and Linux receivers against the same extracted data folder.

## Checks to report from each real desktop

- Does a new alert appear while another app keeps focus? Can you intentionally click and Tab through controls? Is it visible in full-screen and across monitors?
- Are success/failure sounds gentle and distinct? Check Replay, mute, sound level, and output-device changes. No sound is synthesized as an abrupt beep fallback.
- Do repeated sends keep the same PID? Does Snooze cycle? Do Dismiss/Dismiss all delete, with Undo restoring the latest deletion?
- Quit should exit without error. A later send should report queued/running false. Open should restore pending alerts without replaying sound.
- Report exact OS/session, visible result, audible result, and command error if any. Build/import success is not native desktop acceptance.
