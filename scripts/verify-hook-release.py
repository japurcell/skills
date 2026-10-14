#!/usr/bin/env python3
"""Prepare serial Guardian release evidence using the maintained benchmark cases.

Run only against frozen baseline/candidate roots with other tests and benchmarks
stopped. --mechanics-only is a bounded adapter check, never release acceptance.
An exact --case filter supports isolated repeats; always use a new --output.
"""
from __future__ import annotations

import argparse
import concurrent.futures
from dataclasses import replace
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time

from tool_guard_corpus import PROVIDERS, decision, script_path


def load_runner(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


high_rate = load_runner("release_high_rate", "benchmark-high-rate-hooks.py")
resources = load_runner("release_resources", "benchmark-tool-guard-resources.py")
BASELINE_REF = "bc52d7d69aaa046ea97e323879402241a01fead7"
ORDER = (("baseline", "candidate"), ("candidate", "baseline"))


def baseline_fingerprints() -> dict[str, str]:
    """Validate the supplied archive against the fixed Git source, not a label."""
    root = Path(__file__).resolve().parents[1]
    names = subprocess.check_output(["git", "-C", str(root), "ls-tree", "-r", "--name-only", BASELINE_REF], text=True).splitlines()
    scripts = [script_path(Path("."), provider).as_posix() for provider in PROVIDERS]
    helpers = [str(Path(path).parent / "helpers") + "/" for path in scripts]
    selected = [name for name in names if name in scripts or name == "hooks/families/tool_guard.py"
                or (name.endswith(".py") and any(name.startswith(prefix) for prefix in helpers))]
    return {name: hashlib.sha256(subprocess.check_output(["git", "-C", str(root), "show", f"{BASELINE_REF}:{name}"])).hexdigest()
            for name in selected}


def release_cases(root: Path, condition: str):
    """bc52 already contains the corpus repairs; only full profiles are new.

    The historical runner baseline mode is deliberately not used. bc52 lacks
    _native_shell_shape, so the 130-separator full search goes through strict
    traversal; both dangerous and unknown full shapes still deny.
    """
    cases = high_rate.guard_cases(root, "candidate")
    return [replace(case, expected_decision="deny")
            if condition == "baseline" and case.name.endswith(".search.full-provider-envelope")
            else case for case in cases]


def selected_cases(root: Path, condition: str, names: list[str], mode: str):
    if mode == "timing":
        cases = release_cases(root, condition)
    else:
        cases = [high_rate.Case(f"{provider}.resources.{name}", script_path(root, provider),
                                resources.payload(provider, tool, value), "clean",
                                {"GUARD_MODE": "block"}, expected)
                 for provider in PROVIDERS
                 for name, tool, value, expected in resources.fixtures(provider)]
    known = {case.name for case in cases}
    if set(names) - known:
        raise ValueError("unknown exact case: " + ", ".join(sorted(set(names) - known)))
    return [case for case in cases if not names or case.name in names]


def copy_provider(root: Path, destination: Path, provider: str) -> None:
    source = script_path(root, provider).parent
    target = script_path(destination, provider).parent
    for path in source.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        copied = target / path.relative_to(source)
        copied.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, copied)


def case_environment(*, cold: bool = False):
    # Override inherited redirectors as well as HOME. No log reaches live state.
    return {"OBSERVABILITY_TESTING": "1", "PYTHONDONTWRITEBYTECODE": "1" if cold else "",
            "PYTHONPYCACHEPREFIX": "",
            "AUDIT_PASSIVE_LOG_MODE": "default", "AUDIT_LOG_MAX_BYTES": "134217728",
            "AUDIT_LOG_MAX_BACKUPS": "0"}


def prepared_case(case, root: Path, *, cold: bool = False):
    provider = case.name.split(".", 1)[0]
    return replace(case, script=script_path(root, provider),
                   environment={**case.environment, **case_environment(cold=cold)})


def verify_logging(home: Path, case, calls: int) -> dict:
    """Inspect completed records outside timed invocation, before home cleanup."""
    files = [home / "guard.log"] if not case.name.startswith("gemini.") else sorted((home / "guard").glob("*.log"))
    records = []
    evidence = []
    for path in files:
        if not path.is_file():
            continue
        data = path.read_bytes()
        evidence.append({"path": str(path.relative_to(home)), "bytes": len(data),
                         "sha256": hashlib.sha256(data).hexdigest()})
        for line in data.decode("utf-8").splitlines():
            start = line.find("{")
            record = json.loads(line[start:]) if start >= 0 else {}
            if record.get("event") not in {"guard_passed", "threats_detected"} or record.get("mode") != "block":
                raise ValueError("unexpected completed guard log record")
            if not case.name.endswith(".guard.failure"):
                expected_event = "guard_passed" if case.expected_decision == "allow" else "threats_detected"
                if record["event"] != expected_event:
                    raise ValueError("completed guard record does not match expected decision")
            records.append(record)
    # Existing malformed-JSON fixture exits before audit initialization. New
    # attribution may add logging; neither zero nor new logging proves a pass.
    malformed = case.name.endswith(".guard.failure")
    return {"records": len(records), "required_records": 0 if malformed else calls,
            "calls": calls, "status": "completed" if len(records) == calls else "legacy transport exception" if malformed else "missing",
            "legacy_exception": malformed, "files": evidence,
            "verified_after_elapsed": True}


def checked_invocation(case, repo: Path, home: Path):
    elapsed, code, output = high_rate.invoke(case, repo, home)
    try:
        high_rate.verify_outcome(case, code, output)
    except (RuntimeError, ValueError) as exc:
        error = ValueError(str(exc))
        error.invocation = {"case": case.name, "elapsed_ms": elapsed, "exit_code": code,
                            "expected_decision": case.expected_decision, "output": output}
        raise error from exc
    return elapsed, {"exit_code": code, "decision": decision(case.name.split(".", 1)[0], output),
                     "output": output}


def logging_error(proof: dict) -> None:
    if not proof["legacy_exception"] and proof["records"] != proof["calls"]:
        raise ValueError(f"expected {proof['calls']} completed guard records, found {proof['records']}")


def warm_run(case, root: Path, repo: Path, home: Path, samples: int, warmups: int, row: dict) -> None:
    home.mkdir(parents=True)
    case = prepared_case(case, root)
    row.update({"samples_ms": [], "outputs": []})
    for index in range(1 + warmups + samples):
        elapsed, output = checked_invocation(case, repo, home)
        if index == 0:
            row["first_process_ms"] = elapsed
            row["first_output"] = output
        elif index > warmups:
            row["samples_ms"].append(elapsed)
            row["outputs"].append(output)
    row["summary"] = high_rate.summary(row["samples_ms"])
    row["provider_bytecode_after"] = len(list(case.script.parent.rglob("*.pyc")))
    row["logging"] = verify_logging(home, case, 1 + warmups + samples)
    logging_error(row["logging"])


def comparisons(report: dict) -> list[dict]:
    """Retain pair deltas independently; one failed pair cannot average away."""
    rows = []
    for pair in (0, 1):
        by_case = {}
        for row in report["warm"]:
            if row["pair"] == pair and "summary" in row:
                by_case.setdefault(row["case"], {})[row["condition"]] = row["summary"]
        for name, conditions in by_case.items():
            if len(conditions) == 2:
                rows.append(compare(name, f"warm-pair-{pair + 1}", conditions, 2, 5))
    by_case = {}
    for row in report["cold"]:
        if "elapsed_ms" in row:
            by_case.setdefault(row["case"], {}).setdefault(row["condition"], []).append(row["elapsed_ms"])
    for name, conditions in by_case.items():
        if len(conditions) == 2:
            rows.append(compare(name, "cold", {key: high_rate.summary(value) for key, value in conditions.items()}, 5, 10))
    return rows


def compare(name: str, phase: str, conditions: dict, median_limit: float, p95_limit: float) -> dict:
    delta = {key: conditions["candidate"][key] - conditions["baseline"][key]
             for key in ("median_ms", "p95_ms")}
    return {"case": name, "phase": phase, "conditions": conditions, "delta_ms": delta,
            "allowance_ms": {"median_ms": median_limit, "p95_ms": p95_limit},
            "met": delta["median_ms"] <= median_limit and delta["p95_ms"] <= p95_limit}


def harness_fingerprints() -> dict[str, str]:
    return {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
            for name in (Path(__file__).name, "benchmark-high-rate-hooks.py", "benchmark-tool-guard-resources.py",
                         "tool_guard_corpus.py", "fixtures/tool_guard_vectors.py")}


def measure_timing(report: dict, roots: dict, selected: dict, temporary: Path, samples: int, warmups: int, cold_samples: int) -> None:
    repo = temporary / "repo"
    high_rate.make_repo(repo, "clean")
    frozen = {}
    for condition, root in roots.items():
        frozen[condition] = temporary / "warm-source" / condition
        for provider in PROVIDERS:
            copy_provider(root, frozen[condition], provider)
    for pair, order in enumerate(ORDER):
        for condition in order:
            for case in selected[condition]:
                print(f"warm pair {pair + 1}: {condition} {case.name}", file=sys.stderr, flush=True)
                row = {"pair": pair, "condition": condition, "case": case.name,
                       "expected_decision": case.expected_decision,
                       "input_sha256": hashlib.sha256(case.payload).hexdigest()}
                report["warm"].append(row)
                warm_run(case, frozen[condition], repo, temporary / f"pair-{pair}" / condition / case.name, samples, warmups, row)
    for index in range(cold_samples):
        for condition in ORDER[index % 2]:
            for case in selected[condition]:
                provider = case.name.split(".", 1)[0]
                identity = f"cold-{index}/{condition}/{case.name}"
                source, home = temporary / identity / "source", temporary / identity / "home"
                copy_provider(roots[condition], source, provider)
                home.mkdir(parents=True)
                row = {"condition": condition, "case": case.name, "index": index,
                       "expected_decision": case.expected_decision,
                       "input_sha256": hashlib.sha256(case.payload).hexdigest(),
                       "copy_id": identity + "/source", "home_id": identity + "/home",
                       "bytecode_before": len(list(source.rglob("*.pyc")))}
                report["cold"].append(row)
                current = prepared_case(case, source, cold=True)
                elapsed, outcome = checked_invocation(current, repo, home)
                row.update({"elapsed_ms": elapsed, "outcome": outcome,
                            "bytecode_after": len(list(source.rglob("*.pyc"))),
                            "logging": verify_logging(home, current, 1)})
                logging_error(row["logging"])
                if row["bytecode_before"] or row["bytecode_after"]:
                    raise ValueError("cold provider copy contains bytecode")
                shutil.rmtree(source)
    # A separate two-call batch observes contention, never feeds latency gates.
    for condition in ("baseline", "candidate"):
        for case in selected[condition]:
            if not case.name.endswith(".guard.clean"):
                continue
            home = temporary / "concurrency" / condition / case.name
            home.mkdir(parents=True)
            current = prepared_case(case, frozen[condition])
            start = time.perf_counter_ns()
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                calls = list(pool.map(lambda _: checked_invocation(current, repo, home), range(2)))
            row = {"condition": condition, "case": case.name, "workers": 2,
                   "batch_ms": (time.perf_counter_ns() - start) / 1_000_000,
                   "samples_ms": [elapsed for elapsed, _ in calls],
                   "outcomes": [outcome for _, outcome in calls],
                   "logging": verify_logging(home, current, 2)}
            report["concurrency"].append(row)
            logging_error(row["logging"])
    report["comparisons"] = comparisons(report)
    report["pair_variation"] = [{"case": case.name, "condition": condition,
                                  "median_ms": [row["summary"]["median_ms"] for row in report["warm"] if row["case"] == case.name and row["condition"] == condition],
                                  "p95_ms": [row["summary"]["p95_ms"] for row in report["warm"] if row["case"] == case.name and row["condition"] == condition]}
                                 for condition in roots for case in selected[condition]]


def measure_resources(report: dict, roots: dict, selected: dict, temporary: Path, samples: int, warmups: int) -> None:
    repo = temporary / "repo"
    high_rate.make_repo(repo, "clean")
    for condition, root in roots.items():
        frozen = temporary / "source" / condition
        for provider in PROVIDERS:
            copy_provider(root, frozen, provider)
        for case in selected[condition]:
            print(f"resources: {condition} {case.name}", file=sys.stderr, flush=True)
            row = {"condition": condition, "case": case.name, "ceiling_ms": 500}
            report["resources"].append(row)
            home = temporary / condition / case.name
            warm_run(case, frozen, repo, home, samples, warmups, row)
            current = prepared_case(case, frozen)
            env = high_rate.invocation_environment(current, home)
            memory = resources.checked_run(["/usr/bin/time", "-l", sys.executable, str(current.script)],
                                           current.payload, env, case.name.split(".", 1)[0], case.expected_decision, cwd=repo)
            match = re.search(rb"([0-9]+)\s+maximum resident set size", memory.stderr)
            if match is None:
                raise ValueError("native macOS time did not report peak RSS: " + memory.stderr.decode("utf-8", errors="replace")[:512])
            row["peak_rss_bytes"] = int(match.group(1))
            row["logging"] = verify_logging(home, current, 2 + warmups + samples)
            logging_error(row["logging"])
            row["ceiling_met"] = max(row["first_process_ms"], *row["samples_ms"]) <= 500


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-root", type=Path, help=f"git archive of {BASELINE_REF}")
    parser.add_argument("--candidate-root", type=Path, help="frozen final candidate checkout")
    parser.add_argument("--mode", choices=("timing", "resources"), default="timing")
    parser.add_argument("--case", action="append", default=[], help="exact case name; repeat this flag for an isolated repeat")
    parser.add_argument("--output", type=Path, help="new evidence JSON path; existing evidence is never replaced")
    parser.add_argument("--list", action="store_true", help="list maintained cases and explicit condition expectations")
    parser.add_argument("--mechanics-only", action="store_true", help="two samples and no warmups; NOT release evidence")
    args = parser.parse_args()
    if args.list:
        try:
            candidate = selected_cases(Path("."), "candidate", args.case, args.mode)
            baseline = {case.name: case for case in selected_cases(Path("."), "baseline", args.case, args.mode)}
        except ValueError as exc:
            parser.error(str(exc))
        print(json.dumps([{"case": case.name, "expected": {"baseline": baseline[case.name].expected_decision,
                                                          "candidate": case.expected_decision}} for case in candidate], indent=2))
        return 0
    if not args.baseline_root or not args.candidate_root or not args.output:
        parser.error("--baseline-root, --candidate-root and --output are required")
    if args.output.exists():
        parser.error("--output already exists; retain original evidence and choose a new path")
    if platform.system() != "Darwin":
        parser.error("release verification requires native macOS")
    roots = {"baseline": args.baseline_root.resolve(), "candidate": args.candidate_root.resolve()}
    try:
        selected = {condition: selected_cases(root, condition, args.case, args.mode) for condition, root in roots.items()}
        before = {condition: resources.fingerprints(root) for condition, root in roots.items()}
        if not args.mechanics_only and before["baseline"] != baseline_fingerprints():
            raise ValueError("baseline runtime fingerprints do not match " + BASELINE_REF)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    counts = (2, 0, 2) if args.mechanics_only else (25, 3, 25)
    report = {"baseline_reference": BASELINE_REF, "mode": args.mode,
              "release_acceptance_eligible": not args.mechanics_only and not args.case,
              "environment": {"platform": platform.platform(), "machine": platform.machine(),
                              "python": sys.version, "python_executable": sys.executable,
                              "git": subprocess.check_output(["git", "--version"], text=True).strip()},
              "method": {"samples": counts[0], "warmups": counts[1], "cold_launches_per_case_condition": counts[2],
                         "warm_order": ORDER, "exact_case_filter": args.case,
                         "clock": "maintained high-rate invoke: whole Python subprocess only",
                         "logging": "OBSERVABILITY_TESTING=1; disposable homes retained until completed-log verification; validation outside elapsed",
                         "cold": "independent fresh provider copy/home per launch; zero provider bytecode; OS and stdlib caches uncleared",
                         "warm_bytecode": "normal Python bytecode reuse within disposable warm/resource copies after first process",
                         "resources": "maintained resource fixtures and checked_run; separate native /usr/bin/time -l launch; RSS bytes",
                         "repeat_policy": "retain original failures; exact isolated repeats require separate output and an attributable explanation before acceptance"},
              "script_sha256": before,
              "baseline_archive_verified": not args.mechanics_only,
              "harness_sha256": harness_fingerprints(),
              "warm": [], "cold": [], "concurrency": [], "resources": [], "errors": []}
    try:
        with tempfile.TemporaryDirectory(prefix="hook-release-") as temporary:
            if args.mode == "timing":
                measure_timing(report, roots, selected, Path(temporary), *counts)
            else:
                measure_resources(report, roots, selected, Path(temporary), *counts[:2])
    except (Exception, KeyboardInterrupt) as exc:
        report["errors"].append(f"{type(exc).__name__}: {exc}")
        if hasattr(exc, "invocation"):
            report["failed_invocation"] = exc.invocation
    finally:
        try:
            after = {condition: resources.fingerprints(root) for condition, root in roots.items()}
            report["sources_unchanged"] = before == after and report["harness_sha256"] == harness_fingerprints()
            if not report["sources_unchanged"]:
                report["errors"].append("hook or harness sources changed during verification")
                report["script_sha256_after"] = after
        except OSError as exc:
            report["sources_unchanged"] = False
            report["errors"].append(f"cannot recheck frozen source: {exc}")
        passed = not report["errors"] and all(row["met"] for row in report.get("comparisons", [])) and all(row.get("ceiling_met", False) for row in report["resources"])
        report["gates_met"] = passed
        # Mechanics checks exercise collection and validation without noisy
        # low-count timing comparisons becoming an acceptance claim.
        result = not report["errors"] if args.mechanics_only else passed
        with args.output.open("x", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
    return 0 if result else 1


if __name__ == "__main__":
    raise SystemExit(main())
