"""Disposable native popup/audio experiment. No real hooks or login items installed."""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import time
import uuid
import wave

from PySide6.QtCore import QCoreApplication, QLockFile, QTimer, Qt, QUrl
from PySide6.QtNetwork import QLocalServer, QLocalSocket

ROOT = Path(__file__).resolve().parent
KINDS = ("success", "failure", "input", "approval", "cancelled", "stall", "unknown")
TITLES = {"success": "Completed successfully", "failure": "Failure reported",
          "input": "Input needed", "approval": "Approval needed", "cancelled": "Work cancelled",
          "stall": "Stall reported by producer", "unknown": "Turn ended"}
MAX_FRAME = 8192
MAX_PENDING = 500


def load_state(directory):
    path = directory / "pending.json"
    if not path.exists():
        return {"events": [], "paused": False, "muted": False, "volume": 0.25}
    state = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(state.get("events"), list) or len(state["events"]) > MAX_PENDING:
        raise ValueError("Invalid prototype pending store; preserve it for inspection")
    return state


def save_state(directory, state):
    with tempfile.NamedTemporaryFile(mode="w", dir=directory, prefix="pending-", suffix=".tmp",
                                     delete=False, encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False)
        handle.flush()
        os.fsync(handle.fileno())
        temporary = handle.name
    os.replace(temporary, directory / "pending.json")


def locked(directory, name, timeout=3000):
    lock = QLockFile(str(directory / name))
    if not lock.tryLock(timeout):
        raise RuntimeError("Prototype state is busy; retry the command")
    return lock


def event_from_request(request):
    kind = request.get("kind", "unknown")
    if kind not in KINDS:
        raise ValueError("Unsupported alert type")
    event = {"id": str(uuid.uuid4()), "kind": kind, "time": time.time()}
    for field, default, limit in (("agent", "Demo agent", 80), ("repo", "demo-repository", 160),
                                  ("summary", "A local prototype event arrived.", 500)):
        value = request.get(field, default)
        if not isinstance(value, str) or len(value) > limit or any(ord(c) < 32 for c in value):
            raise ValueError("Invalid " + field + "; use bounded single-line text")
        event[field] = value
    return event


def make_sounds():
    sounds = ROOT / "sounds"
    sounds.mkdir(exist_ok=True)
    motifs = {"success": [523.25, 659.25, 783.99], "failure": [392.00, 349.23, 293.66],
              "attention": [587.33, 659.25]}
    rate = 44100
    for name, notes in motifs.items():
        path = sounds / (name + ".wav")
        if path.exists():
            continue
        frames = bytearray()
        for sample in range(int(rate * 1.1)):
            t = sample / rate
            value = 0.0
            for index, frequency in enumerate(notes):
                age = t - index * 0.19
                if 0 <= age < 0.65:
                    envelope = math.sin(math.pi * age / 0.65) ** 2
                    value += 0.035 * envelope * math.sin(2 * math.pi * frequency * age)
            frames.extend(struct.pack("<h", round(max(-0.12, min(0.12, value)) * 32767)))
        with wave.open(str(path), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(rate)
            audio.writeframes(frames)


def server_name(directory):
    name = "agent-alert-prototype-" + hashlib.sha256(str(directory).encode()).hexdigest()[:20]
    if os.name == "nt":
        return name
    # macOS ignores Qt's Unix socket permission flags. Protect the parent directory.
    private = Path("/tmp") / (name + "-" + str(os.getuid()))
    if private.is_symlink():
        raise RuntimeError("Unsafe prototype socket directory")
    private.mkdir(mode=0o700, exist_ok=True)
    if private.stat().st_uid != os.getuid():
        raise RuntimeError("Prototype socket directory belongs to another user")
    private.chmod(0o700)
    return str(private / "receiver.sock")


def rpc(directory, request, timeout=500):
    socket = QLocalSocket()
    socket.connectToServer(server_name(directory))
    if not socket.waitForConnected(timeout):
        return None
    socket.write(json.dumps(request).encode() + b"\n")
    socket.flush()
    if not socket.waitForReadyRead(3000):
        raise RuntimeError("Prototype receiver did not acknowledge the event")
    response = json.loads(bytes(socket.readLine()))
    socket.disconnectFromServer()
    return response


def client(directory, request, audio_backend="auto"):
    response = rpc(directory, request)
    if response is not None:
        return response
    launch_lock = locked(directory, "launch.lock", 10000)
    try:
        response = rpc(directory, request)
        if response is not None:
            return response
        state_lock = locked(directory, "state.lock")
        try:
            state = load_state(directory)
            if request["command"] == "status":
                return {"ok": True, "running": False, "paused": state["paused"],
                        "pending": len(state["events"])}
            if request["command"] == "stop":
                state["paused"] = True
                save_state(directory, state)
                return {"ok": True, "running": False, "paused": True}
            if request["command"] == "send" and state["paused"]:
                if len(state["events"]) >= MAX_PENDING:
                    raise ValueError("Prototype queue full (500); reopen and review alerts")
                state["events"].append(event_from_request(request))
                save_state(directory, state)
                return {"ok": True, "queued": True, "running": False,
                        "pending": len(state["events"])}
        finally:
            state_lock.unlock()
        with (directory / "runtime.log").open("ab") as log:
            subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "serve", "--data-dir",
                              str(directory), "--audio-backend", audio_backend],
                             stdout=log, stderr=log, start_new_session=True)
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            response = rpc(directory, request, 150)
            if response is not None:
                return response
            time.sleep(0.08)
        raise RuntimeError("Native receiver did not start; inspect prototype runtime.log")
    finally:
        launch_lock.unlock()


def serve(directory, force_show=False, audio_backend="auto"):
    from PySide6.QtGui import QFont, QShortcut, QKeySequence
    from PySide6.QtMultimedia import QAudioOutput, QMediaDevices, QMediaPlayer, QSoundEffect
    from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QHBoxLayout, QLabel,
                                   QPushButton, QSlider, QVBoxLayout, QWidget)

    app = QApplication(sys.argv[:1])
    app.setApplicationName("Agent Alert Prototype")
    app.setQuitOnLastWindowClosed(False)
    if audio_backend == "auto":
        audio_backend = "media" if sys.platform == "win32" else "soundeffect"
    instance = QLockFile(str(directory / "instance.lock"))
    if not instance.tryLock(0):
        return 0

    class AlertWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.state = load_state(directory)
            self.undo_batch = None
            self.undo_deadline = 0.0
            self.started = time.monotonic()
            self.play_count = 0
            self.sound_queue = []
            self.sockets = set()
            self.setWindowTitle("Agent Alert Prototype")
            self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
            self.setMinimumWidth(410)
            self.setMaximumWidth(510)
            self.setFont(QFont("", 11))
            self.setStyleSheet("QWidget {font-size:14px;} QPushButton {padding:8px 12px;min-height:40px;} "
                               "QPushButton:disabled {color:palette(text);background-color:palette(window);"
                               "border:1px solid palette(mid);border-radius:4px;} "
                               "QLabel#title {font-size:22px;font-weight:600;} "
                               "QFrame#card {border:1px solid palette(mid);border-radius:10px;} "
                               "QLabel#muted {color:palette(mid);}")
            root = QVBoxLayout(self)
            root.setContentsMargins(22, 18, 22, 18)
            root.setSpacing(14)
            heading = QHBoxLayout()
            heading.addWidget(QLabel("Native alert experiment"), 1)
            self.count = QLabel()
            heading.addWidget(self.count)
            root.addLayout(heading)
            self.next_label = QLabel()
            root.addWidget(self.next_label)
            card = QFrame()
            card.setObjectName("card")
            body = QVBoxLayout(card)
            body.setContentsMargins(18, 18, 18, 18)
            body.setSpacing(12)
            self.title = QLabel()
            self.title.setObjectName("title")
            self.title.setWordWrap(True)
            self.context = QLabel()
            self.context.setWordWrap(True)
            self.summary = QLabel()
            self.summary.setWordWrap(True)
            for label in (self.title, self.context, self.summary, self.next_label):
                label.setTextFormat(Qt.TextFormat.PlainText)
            body.addWidget(self.title)
            body.addWidget(self.context)
            body.addWidget(self.summary)
            row = QHBoxLayout()
            self.snooze_button = QPushButton("Snooze")
            self.snooze_button.clicked.connect(self.snooze)
            self.dismiss_button = QPushButton("Dismiss")
            self.dismiss_button.clicked.connect(lambda: self.dismiss(False))
            self.replay_button = QPushButton("Replay sound")
            self.replay_button.clicked.connect(lambda: self.play(self.front_kind(), manual=True))
            for button in (self.snooze_button, self.dismiss_button, self.replay_button):
                row.addWidget(button)
            body.addLayout(row)
            root.addWidget(card)
            row = QHBoxLayout()
            self.dismiss_all = QPushButton("Dismiss all")
            self.dismiss_all.clicked.connect(lambda: self.dismiss(True))
            self.undo_button = QPushButton("Undo (10s)")
            self.undo_button.clicked.connect(self.undo)
            row.addWidget(self.dismiss_all)
            row.addWidget(self.undo_button)
            root.addLayout(row)
            self.mute = QCheckBox("Mute automatic sounds")
            self.mute.setChecked(self.state.get("muted", False))
            self.mute.toggled.connect(self.mute_changed)
            root.addWidget(self.mute)
            row = QHBoxLayout()
            row.addWidget(QLabel("Sound level"))
            self.volume = QSlider(Qt.Orientation.Horizontal)
            self.volume.setRange(0, 50)
            self.volume.setValue(round(self.state.get("volume", 0.25) * 100))
            self.volume.setAccessibleName("Prototype sound level")
            self.volume.valueChanged.connect(self.volume_changed)
            row.addWidget(self.volume)
            root.addLayout(row)
            row = QHBoxLayout()
            preview_buttons = []
            for kind in ("success", "failure", "approval"):
                button = QPushButton("Preview " + ("attention" if kind == "approval" else kind))
                button.clicked.connect(lambda checked=False, k=kind: self.play(k, manual=True))
                preview_buttons.append(button)
                row.addWidget(button)
            root.addLayout(row)
            for button in preview_buttons:
                button.setMinimumWidth(button.sizeHint().width())
            self.audio_status = QLabel("Audio: loading gentle WAVs")
            self.audio_status.setWordWrap(True)
            root.addWidget(self.audio_status)
            self.status_label = QLabel("Disposable prototype. No history, hooks, or login items.")
            self.status_label.setWordWrap(True)
            root.addWidget(self.status_label)
            row = QHBoxLayout()
            close = QPushButton("Quit prototype")
            close.clicked.connect(self.quit_prototype)
            row.addStretch()
            row.addWidget(close)
            root.addLayout(row)
            self.effects = {}
            self.outputs = {}
            self.pending_play = None
            for kind in ("success", "failure", "attention"):
                if audio_backend == "media":
                    effect = QMediaPlayer(self)
                    output = QAudioOutput(self)
                    output.setVolume(self.state.get("volume", 0.25))
                    effect.setAudioOutput(output)
                    self.outputs[kind] = output
                    effect.mediaStatusChanged.connect(lambda status, k=kind: self.audio_changed(k))
                    effect.errorOccurred.connect(lambda error, message, k=kind: self.audio_changed(k))
                else:
                    effect = QSoundEffect(self)
                    effect.setLoopCount(1)
                    effect.setVolume(self.state.get("volume", 0.25))
                    effect.statusChanged.connect(lambda k=kind: self.audio_changed(k))
                effect.playingChanged.connect(lambda *args, k=kind: self.playing_changed(k))
                self.effects[kind] = effect
                effect.setSource(QUrl.fromLocalFile(str(ROOT / "sounds" / (kind + ".wav"))))
            self.devices = QMediaDevices(self)
            self.devices.audioOutputsChanged.connect(lambda: self.audio_changed("attention"))
            self.sound_timer = QTimer(self)
            self.sound_timer.setSingleShot(True)
            self.sound_timer.timeout.connect(self.flush_sound)
            self.undo_timer = QTimer(self)
            self.undo_timer.setInterval(100)
            self.undo_timer.timeout.connect(self.expire_undo)
            self.undo_timer.start()
            QShortcut(QKeySequence("Ctrl+Z"), self, activated=self.undo)
            self.server = QLocalServer(self)
            self.server.setSocketOptions(QLocalServer.SocketOption.UserAccessOption)
            QLocalServer.removeServer(server_name(directory))
            if not self.server.listen(server_name(directory)):
                raise RuntimeError("Unable to listen on local prototype socket")
            self.server.newConnection.connect(self.connect_client)
            self.render()
            self.setMaximumWidth(max(self.maximumWidth(), self.minimumSizeHint().width()))
            self.position_popup()

        def persist(self):
            lock = locked(directory, "state.lock")
            try:
                save_state(directory, self.state)
            finally:
                lock.unlock()

        def position_popup(self):
            screen = app.primaryScreen().availableGeometry()
            self.adjustSize()
            self.move(screen.right() - self.width() - 24, screen.bottom() - self.height() - 24)

        def front_kind(self):
            return self.state["events"][0]["kind"] if self.state["events"] else "unknown"

        def render(self):
            events = self.state["events"]
            self.count.setText(str(len(events)) + " pending")
            self.title.setText(TITLES[events[0]["kind"]] if events else "Stack clear")
            self.context.setText(events[0]["agent"] + " / " + events[0]["repo"] if events else "Ready for the next local event")
            self.summary.setText(events[0]["summary"] if events else "Dismiss deletes. Undo is briefly available; no alert history is kept.")
            self.next_label.setText("Next: " + events[1]["agent"] + " / " + TITLES[events[1]["kind"]] if len(events) > 1 else "No automatic dismissal")
            for button in (self.snooze_button, self.dismiss_button, self.replay_button, self.dismiss_all):
                button.setEnabled(bool(events))
            self.undo_button.setVisible(self.undo_batch is not None)

        def snooze(self):
            if self.state["events"]:
                self.state["events"].append(self.state["events"].pop(0))
                self.persist()
                self.render()
                self.snooze_button.setFocus()

        def dismiss(self, all_alerts):
            events = self.state["events"]
            if not events:
                return
            self.undo_batch = events[:] if all_alerts else events[:1]
            self.undo_deadline = time.monotonic() + 10
            self.state["events"] = [] if all_alerts else events[1:]
            self.persist()
            self.render()
            self.undo_button.setFocus()

        def undo(self):
            if self.undo_batch is not None and time.monotonic() < self.undo_deadline:
                self.state["events"] = self.undo_batch + self.state["events"]
                self.undo_batch = None
                self.persist()
                self.render()
                self.snooze_button.setFocus()

        def expire_undo(self):
            if self.undo_batch is not None and time.monotonic() >= self.undo_deadline:
                self.undo_batch = None
                self.render()

        def mute_changed(self, muted):
            self.state["muted"] = muted
            self.persist()
            if muted:
                self.pending_play = None
                self.sound_queue.clear()
                self.sound_timer.stop()
                for effect in self.effects.values():
                    effect.stop()

        def volume_changed(self, value):
            self.state["volume"] = value / 100
            for output in (self.outputs or self.effects).values():
                output.setVolume(value / 100)
            self.persist()

        def source_status(self, kind):
            effect = self.effects[kind]
            if audio_backend == "soundeffect":
                return effect.status().name
            if effect.error() != QMediaPlayer.Error.NoError:
                return "Error"
            status = effect.mediaStatus()
            if status == QMediaPlayer.MediaStatus.InvalidMedia:
                return "Error"
            if status == QMediaPlayer.MediaStatus.StalledMedia:
                return "Stalled"
            if status in (QMediaPlayer.MediaStatus.LoadedMedia, QMediaPlayer.MediaStatus.BufferedMedia,
                          QMediaPlayer.MediaStatus.EndOfMedia):
                return "Ready"
            return "Loading"

        def audio_changed(self, kind):
            output = QMediaDevices.defaultAudioOutput()
            failed = [name for name in self.effects if self.source_status(name) == "Error"]
            if output.isNull():
                self.pending_play = None
                self.audio_status.setText("Audio unavailable: no output device. No beep fallback.")
            elif failed:
                if self.pending_play in failed:
                    self.pending_play = None
                details = [self.effects[name].errorString() for name in failed] if self.outputs else []
                self.audio_status.setText("Audio load failed: " + ", ".join(failed + details))
            else:
                self.audio_status.setText("Audio (" + audio_backend + "): " + output.description())
            print(json.dumps({"audio": kind, "backend": audio_backend, "status": self.source_status(kind),
                              "error": self.effects[kind].errorString() if self.outputs else "",
                              "output_available": not output.isNull()}), flush=True)
            if self.pending_play == kind and not output.isNull() and self.source_status(kind) == "Ready":
                self.pending_play = None
                self.effects[kind].play()

        def playing_changed(self, kind):
            if self.effects[kind].isPlaying():
                self.play_count += 1
            print(json.dumps({"audio": kind, "playing": self.effects[kind].isPlaying(),
                              "play_count": self.play_count}), flush=True)

        def play(self, kind, manual=False):
            if not manual and (self.state.get("muted") or self.state["paused"]):
                return
            self.pending_play = None
            if QMediaDevices.defaultAudioOutput().isNull():
                self.audio_status.setText("Audio unavailable: no output device. No beep fallback.")
                return
            sound = kind if kind in ("success", "failure") else "attention"
            for effect in self.effects.values():
                effect.stop()
            if self.source_status(sound) == "Loading":
                self.pending_play = sound
            elif self.source_status(sound) == "Ready":
                self.pending_play = None
                self.effects[sound].play()
            else:
                self.audio_status.setText("Audio source unavailable; inspect runtime.log")

        def flush_sound(self):
            kinds = self.sound_queue[:]
            self.sound_queue.clear()
            if kinds:
                self.play("failure" if "failure" in kinds else kinds[-1])

        def connect_client(self):
            while self.server.hasPendingConnections():
                socket = self.server.nextPendingConnection()
                self.sockets.add(socket)
                socket.setProperty("buffer", b"")
                socket.readyRead.connect(lambda s=socket: self.read_client(s))
                socket.disconnected.connect(lambda s=socket: (self.sockets.discard(s), s.deleteLater()))
                timeout = QTimer(socket)
                timeout.setSingleShot(True)
                timeout.timeout.connect(lambda s=socket: self.timeout_client(s))
                timeout.start(5000)

        def timeout_client(self, socket):
            if socket in self.sockets:
                socket.disconnectFromServer()

        def read_client(self, socket):
            data = socket.property("buffer") + bytes(socket.readAll())
            if len(data) > MAX_FRAME:
                socket.disconnectFromServer()
                return
            socket.setProperty("buffer", data)
            if b"\n" not in data:
                return
            try:
                request = json.loads(data.split(b"\n", 1)[0])
                if not isinstance(request, dict):
                    raise ValueError("Expected event object")
                response = self.handle(request)
            except (ValueError, KeyError, TypeError) as error:
                response = {"ok": False, "error": str(error)}
            socket.write(json.dumps(response).encode() + b"\n")
            socket.flush()
            socket.disconnectFromServer()

        def handle(self, request):
            command = request.get("command")
            if command == "send":
                if len(self.state["events"]) >= MAX_PENDING:
                    raise ValueError("Prototype queue full (500)")
                event = event_from_request(request)
                self.state["events"].append(event)
                self.persist()
                self.render()
                if not self.state["paused"]:
                    self.show()
                    self.sound_queue.append(event["kind"])
                    if not self.sound_timer.isActive():
                        self.sound_timer.start(150)
            elif command == "open":
                self.state["paused"] = False
                self.persist()
                self.render()
                self.show()
            elif command == "stop":
                QTimer.singleShot(100, self.quit_prototype)
            elif command != "status":
                raise ValueError("Unsupported command")
            return {"ok": True, "pid": os.getpid(), "pending": len(self.state["events"]),
                    "paused": self.state["paused"], "audio_play_count": self.play_count,
                    "window_visible": self.isVisible(), "window_active": self.isActiveWindow(),
                    "audio_backend": audio_backend,
                    "audio_status": {name: self.source_status(name) for name in self.effects},
                    "platform": app.platformName(), "uptime_seconds": round(time.monotonic() - self.started, 3)}

        def quit_prototype(self):
            self.state["paused"] = True
            self.undo_batch = None
            self.persist()
            # Exit the Qt loop first; macOS quit can terminate before Python-owned widgets are cleaned up.
            app.exit(0)

        def closeEvent(self, event):
            self.quit_prototype()
            event.accept()

    make_sounds()
    window = AlertWindow()
    if force_show:
        window.state["paused"] = False
        window.persist()
    if not window.state["paused"]:
        window.show()
    result = app.exec()
    print(json.dumps({"shutdown": "event-loop-stopped"}), flush=True)
    # Destroy Qt objects while Python's signal machinery is still alive, not at interpreter exit.
    import shiboken6
    window.undo_timer.stop()
    window.sound_timer.stop()
    window.server.close()
    for effect in window.effects.values():
        effect.stop()
        if audio_backend == "media":
            effect.mediaStatusChanged.disconnect()
            effect.errorOccurred.disconnect()
        else:
            effect.statusChanged.disconnect()
        effect.playingChanged.disconnect()
    for socket in list(window.sockets):
        socket.disconnectFromServer()
    shiboken6.delete(window)
    shiboken6.delete(app)
    print(json.dumps({"shutdown": "objects-destroyed"}), flush=True)
    instance.unlock()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("send", "open", "status", "stop", "serve", "sounds"))
    parser.add_argument("kind", nargs="?", choices=KINDS, default="unknown")
    parser.add_argument("--agent", default="Codex")
    parser.add_argument("--repo", default="skills")
    parser.add_argument("--summary", default="Native popup and gentle sound experiment.")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "PROTOTYPE-data")
    parser.add_argument("--show", action="store_true", help="Open the native window when launching its app bundle")
    parser.add_argument("--audio-backend", choices=("auto", "media", "soundeffect"), default="auto",
                        help="Receiver startup only: auto uses media on Windows, soundeffect elsewhere; stop first to change")
    args = parser.parse_args()
    directory = args.data_dir.resolve()
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    if args.command == "serve":
        return serve(directory, args.show, args.audio_backend)
    if args.command == "sounds":
        make_sounds()
        return 0
    core = QCoreApplication(sys.argv[:1])
    event_from_request(vars(args))
    start = time.monotonic()
    response = client(directory, {"command": args.command, "kind": args.kind,
                                 "agent": args.agent, "repo": args.repo, "summary": args.summary}, args.audio_backend)
    response["cli_elapsed_ms"] = round((time.monotonic() - start) * 1000, 1)
    print(json.dumps(response))
    return 0 if response.get("ok") else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print("Prototype error: " + str(error), file=sys.stderr)
        raise SystemExit(1)
