#!/usr/bin/env python3
"""Public-process proof checks for the bounded D0 experiment."""
import os
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class Feasibility(unittest.TestCase):
    def keep(self, name, data):
        if os.environ.get("D0_EVIDENCE"):
            directory = Path(os.environ["D0_EVIDENCE"])
            directory.mkdir(parents=True, exist_ok=True)
            (directory / (name + ".json")).write_text(json.dumps(json.loads(data), indent=2) + "\n")

    def test_incremental_sensitive_path_reuses_published_blob(self):
        script = Path(__file__).with_name("d0-probe.py")
        with tempfile.TemporaryDirectory(prefix="d0-path-proof-") as directory:
            result = subprocess.run([sys.executable, str(script), "experiment", "--source", os.environ["D0_SOURCE"], "--workspace", directory, "--case", "path-control"], capture_output=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            self.assertIn(b'"reused_blob_sensitive_path_rejected": true', result.stdout)
            self.keep("path-control", result.stdout)

    def test_large_protected_capture_scans_embedded_late_control(self):
        script = Path(__file__).with_name("d0-probe.py")
        with tempfile.TemporaryDirectory(prefix="d0-large-proof-") as directory:
            result = subprocess.run([sys.executable, str(script), "experiment", "--source", os.environ["D0_SOURCE"], "--workspace", directory, "--case", "large-control"], capture_output=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            self.assertIn(b'"embedded_late_secret_detected": true', result.stdout)
            self.keep("large-control", result.stdout)

    def test_capacity_late_control_does_not_hide_behind_repeated_blob(self):
        script = Path(__file__).with_name("d0-probe.py")
        with tempfile.TemporaryDirectory(prefix="d0-capacity-proof-") as directory:
            result = subprocess.run([sys.executable, str(script), "experiment", "--source", os.environ["D0_SOURCE"], "--workspace", directory, "--case", "capacity-control"], capture_output=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            self.assertIn(b'"late_control_detected": true', result.stdout)
            self.assertIn(b'"over_limit_incomplete": true', result.stdout)
            self.keep("capacity-control", result.stdout)

    def test_lfs_delivers_verified_snapshot_and_rejection_transfers_zero(self):
        script = Path(__file__).with_name("d0-probe.py")
        with tempfile.TemporaryDirectory(prefix="d0-lfs-proof-") as directory:
            result = subprocess.run([sys.executable, str(script), "experiment", "--source", os.environ["D0_SOURCE"], "--workspace", directory, "--case", "lfs", "--lfs", os.environ["D0_LFS"]], capture_output=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            self.assertIn(b'"delivered_snapshot_matches": true', result.stdout)
            self.assertIn(b'"rejected_payload_transfers": 0', result.stdout)
            self.assertIn(b'"scanner_dispatcher_handoff": true', result.stdout)
            self.keep("lfs", result.stdout)

    def test_actual_push_uses_checked_oid_and_rejects_earlier_secret(self):
        script = Path(__file__).with_name("d0-probe.py")
        with tempfile.TemporaryDirectory(prefix="d0-proof-") as directory:
            result = subprocess.run([sys.executable, str(script), "experiment", "--source", os.environ["D0_SOURCE"], "--workspace", directory, "--case", "transaction"], capture_output=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            self.assertIn(b'"earlier_secret_rejected": true', result.stdout)
            self.assertIn(b'"delivered_oid_matches": true', result.stdout)
            self.keep("transaction", result.stdout)


if __name__ == "__main__":
    unittest.main()
