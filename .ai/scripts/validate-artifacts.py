#!/usr/bin/env python3
"""Lightweight stop-gate validator for .ai workflow artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

REQUIRED_FILES = [
    "00-intake.md",
    "01-worktree.md",
    "02-exploration-summary.md",
    "03-research-findings.md",
    "04-clarifications.md",
    "05-plan.md",
    "06-task-graph.yaml",
    "08-code-review.md",
    "08-security-review.md",
    "08-tech-debt.md",
    "09-verification.md",
]


GATE_HINTS = {
    "00-intake.md": "must include acceptance criteria",
    "01-worktree.md": "must include branch and worktree path",
    "02-exploration-summary.md": "must include open questions",
    "03-research-findings.md": "must include dated source rows",
    "04-clarifications.md": "must include unresolved blockers section",
    "05-plan.md": "must include verification strategy",
    "06-task-graph.yaml": "must define red/green/refactor tasks",
    "09-verification.md": "must include checks executed",
}


CONTENT_CHECKS = [
    ("00-intake.md", "Acceptance criteria"),
    ("01-worktree.md", "Worktree path"),
    ("02-exploration-summary.md", "Open questions"),
    ("03-research-findings.md", "Checked at"),
    ("04-clarifications.md", "Unresolved blockers"),
    ("05-plan.md", "Verification strategy"),
    ("06-task-graph.yaml", "stage: red"),
    ("06-task-graph.yaml", "stage: green"),
    ("06-task-graph.yaml", "stage: refactor"),
    ("09-verification.md", "Checks executed"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate .ai workflow artifacts")
    parser.add_argument("--work-id", required=True, help="Artifact work ID")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root path (default: current directory)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.repo_root).resolve()
    artifact_dir = root / ".ai" / "artifacts" / args.work_id

    if not artifact_dir.exists():
        print(f"ERROR: missing artifact directory: {artifact_dir}")
        return 1

    errors: List[str] = []

    for file_name in REQUIRED_FILES:
        path = artifact_dir / file_name
        if not path.exists():
            hint = GATE_HINTS.get(file_name, "required by workflow")
            errors.append(f"missing {file_name} ({hint})")

    for file_name, needle in CONTENT_CHECKS:
        path = artifact_dir / file_name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if needle not in text:
            errors.append(f"{file_name}: expected text '{needle}'")

    if errors:
        print("STOP GATES: FAILED")
        for err in errors:
            print(f"- {err}")
        return 1

    print("STOP GATES: PASSED")
    print(f"Validated artifacts for work-id '{args.work_id}' at {artifact_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
