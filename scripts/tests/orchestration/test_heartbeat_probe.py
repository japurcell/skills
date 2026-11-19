"""Public CLI checks for the bounded native heartbeat writer."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PROBE = Path(__file__).with_name("heartbeat_probe.py")


class HeartbeatProbeTests(unittest.TestCase):
    def test_writer_emits_timestamped_records_and_exits(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "heartbeats.jsonl"
            result = subprocess.run(
                [sys.executable, str(PROBE), "--output", str(output), "--interval", "0.01", "--duration", "0.08"],
                cwd=directory, capture_output=True, text=True, timeout=3,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            records = [json.loads(line) for line in output.read_text().splitlines()]
            self.assertGreaterEqual(len(records), 3)
            self.assertEqual([record["sequence"] for record in records], list(range(1, len(records) + 1)))
            self.assertTrue(all(isinstance(record["wall_time_ns"], int) for record in records))
            self.assertTrue(all(isinstance(record["monotonic_ns"], int) for record in records))
            self.assertTrue(all(record["pid"] > 0 for record in records))
            self.assertEqual(len({record["pid"] for record in records}), 1)
            self.assertEqual(records, sorted(records, key=lambda record: record["monotonic_ns"]))

    def test_writer_rejects_path_outside_project(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            result = subprocess.run(
                [sys.executable, str(PROBE), "--output", str(Path(outside) / "heartbeat.jsonl"),
                 "--interval", "0.01", "--duration", "0.05"],
                cwd=directory, capture_output=True, text=True, timeout=3,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("inside the current project", result.stderr)
            self.assertFalse((Path(outside) / "heartbeat.jsonl").exists())

    def test_writer_rejects_duration_above_finite_safety_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(PROBE), "--output", "heartbeats.jsonl",
                 "--interval", "1", "--duration", "241"],
                cwd=directory, capture_output=True, text=True, timeout=3,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("maximum duration is 240 seconds", result.stderr)
            self.assertFalse((Path(directory) / "heartbeats.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
