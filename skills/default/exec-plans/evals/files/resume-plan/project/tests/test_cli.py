import json
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT / "src" / "report_cli.py"


def run_cli(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=PROJECT, text=True, capture_output=True)


class ReportCliTests(unittest.TestCase):
    def test_default_output_remains_text(self):
        result = run_cli()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "count=3 total=31")

    def test_json_output_has_integer_count_and_total(self):
        result = run_cli("--json")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), {"count": 3, "total": 31})


if __name__ == "__main__":
    unittest.main()
