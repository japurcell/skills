"""Prepare a candidate for the target skill's existing evaluation harness."""

import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
from tempfile import TemporaryDirectory


def split_skill(original):
    parts = re.fullmatch(rb"(---\r?\n.*?\r?\n---(?:\r?\n|$))(.*)", original, re.S)
    if not parts:
        raise ValueError("expected YAML frontmatter delimited by --- lines in SKILL.md")
    return parts.groups()


def prepare(source, destination, cut):
    original = (source / "SKILL.md").read_bytes()
    frontmatter, body = split_skill(original)
    needle = cut.encode()
    if body.count(needle) != 1 or not needle:
        raise ValueError("supply a nonempty cut occurring exactly once in the body")
    shortened = body.replace(needle, b"", 1)
    candidate = frontmatter + shortened
    metrics = {
        "cut": cut,
        "source_body_words": len(body.decode().split()),
        "candidate_body_words": len(shortened.decode().split()),
        "source_skill_sha256": hashlib.sha256(original).hexdigest(),
        "candidate_skill_sha256": hashlib.sha256(candidate).hexdigest(),
    }
    if destination.resolve().is_relative_to(source.resolve()):
        raise ValueError("choose a destination outside the source bundle")
    if destination.exists():
        raise ValueError("choose a fresh destination to preserve earlier trials")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=destination.parent) as temporary:
        staged = Path(temporary) / "bundle"
        shutil.copytree(source, staged)
        (staged / "SKILL.md").write_bytes(candidate)
        staged.rename(destination)
    return metrics


def fingerprint(path):
    if path.is_symlink() or not path.exists():
        raise ValueError(f"expected a self-contained file or directory: {path}")
    if path.is_file():
        return hashlib.sha256(path.read_bytes()).hexdigest()
    entries = []
    for item in sorted(path.rglob("*")):
        if item.is_symlink() or not (item.is_dir() or item.is_file()):
            raise ValueError(f"unsupported input type: {item}")
        name = item.relative_to(path).as_posix()
        digest = hashlib.sha256(item.read_bytes()).hexdigest() if item.is_file() else None
        entries.append((name, item.stat().st_mode & 0o777, digest))
    return hashlib.sha256(json.dumps(entries).encode()).hexdigest()


def assess(db, bundle, cases, conditions):
    bundle_id = fingerprint(bundle)
    results = {}
    for name, case_id in cases.items():
        runs = []
        for verdict, path, digest in db.execute(
            "SELECT verdict, evidence, digest FROM runs WHERE bundle=? AND conditions=? "
            "AND name=? AND scenario=? ORDER BY rowid", (bundle_id, conditions, name, case_id)
        ):
            evidence = Path(path)
            valid = evidence.exists() and fingerprint(evidence) == digest
            runs.append({"verdict": verdict, "evidence": path, "verified": valid})
        verdicts = [run["verdict"] for run in runs]
        if "fail" in verdicts:
            status = "rejected"
        elif any(not run["verified"] for run in runs):
            status = "inspect-evidence"
        elif not runs:
            status = "pending"
        elif verdicts[-1] == "blocked":
            status = "blocked"
        elif verdicts[-1] == "borderline":
            status = "repeat"
        else:
            status = "passed"
        results[name] = {"status": status, "runs": runs}
    skill = (bundle / "SKILL.md").read_bytes()
    return {"candidate": str(bundle), "bundle_id": bundle_id,
            "body_words": len(split_skill(skill)[1].decode().split()), "cases": results}


def graded_verdict(evidence):
    path = evidence / "grading.json" if evidence.is_dir() else evidence
    report = json.loads(path.read_text())
    assertions = report["expectations"]
    if not isinstance(assertions, list) or not assertions:
        raise ValueError("grading.json requires a nonempty expectations list")
    results = [item["passed"] for item in assertions]
    if any(type(result) is not bool for result in results):
        raise ValueError("each expectation needs a boolean passed field")
    counts = {"passed": sum(results), "failed": results.count(False), "total": len(results)}
    for key, count in counts.items():
        actual = report["summary"][key]
        if type(actual) is not int or actual != count:
            raise ValueError(f"summary.{key} disagrees with the graded expectations")
    return "pass" if all(results) else "fail"


def ledger(args):
    suite = json.loads(args.suite.read_text())
    base = args.suite.parent
    conditions = fingerprint(base / suite["conditions"])
    cases = {name: fingerprint(base / path) for name, path in suite["cases"].items()}
    if not cases:
        raise ValueError("declare at least one case in the suite")
    with closing(sqlite3.connect(args.ledger)) as db, db:
        db.execute("""CREATE TABLE IF NOT EXISTS runs
                   (bundle TEXT, conditions TEXT, name TEXT, scenario TEXT,
                    verdict TEXT, evidence TEXT UNIQUE, digest TEXT)""")
        if args.command == "record":
            if args.case not in cases:
                raise ValueError(f"unknown case {args.case!r}")
            verdict = graded_verdict(args.evidence) if args.verdict == "graded" else args.verdict
            db.execute("INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (fingerprint(args.bundle), conditions, args.case, cases[args.case],
                        verdict, str(args.evidence.resolve()), fingerprint(args.evidence)))
            return {"recorded": str(args.evidence), "verdict": verdict}
        results = [assess(db, bundle, cases, conditions) for bundle in args.bundles]
        qualified = [r for r in results if all(case["status"] == "passed"
                                               for case in r["cases"].values())]
        winner = min(qualified, key=lambda r: r["body_words"])["candidate"] if qualified else None
        return {"winner": winner, "conditions_id": conditions, "case_ids": cases,
                "candidates": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    cut = commands.add_parser("cut", help="prepare an isolated deletion trial")
    cut.add_argument("source", type=Path)
    cut.add_argument("destination", type=Path)
    cut.add_argument("cut", help="exact text to delete once from the body")
    record = commands.add_parser("record", help="retain a graded run using a unique evidence path")
    status = commands.add_parser("status", help="list reusable runs and select a full-suite winner")
    for sub in (record, status):
        sub.add_argument("suite", type=Path, help="suite JSON defining conditions and case inputs")
        sub.add_argument("ledger", type=Path, help="persistent SQLite ledger outside input trees")
    record.add_argument("bundle", type=Path)
    record.add_argument("case")
    record.add_argument("verdict", choices=["graded", "pass", "borderline", "fail", "blocked"])
    record.add_argument("evidence", type=Path, help="retained run file or directory")
    status.add_argument("bundles", nargs="+", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "cut":
            result = prepare(args.source, args.destination, args.cut)
        else:
            result = ledger(args)
    except (OSError, ValueError, KeyError, AttributeError, TypeError, sqlite3.Error) as error:
        parser.exit(2, f"{error}\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
