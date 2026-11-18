import tempfile
import unittest
from pathlib import Path

from guardian import restore, snapshot


class GuardianRecoveryTests(unittest.TestCase):
    def test_snapshot_and_restore_recover_original_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "policy.json"
            saved = root / "policy.snapshot"
            target.write_bytes(b'{"mode":"safe"}')
            snapshot(target, saved)
            target.write_bytes(b'{"mode":"changed"}')
            restore(saved, target)
            self.assertEqual(target.read_bytes(), b'{"mode":"safe"}')


if __name__ == "__main__":
    unittest.main()
