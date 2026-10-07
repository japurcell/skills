import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from summary import summarize


class SummaryTests(unittest.TestCase):
    def test_counts_rows_and_sums_values(self):
        self.assertEqual(summarize([7, 11, 13]), {"count": 3, "total": 31})


if __name__ == "__main__":
    unittest.main()
