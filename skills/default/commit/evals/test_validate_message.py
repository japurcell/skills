#!/usr/bin/env python3
"""Exercise the bundled commit-message checker through its public CLI."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_message.py"
COPILOT = "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
MESSAGE = """fix: preserve inherited dispatch

Summary:
- Support permitted host defaults.

Rationale:
- Model overrides may be forbidden.

Tests:
- Run focused dispatch scenarios.

""" + COPILOT + "\n"


class MessageCliTests(unittest.TestCase):
    def check_message(self, message, *options):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "message.txt"
            path.write_bytes(message.encode("utf-8"))
            return subprocess.run(
                [sys.executable, str(SCRIPT), str(path), *options],
                capture_output=True, text=True, check=False, timeout=5,
            )

    def test_valid_message(self):
        result = self.check_message(MESSAGE, "--co-author", COPILOT.removeprefix("Co-authored-by: "))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Commit message valid.\n")
        self.assertEqual(result.stderr, "")

    def test_valid_message_without_attribution(self):
        result = self.check_message(MESSAGE.replace(COPILOT, ""))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_only_git_line_endings_form_message_structure(self):
        message = MESSAGE.replace(COPILOT, "")
        for separator, expected in (
            ("\n", 0), ("\r\n", 0),
            ("\r", 1), ("\v", 1), ("\f", 1),
            ("\x1c", 1), ("\x1d", 1), ("\x1e", 1),
            ("\x85", 1), ("\u2028", 1), ("\u2029", 1),
        ):
            with self.subTest(separator=repr(separator)):
                result = self.check_message(message.replace("\n", separator))
                self.assertEqual(result.returncode, expected, result.stderr)

    def test_only_established_contributors_are_attributed(self):
        person = "Person <person@example.com>"
        message = MESSAGE.replace(COPILOT, "Co-authored-by: " + person)
        result = self.check_message(message, "--co-author", person)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.check_message(message)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("--co-author", result.stderr)
        result = self.check_message(MESSAGE)
        self.assertEqual(result.returncode, 1, result.stderr)

    def test_each_supplied_coauthor_is_required_exactly_once(self):
        person = "Person <person@example.com>"
        expected = ("--co-author", person)
        absent = self.check_message(MESSAGE.replace(COPILOT, ""), *expected)
        self.assertEqual(absent.returncode, 1, absent.stderr)
        self.assertIn("missing required co-author", absent.stderr)

        present = self.check_message(
            MESSAGE.replace(COPILOT, "Co-authored-by: " + person), *expected,
        )
        self.assertEqual(present.returncode, 0, present.stderr)

        duplicate = self.check_message(
            MESSAGE.replace(COPILOT, "Co-authored-by: " + person + "\nCo-authored-by: " + person),
            *expected,
        )
        self.assertEqual(duplicate.returncode, 1, duplicate.stderr)

    def test_rejects_malformed_body(self):
        cases = (
            "", MESSAGE.replace("\n", r"\n"),
            MESSAGE.replace("Rationale:\n- Model overrides may be forbidden.\n\n", ""),
            MESSAGE.replace("- Support permitted host defaults.", "- "),
            MESSAGE.replace("fix: preserve inherited dispatch", "update stuff"),
            MESSAGE.replace("fix: preserve inherited dispatch", "fix: " + "x" * 70),
            MESSAGE.replace("fix: preserve inherited dispatch", "fix: preserve inherited dispatch."),
            MESSAGE.replace("\n\nSummary:", "\nSummary:"),
        )
        for message in cases:
            with self.subTest(message=message):
                result = self.check_message(message, "--co-author", COPILOT.removeprefix("Co-authored-by: "))
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("Invalid commit message", result.stderr)

    def test_default_subject_types_scope_and_length_boundary(self):
        for subject, expected in (
            *((f"{kind}: update changed files", 0) for kind in (
                "docs", "test", "fix", "feat", "refactor", "perf", "chore",
            )),
            ("fix(parser): preserve newlines", 0),
            ("fix: " + "x" * 67, 0),
            ("fix: " + "x" * 68, 1),
            ("unknown: update changed files", 1),
            ("fix(): preserve newlines", 1),
        ):
            with self.subTest(subject=subject):
                message = MESSAGE.replace(COPILOT, "").replace("fix: preserve inherited dispatch", subject)
                result = self.check_message(message)
                self.assertEqual(result.returncode, expected, result.stderr)

    def test_wrapped_bullets_and_literal_backslashes_use_real_message_newlines(self):
        message = MESSAGE.replace(COPILOT, "").replace(
            "- Run focused dispatch scenarios.",
            '- Run `printf "first\\nsecond\\n"`.\n  Confirm both output lines.',
        )
        result = self.check_message(message)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_trailer_authorization_and_layout(self):
        cases = (
            (MESSAGE.replace(COPILOT, ""), (), 1),
            (MESSAGE.replace(COPILOT, "Refs #123\n" + COPILOT), (), 1),
            (MESSAGE.replace(COPILOT, "Refs #123\n" + COPILOT), ("--issue", "123"), 0),
            (MESSAGE.replace(COPILOT, "Fixes #123\n" + COPILOT), ("--issue", "123"), 1),
            (MESSAGE.replace(COPILOT, "Fixes #123\n" + COPILOT), ("--issue", "123", "--fixes", "123"), 0),
            (MESSAGE.replace(COPILOT, "Fixes #123\n" + COPILOT), ("--fixes", "123"), 1),
            (MESSAGE.replace(COPILOT, "Refs #123\n\n" + COPILOT), ("--issue", "123"), 1),
            (MESSAGE + "Co-authored-by: Person <not-an-email>\n", (), 1),
            (MESSAGE + "Co-authored-by: Person <person@example.com>\n", ("--co-author", "Person <person@example.com>"), 0),
            (MESSAGE + "Unknown: trailer\n", (), 1),
            (MESSAGE.replace(COPILOT, "Session: observed-session\n\n" + COPILOT), (), 0),
            (MESSAGE.replace(COPILOT, "Session: observed-session"), (), 1),
            (MESSAGE + COPILOT + "\n", (), 1),
            (MESSAGE + "Session: observed-session\n", (), 1),
            (MESSAGE.replace(COPILOT, "Session: first\nSession: second"), (), 1),
        )
        for message, options, expected in cases:
            with self.subTest(message=message, options=options):
                result = self.check_message(message, "--co-author", COPILOT.removeprefix("Co-authored-by: "), *options)
                self.assertEqual(result.returncode, expected, result.stderr)

    def test_issue_closing_requires_intent_for_each_specific_issue(self):
        message = MESSAGE.replace(COPILOT, "Fixes #123\nFixes #456")
        result = self.check_message(message, "--issue", "123", "--issue", "456", "--fixes", "123")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("--fixes 456", result.stderr)
        result = self.check_message(message, "--issue", "#123", "--issue", "456", "--fixes", "#123", "--fixes", "456")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_issue_trailers_are_deduplicated_in_input_order(self):
        options = ("--issue", "#456", "--issue", "123", "--issue", "456")
        for trailers, expected in (
            ("Refs #456\nRefs #123", 0),
            ("Refs #456\nRefs #456", 1),
            ("Refs #123\nRefs #456", 1),
        ):
            with self.subTest(trailers=trailers):
                result = self.check_message(MESSAGE.replace(COPILOT, trailers), *options)
                self.assertEqual(result.returncode, expected, result.stderr)

    def test_missing_file_is_an_input_error(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(Path(directory) / "missing.txt")],
                capture_output=True, text=True, check=False, timeout=5,
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("Cannot read message", result.stderr)

    def test_non_utf8_file_is_an_input_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "message.txt"
            path.write_bytes(b"\xff")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True, text=True, check=False, timeout=5,
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("Cannot read message", result.stderr)

    def test_invalid_issue_options_are_usage_errors(self):
        for option in ("--issue", "--fixes"):
            for value in ("", "#", "0", "-1", "abc", "12x"):
                with self.subTest(option=option, value=value):
                    result = self.check_message(MESSAGE, option, value)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertIn("positive issue number", result.stderr)


if __name__ == "__main__":
    unittest.main()
