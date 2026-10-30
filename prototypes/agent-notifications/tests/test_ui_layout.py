import os
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

import native_alerts
from PySide6.QtNetwork import QLocalServer
from PySide6.QtWidgets import QApplication, QPushButton, QStyle, QStyleOptionButton


class AlertButtonLayoutTests(unittest.TestCase):
    def test_every_visible_button_label_fits_its_style_content_area(self):
        state_dir = Path(__file__).parent / f".layout-state-{os.getpid()}"
        state_dir.mkdir(mode=0o700)
        self.addCleanup(shutil.rmtree, state_dir, ignore_errors=True)
        native_alerts.save_state(
            state_dir,
            {
                "events": [
                    {
                        "id": "layout-test",
                        "kind": "success",
                        "time": 0,
                        "agent": "Test",
                        "repo": "demo",
                        "summary": "Layout test alert",
                    }
                ],
                "paused": False,
                "muted": False,
                "volume": 0.25,
            },
        )

        visible_buttons = []
        overflows = []

        def inspect_window(application):
            application.processEvents()
            windows = [
                window
                for window in application.topLevelWidgets()
                if window.windowTitle() == "Agent Alert Prototype"
            ]
            if len(windows) != 1:
                overflows.append(f"expected one alert window, found {len(windows)}")
                return 0

            window = windows[0]
            window.show()
            application.processEvents()
            for button in window.findChildren(QPushButton):
                if not button.isVisible():
                    continue
                visible_buttons.append(button.text())
                option = QStyleOptionButton()
                option.initFrom(button)
                option.rect = button.rect()
                content = button.style().subElementRect(
                    QStyle.SubElement.SE_PushButtonContents, option, button
                )
                text_width = button.fontMetrics().horizontalAdvance(button.text())
                if text_width > content.width():
                    overflows.append(
                        f"{button.text()!r}: text={text_width}px, "
                        f"content={content.width()}px, button={button.width()}px, "
                        f"button-hint={button.sizeHint().width()}px, "
                        f"window-min-hint={window.minimumSizeHint().width()}px, "
                        f"window-max={window.maximumWidth()}px"
                    )
            return 0

        with (
            patch.object(QLocalServer, "removeServer", return_value=True),
            patch.object(QLocalServer, "listen", return_value=True),
            patch.object(QApplication, "exec", new=inspect_window),
        ):
            result = native_alerts.serve(
                state_dir, force_show=True, audio_backend="media"
            )

        self.assertEqual(result, 0)
        self.assertTrue(
            visible_buttons, "the populated alert window should expose visible buttons"
        )
        self.assertEqual(
            overflows, [], "button labels must fit: " + "; ".join(overflows)
        )


if __name__ == "__main__":
    unittest.main()
