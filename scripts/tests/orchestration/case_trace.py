"""Read controlled observations in append order, retaining partial and legacy cases."""
from collections import defaultdict
from dataclasses import dataclass, field
import json
from pathlib import Path


CASE_IDS = tuple(f"case{number:02d}" for number in range(1, 17))


@dataclass
class CaseTrace:
    starts: dict = field(default_factory=dict, init=False)
    rows: list = field(default_factory=list)
    ordering_issues: list = field(default_factory=list)

    def of_kind(self, *kinds):
        return [row for row in self.rows if row["kind"] in kinds]

    def flag(self, row, reason):
        self.ordering_issues.append({"kind": row["kind"], "reason": reason})

    def check_dispatch_starts(self):
        self.starts = {row["sequence"]: row for row in self.of_kind("dispatch_start")
                       if type(row.get("sequence")) is int}
        for start in self.starts.values():
            if type(start.get("entered_ns")) is not int:
                self.flag(start, "missing dispatch entry time")
        for receipt in self.of_kind("dispatch"):
            ref = receipt.get("start_sequence")
            start = self.starts.get(ref) if type(ref) is int else None
            seq = receipt.get("sequence")
            if (not start or start.get("model") != receipt.get("model")
                    or type(seq) is not int or ref >= seq):
                self.flag(receipt, "dispatch receipt lacks a matching earlier start")

            if receipt.get("result") == "model_wide_rejection":
                confirmations = self.confirmations(receipt)
                if len(confirmations) != 1 or type(confirmations[0].get("recorded_ns")) is not int:
                    self.flag(receipt, "missing or ambiguous rejection recording time")

    def confirmations(self, receipt):
        return [row for row in self.of_kind("rejection_recorded")
                if type(row.get("receipt_sequence")) is int
                and row["receipt_sequence"] == receipt.get("sequence")
                and type(row.get("sequence")) is int and row["sequence"] > row["receipt_sequence"]]

    def order_after_receipt(self, earlier, later):
        if any(issue["kind"] in ("dispatch", "dispatch_start", "reuse", "rejection_recorded") for issue in self.ordering_issues):
            return None
        start = self.starts[later["start_sequence"]]
        confirmation, = self.confirmations(earlier)
        return confirmation["sequence"] < start["sequence"] and confirmation["recorded_ns"] < start["entered_ns"]

    @property
    def actions(self):
        return self.of_kind("dispatch", "reuse")


def read_cases(path: Path):
    cases = defaultdict(CaseTrace)
    rows = []
    with path.open(encoding="utf-8") as stream:
        for line, raw in enumerate(stream, 1):
            row = json.loads(raw)
            if (not isinstance(row, dict) or not isinstance(row.get("kind"), str)
                    or not isinstance(row.get("case_id"), str)):
                raise ValueError(f"missing event or case ID on line {line}")
            cases[row["case_id"]].rows.append(row)
            rows.append(row)

    # Mark both sides of any inversion or duplicate in the global sequence.
    # Other cases may legitimately occur between two receipts for this case.
    highest = -1
    conflicts = set()
    for index, row in enumerate(rows):
        sequence = row.get("sequence")
        if type(sequence) is not int or sequence < 0:
            cases[row["case_id"]].flag(row, f"missing or invalid sequence on line {index + 1}")
        else:
            if sequence <= highest:
                conflicts.add(index)
            highest = max(sequence, highest)
    lowest = None
    for index in reversed(range(len(rows))):
        sequence = rows[index].get("sequence")
        if type(sequence) is int and sequence >= 0:
            if lowest is not None and sequence >= lowest:
                conflicts.add(index)
            lowest = min(lowest, sequence) if lowest is not None else sequence
    for index in sorted(conflicts):
        row = rows[index]
        cases[row["case_id"]].flag(row, f"conflicting sequence on line {index + 1}")

    for case in cases.values():
        case.check_dispatch_starts()
    return cases
