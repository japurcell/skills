import unittest

from commands import dispatch
from intake import caption, lookup
from labels import display


class Contract(unittest.TestCase):
    def test_lookup(self):
        self.assertEqual(lookup("  Straße "), "strasse")
        self.assertEqual(lookup("  "), "")

    def test_labels(self):
        self.assertEqual(display("  "), "(blank)")
        self.assertEqual(caption("  "), "(untitled)")
        self.assertEqual(caption(" Name "), "Name")

    def test_registered_command(self):
        for attempt, expected in [(-1, False), (0, True), (2, True), (3, False)]:
            with self.subTest(attempt=attempt):
                self.assertEqual(dispatch("retry", attempt), expected)


if __name__ == "__main__":
    unittest.main()
