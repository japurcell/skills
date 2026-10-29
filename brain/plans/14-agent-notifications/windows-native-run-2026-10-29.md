# Windows native desktop run (2026-10-29)

- Scope: run the existing prototype on this Windows desktop only. No system install, login registration, real hooks, or remote delivery.
- Source: `prototypes/agent-notifications/`; Python 3.14.7 and the pinned PySide6 6.12.0 wheels restored in the source kit's local `.venv`.
- All runtime state and logs stayed outside the repository in `C:\Users\jeffreypurcell\.copilot\session-state\527b7ff6-948d-4594-9e39-1cbe9b154ee9\files\PROTOTYPE-windows-20261029\`. Receivers were stopped cleanly. The lifecycle sequence ended with three paused test alerts; later audio checks left one paused success test event at volume 0.50.

## Runtime and UI evidence

- One receiver PID served open, success/failure sends, and status. Status reported `platform=windows`, `window_visible=true`, all QSoundEffects `Ready`, and playback counts. CLI success/failure deliveries were acknowledged.
- Stop persisted two alerts; a stopped/offline `approval` send queued a third; reopen used one new PID and restored all three without autoplay. Final stop reported `running=false`, `paused=true`, `pending=3`; runtime log contained both `event-loop-stopped` and `objects-destroyed`.
- User-provided `windows-cutoff-buttons.png` showed empty-stack disabled action labels hard to read. The final change in `native_alerts.py` gives buttons a 40px minimum height and system-palette disabled styling. The user manually confirmed populated and empty labels fit, disabled buttons look disabled, and clicks do nothing.
- `py_compile` and `pip check` passed against the local Windows virtual environment. The user-approved GUI seam was tested manually; no audio backend code was changed.

## Audio comparison

- User could not hear QSoundEffect Preview/Replay even at its maximum configured volume (0.50); Qt status/playback signals continued to indicate readiness and playback.
- The same `sounds/success.wav` was audible to the user through Python `winsound.PlaySound` at original, 0.50, and 0.25 sample gain.
- A minimal Qt `QMediaPlayer` + `QAudioOutput` test of the same WAV at volume 0.25 emitted Playing/Stopped and was audible to the user.
- This isolates the observable difference to the QSoundEffect path or its integration, but does not establish a lower-level cause. The user later accepted the Windows media-backend revision; its integrated listening results are recorded below. Do not equate playback signals with audible success.
- Official API references used: [Qt 6.12 QMediaPlayer](https://doc.qt.io/qt-6.12/qmediaplayer.html), [Qt 6.12 QAudioOutput](https://doc.qt.io/qt-6.12/qaudiooutput.html), [Python 3.14 winsound](https://docs.python.org/3.14/library/winsound.html).

## Integrated Windows media-backend check (2026-10-29)

- Source revision: `ad4cc6da`; Windows, PySide6 6.12.0, fresh isolated state under `%TEMP%\agent-alert-prototype-windows-media-20261029-082619`. PID 45084 served the first run with `audio_backend=media`, visible window, available output, and all sources Ready.
- The user heard separate automatic success and failure sounds, each Preview button, and repeated Replay. They reported the sounds distinct and gentle, confirmed the level slider changed volume, and confirmed a new automatic failure was audible after unmuting. Manual Preview/Replay remained audible while mute was checked, as intended.
- Automatic mute is not fully accepted: the user could not tell whether the test event while muted was silent. The receiver's `audio_play_count` remained 13 during that event. A subsequent unmuted event increased it from 14 to 15 and the user heard it.
- User confirmed the alert did not take focus when another app was focused. Stop persisted one alert; an offline `approval` send queued a second; reopen on PID 26388 restored both silently (`audio_play_count=0`, backend `media`). The user clicked Replay and Quit during playback; the window closed cleanly. Final status was `running=false`, `paused=true`, `pending=2`; log includes `event-loop-stopped` and `objects-destroyed`.
- Isolated `runtime.log` and `pending.json` are under `%TEMP%\agent-alert-prototype-windows-media-20261029-082619\`. No receiver remains active. This run does not establish automatic-mute audibility, no-device handling, full keyboard behavior, or WSLg/Ubuntu support.

## Repeat and recovery

- From `prototypes\agent-notifications` in PowerShell, pass the isolated data path on every command:

  ```powershell
  $data = 'C:\Users\jeffreypurcell\.copilot\session-state\527b7ff6-948d-4594-9e39-1cbe9b154ee9\files\PROTOTYPE-windows-20261029'
  & .\run.cmd status --data-dir $data
  & .\run.cmd open --data-dir $data
  & .\run.cmd send success --agent Test --repo Windows --summary 'Audio check' --data-dir $data
  & .\run.cmd stop --data-dir $data
  ```

- Direct WAV control from the same directory: `.venv\Scripts\python.exe -c "import winsound,sys; winsound.PlaySound(sys.argv[1], winsound.SND_FILENAME)" sounds\success.wav`.
- QMediaPlayer comparison from PowerShell in the same directory: `& .\.venv\Scripts\python.exe -c 'import sys; from PySide6.QtCore import QCoreApplication,QTimer,QUrl; from PySide6.QtMultimedia import QMediaPlayer,QAudioOutput; app=QCoreApplication([]); output=QAudioOutput(); output.setVolume(0.25); player=QMediaPlayer(); player.setAudioOutput(output); player.errorOccurred.connect(lambda *args: print(args)); player.playbackStateChanged.connect(lambda state: print(state)); player.setSource(QUrl.fromLocalFile(sys.argv[1])); player.play(); QTimer.singleShot(2200,app.quit); app.exec()' "$PWD\sounds\success.wav"`.
- Listening is required for acceptance. Do not equate playback signals with audible output.
- The two screenshots under `prototypes/agent-notifications/` were supplied by the user and included in the Windows findings commit `574e2045`.
