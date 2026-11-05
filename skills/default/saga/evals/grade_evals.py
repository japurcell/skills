#!/usr/bin/env python3
"""Grade the Saga live-eval outputs against their disposable fixtures."""

import argparse
import json
import re
import sys
from pathlib import Path


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


def read_required(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"required regular file is missing: {path}")
    content = path.read_text(encoding="utf-8")
    if not content.strip():
        raise ValueError(f"required file is empty: {path}")
    return content


def files_under(root: Path) -> dict[str, bytes | None]:
    result = {}
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"symlinks are not valid fixture evidence: {path}")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = path.read_bytes()
        elif path.is_dir():
            result[path.relative_to(root).as_posix() + "/"] = None
    return result


def matching_files(
    before: dict[str, bytes | None],
    after: dict[str, bytes | None],
    allowed_prefix: str = "",
    ignored_paths: tuple[str, ...] = (),
) -> tuple[bool, str]:
    names = sorted(set(before) | set(after))
    changed = [name for name in names if name not in before or name not in after or before[name] != after[name]]
    changed = [name for name in changed if name not in ignored_paths]
    unexpected = [
        name for name in changed
        if not (allowed_prefix and (name == allowed_prefix.rstrip("/") + "/" or name.startswith(allowed_prefix)))
    ]
    return not unexpected, f"Changed fixture files outside allowed scope: {unexpected}" if unexpected else "No unexpected fixture changes."


def generated_brain_index_update_is_valid(
    before: dict[str, bytes | None], after: dict[str, bytes | None], saga_id: str
) -> tuple[bool, str]:
    old = before.get("brain/index.md")
    new = after.get("brain/index.md")
    if old == new:
        return True, "brain/index.md is unchanged."
    if not isinstance(old, bytes) or not isinstance(new, bytes):
        return False, "brain/index.md was added or removed instead of updated."

    try:
        old_text = old.decode("utf-8")
        new_text = new.decode("utf-8")
    except UnicodeError:
        return False, "brain/index.md is not valid UTF-8."

    prefix = old_text if old_text.endswith("\n") else old_text + "\n"
    if not new_text.startswith(prefix):
        return False, "Existing brain/index.md content was changed."

    saga_root = f"sagas/{saga_id}"
    added_links = 0
    for line in new_text[len(prefix):].splitlines():
        if not line.strip():
            continue
        if re.fullmatch(rf"## {re.escape(saga_root)}(?:/[A-Za-z0-9._/-]+)?", line):
            continue
        link = re.fullmatch(r"- \[[^\]]+\]\(<([^>]+)>\)", line)
        if not link or not link.group(1).startswith(saga_root + "/"):
            return False, f"Unexpected generated brain index line: {line!r}."
        target = "brain/" + link.group(1)
        if target not in after or after[target] is None:
            return False, f"Generated brain index points to a missing saga file: {target}."
        added_links += 1

    if not added_links:
        return False, "brain/index.md added no links to the new saga."
    return True, f"Added {added_links} generated navigation links for {saga_root}; existing content is unchanged."


def grade_creation(fixture: Path, before: dict[str, bytes | None], response: str) -> list[dict]:
    saga_root = fixture / "brain" / "sagas"
    candidates = sorted(path for path in saga_root.iterdir() if path.is_dir()) if saga_root.is_dir() else []
    valid = [path for path in candidates if (path / "SAGA.md").is_file() and (path / "PROGRESS.md").is_file()]
    single_saga = len(candidates) == 1 and len(valid) == 1
    canonical_path = f"brain/sagas/{valid[0].name}" if single_saga else ""
    saga_text = (valid[0] / "SAGA.md").read_text(encoding="utf-8") if single_saga else ""
    progress_text = (valid[0] / "PROGRESS.md").read_text(encoding="utf-8") if single_saga else ""
    path_records = [
        re.search(r"(?m)^- Saga directory:\s*(.+?)\s*$", text)
        for text in (saga_text, progress_text)
    ]
    resolved_path = str((fixture / canonical_path).resolve()) if canonical_path else ""
    paths_match = bool(canonical_path) and all(path_records) and (
        path_records[0].group(1) == path_records[1].group(1)
        and path_records[0].group(1).replace("\\", "/") in (canonical_path, resolved_path.replace("\\", "/"))
    )
    criteria = re.search(r"(?im)^## Saga exit criteria\s*$", saga_text) and re.search(
        r"(?m)^\s*1\.\s+\S", saga_text
    )
    feature_covered = all(term in saga_text.lower() for term in ("cache", "refresh"))
    response_names_path = bool(canonical_path and canonical_path in response.replace("\\", "/"))
    # The eval runner creates this empty working directory before each run.
    after = files_under(fixture)
    index_ok, index_evidence = generated_brain_index_update_is_valid(before, after, valid[0].name if single_saga else "")
    outside_files_ok, outside_evidence = matching_files(
        before,
        after,
        "brain/sagas/",
        ignored_paths=("nested/", "brain/index.md"),
    )
    outside_ok = outside_files_ok and index_ok
    if outside_ok and "Added " in index_evidence:
        outside_evidence = index_evidence
    elif not index_ok:
        outside_evidence = f"{index_evidence} {outside_evidence}"
    return [
        expectation("Exactly one saga was created at <fixture-root>/brain/sagas/<id>, with SAGA.md and PROGRESS.md.", single_saga, f"Found saga directories: {[path.name for path in candidates]}; valid: {[path.name for path in valid]}"),
        expectation("SAGA.md and PROGRESS.md record the same canonical brain/sagas/<id> path.", paths_match, f"Expected path record: {canonical_path or 'no single valid saga'}"),
        expectation("The saga captures the cache refresh feature and at least one numbered exit criterion.", feature_covered and bool(criteria), "Checked feature terms, exit-criteria heading, and numbered criterion in SAGA.md."),
        expectation("The response identifies the created saga path.", response_names_path, f"Expected response to include {canonical_path or 'one canonical saga path'}."),
        expectation("No fixture files outside the new brain/sagas subtree changed, except generated brain/index.md links to that saga.", outside_ok, outside_evidence),
    ]


def grade_unchanged(eval_id: int, fixture: Path, before: dict[str, bytes | None], response: str) -> list[dict]:
    after = files_under(fixture)
    unchanged, evidence = matching_files(before, after)
    if eval_id == 1:
        saga_exists = (fixture / "brain/sagas/cache-refresh-20261105/SAGA.md").is_file()
        saga_named = "cache-refresh-20261105" in response
        state_grounded = "worker-17" in response and any(term in response.lower() for term in ("in progress", "reachable", "wait"))
        label = "Resume the existing cache-refresh-20261105 saga without changing its files."
        detail = f"Existing saga present: {saga_exists}; response names it: {saga_named}; response cites active worker state: {state_grounded}."
        checks = [
            expectation(label, unchanged and saga_exists, evidence),
            expectation("The response names the existing saga and bases its next action on the reachable in-progress worker evidence.", saga_named and state_grounded, detail),
        ]
    else:
        decision_grounded = "label-copy" in response.lower() or "existing plan" in response.lower()
        scope_grounded = "one-line" in response.lower() or "small" in response.lower() or "single" in response.lower()
        label = "Avoid creating a duplicate saga or changing the existing plan fixture."
        detail = f"Fixture unchanged: {unchanged}; response identifies existing plan: {decision_grounded}."
        checks = [
            expectation(label, unchanged, evidence),
            expectation("The response recognizes the existing label-copy plan and its small scope.", decision_grounded and scope_grounded, detail),
        ]
    return checks


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-id", required=True, type=int, choices=(0, 1, 2))
    parser.add_argument("--fixture-root", required=True, type=Path)
    parser.add_argument("--source-fixture", required=True, type=Path, help="Immutable input fixture copied before the run.")
    parser.add_argument("--response", required=True, type=Path)
    parser.add_argument("--transcript", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    for name in ("fixture_root", "source_fixture"):
        value = getattr(args, name)
        if not value.is_dir():
            parser.error(f"--{name.replace('_', '-')} must name an existing directory")
    if args.fixture_root.resolve() == args.source_fixture.resolve():
        parser.error("--fixture-root must be a disposable copy, not the immutable source fixture")
    return args


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(sys.argv[1:] if argv is None else argv)
        response = read_required(args.response)
        read_required(args.transcript)
        before = files_under(args.source_fixture)
        files_under(args.fixture_root)
        expectations = (
            grade_creation(args.fixture_root, before, response)
            if args.eval_id == 0
            else grade_unchanged(args.eval_id, args.fixture_root, before, response)
        )
    except (OSError, UnicodeError, ValueError) as error:
        print(f"invalid evaluation evidence: {error}", file=sys.stderr)
        return 2

    passed = sum(item["passed"] for item in expectations)
    total = len(expectations)
    result = {
        "expectations": expectations,
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "pass_rate": round(passed / total, 2) if total else 0.0,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}; {total - passed} of {total} expectations failed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
