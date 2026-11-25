"""Prepare one disposable input for the size scenarios in authoring-scenarios.md."""

import argparse
from pathlib import Path


CASES = ("create-exact", "create-over", "resume-over", "large-index", "close-only")
APPROVED = Path(__file__).parent / "files" / "size-checkpoints" / "approved.md"


def padded(plan, size):
    # Use UTF-8 and make the one-byte difference visible in the audit trail.
    observation = " field note: café verified."
    remaining = size - len(plan.encode()) - 1
    count, tail = divmod(remaining, len(observation.encode()))
    return plan + observation * count + "." * tail + "\n"


def write_fixture(path, text):
    # The suite measures on-disk UTF-8 bytes, including newlines.
    path.write_bytes(text.encode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=CASES)
    parser.add_argument("workspace", type=Path, help="new directory for this independent checkpoint")
    args = parser.parse_args()
    args.workspace.mkdir(parents=True, exist_ok=False)
    plan = APPROVED.read_text(encoding="utf-8")
    rows = ["café-001"]
    if args.case == "large-index":
        index = ["#### Open tasks", ""]
        for number in range(2, 193):
            # Alternate adjacent tasks with dependencies reaching across index pages.
            prerequisite = number - 1 if number % 2 else number // 2
            label = f"café-{number:03d}"
            rows.append(label)
            index.append(
                f"- T{number:03d} (open, release editor): verify row {number} is "
                f"`{label}`; prerequisite T{prerequisite:03d}. Stop on a mismatch."
            )
        plan = plan.replace("## Concrete Steps", "\n".join(index) + "\n\n## Concrete Steps")
    else:
        plan = padded(plan, 12288 if args.case == "create-exact" else 12289)
    path = "draft.md" if args.case.startswith("create") else "AtlasPlan.md"
    write_fixture(args.workspace / path, plan)
    write_fixture(args.workspace / "labels.txt", "\n".join(rows) + "\n")
    write_fixture(args.workspace / "DormantPlan.md", padded(APPROVED.read_text(encoding="utf-8"), 13312))
    if args.case == "close-only":
        write_fixture(
            args.workspace / "release.txt",
            "Mara checked head -n 1 labels.txt: café-001. Release editor Jo accepted this sole row. Receipt CLOSE-7104.\n",
        )


if __name__ == "__main__":
    main()
