import os
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

import native_alerts
from PySide6.QtCore import Qt
from PySide6.QtNetwork import QLocalServer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QCheckBox, QPushButton, QSlider


class AlertKeyboardFocusTests(unittest.TestCase):
    def test_every_enabled_control_shows_a_visible_keyboard_focus_cue(self):
        state_dir = Path(__file__).parent / f".focus-state-{os.getpid()}"
        state_dir.mkdir(mode=0o700)
        self.addCleanup(shutil.rmtree, state_dir, ignore_errors=True)
        native_alerts.save_state(
            state_dir,
            {
                "events": [
                    {
                        "id": "focus-test",
                        "kind": "success",
                        "time": 0,
                        "agent": "Test",
                        "repo": "demo",
                        "summary": "Focus test alert",
                    }
                ],
                "paused": False,
                "muted": False,
                "volume": 0.25,
            },
        )

        invisible_cues = []

        def inspect_window(application):
            windows = [
                window
                for window in application.topLevelWidgets()
                if window.windowTitle() == "Agent Alert Prototype"
            ]
            self.assertEqual(len(windows), 1)
            window = windows[0]
            window.show()
            window.activateWindow()
            application.processEvents()
            controls = (
                window.findChildren(QPushButton)
                + window.findChildren(QCheckBox)
                + window.findChildren(QSlider)
            )
            visible_controls = [
                control
                for control in controls
                if control.isVisible() and control.isEnabled()
            ]
            first, second = visible_controls[:2]
            if application.focusWidget():
                application.focusWidget().clearFocus()
            QTest.keyClick(window, Qt.Key.Key_Tab)
            self.assertIsNotNone(application.focusWidget(), "Tab must enter the control chain")
            self.assertIs(application.focusWidget(), first)
            QTest.keyClick(first, Qt.Key.Key_Tab)
            self.assertIs(application.focusWidget(), second)
            QTest.keyClick(second, Qt.Key.Key_Tab, Qt.KeyboardModifier.ShiftModifier)
            self.assertIs(application.focusWidget(), first)

            preview = next(
                button
                for button in window.findChildren(QPushButton)
                if button.text() == "Preview success"
            )
            activated = []
            preview.clicked.connect(lambda checked=False: activated.append(True))
            visited = {first}
            for _ in range(len(visible_controls) - 1):
                QTest.keyClick(application.focusWidget(), Qt.Key.Key_Tab)
                visited.add(application.focusWidget())
            self.assertEqual(visited, set(visible_controls))
            for _ in range(len(visible_controls)):
                if application.focusWidget() is preview:
                    break
                QTest.keyClick(application.focusWidget(), Qt.Key.Key_Tab)
            self.assertIs(application.focusWidget(), preview)
            QTest.keyClick(preview, Qt.Key.Key_Space)
            self.assertEqual(activated, [True])

            for control in controls:
                if not control.isVisible() or not control.isEnabled():
                    continue
                control.setFocus(Qt.FocusReason.TabFocusReason)
                application.processEvents()
                self.assertTrue(control.hasFocus(), control.accessibleName() or control.text())
                focused = control.grab().toImage()
                control.clearFocus()
                application.processEvents()
                unfocused = control.grab().toImage()
                if focused == unfocused:
                    invisible_cues.append(control.accessibleName() or control.text())
            return 0

        failures = []

        def inspect_and_cleanup(application):
            try:
                return inspect_window(application)
            except Exception:
                failures.append(sys.exc_info())
                return 0

        with (
            patch.object(QLocalServer, "removeServer", return_value=True),
            patch.object(QLocalServer, "listen", return_value=True),
            patch.object(QApplication, "exec", new=inspect_and_cleanup),
        ):
            result = native_alerts.serve(
                state_dir, force_show=True, audio_backend="media"
            )

        if failures:
            _, error, traceback = failures[0]
            raise error.with_traceback(traceback)
        self.assertEqual(result, 0)
        self.assertEqual(
            invisible_cues,
            [],
            "enabled controls need a visible keyboard focus cue: "
            + ", ".join(invisible_cues),
        )


if __name__ == "__main__":
    unittest.main()
