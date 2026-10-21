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
import math
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time

from tool_guard_corpus import PROVIDERS, script_path
from hook_benchmark_support import (
    collect_macos_rss, guardian_runtime_footprint, prepare_failure, verify_audit,
    guardian_decision, guardian_canonical_paths, guardian_benchmark_environment,
    guardian_response_matches, read_audit_records,
)
from fixtures.tool_guard_resource_cases import (
    FIXTURE_SETS, HISTORICAL_TIMING_CASES, DEFAULT_EXPECTATIONS, resource_inputs, resource_cases,
    load_contracts, validate_response, fixture_metadata,
)


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


def baseline_fingerprints(reference: str = BASELINE_REF) -> dict[str, str]:
    """Validate the supplied archive against the selected Git revision."""
    root = Path(__file__).resolve().parents[1]
    names = subprocess.check_output(["git", "-C", str(root), "ls-tree", "-r", "--name-only", reference], text=True).splitlines()
    scripts, helpers, _canonical = guardian_runtime_footprint()
    selected = [name for name in names if name in scripts or name in guardian_canonical_paths() or (name.startswith("hooks/runtime/") and name.endswith(".py"))
                or (name.endswith(".py") and any(name.startswith(prefix) for prefix in helpers))]
    return {name: hashlib.sha256(subprocess.check_output(["git", "-C", str(root), "show", f"{reference}:{name}"])).hexdigest()
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


def fixture_cases(root: Path, fixture_set: str, mode: str, *,
                  expectations: Path | None = None, condition: str = "candidate"):
    if mode == "timing":
        cases = [case for case in release_cases(root, "candidate")
                 if case.name.split(".", 1)[1] in HISTORICAL_TIMING_CASES]
        if fixture_set in {"file-operations-v1", "file-operations-v2"}:
            from tool_guard_corpus import file_operation_fixtures, encode, envelope
            cases.extend(high_rate.Case(f"{provider}.guard.{fixture.name}", script_path(root, provider),
                                       encode(envelope(provider, fixture)), "clean", {"GUARD_MODE": "block"})
                         for provider in PROVIDERS for fixture in file_operation_fixtures())
            for provider in PROVIDERS:
                cases.extend(high_rate.Case(f"{provider}.guard.{name}", script_path(root, provider), data,
                                           "clean", {"GUARD_MODE": guard_mode}, fixture_metadata={"injection": injection})
                             for name, data, guard_mode, injection in resource_inputs(provider, fixture_set)
                             if injection not in {"none", "raw-envelope"} or name.startswith(("mode.", "capacity-")))
        return cases
    return [high_rate.Case(case.name, case.script, case.payload, "clean", case.environment,
                           case.expected_decision, case.fixture_metadata)
            for case in resource_cases(root, fixture_set, expectations, condition)]


def selected_cases(root: Path, condition: str, names: list[str], mode: str,
                   fixture_set: str = "historical-v1", expectations: Path | None = None):
    cases = fixture_cases(root, fixture_set, mode, expectations=expectations, condition=condition)
    if mode == "timing":
        contracts = load_contracts(expectations or DEFAULT_EXPECTATIONS, fixture_set, mode,
                                  [(case.name, case.payload, case.environment["GUARD_MODE"],
                                    (case.fixture_metadata or {}).get("injection", "malformed-json" if case.name.endswith(".guard.failure") else "none"))
                                   for case in cases])
        cases = [replace(case, expected_decision=contracts[case.name][condition]["decision"],
                         fixture_metadata=fixture_metadata(contracts[case.name], condition)) for case in cases]
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
    return guardian_benchmark_environment(cold=cold)


def prepared_case(case, root: Path, *, cold: bool = False, home: Path | None = None):
    provider = case.name.split(".", 1)[0]
    current = replace(case, script=script_path(root, provider),
                      environment={**case.environment, **case_environment(cold=cold)})
    return prepare_failure(current, home) if home is not None else current


def verify_logging(home: Path, case, calls: int) -> dict:
    """Inspect completed records outside timed invocation, before home cleanup."""
    if (case.fixture_metadata or {}).get("contract"):
        return verify_audit(home, case, calls)
    evidence, completed = read_audit_records(home, case, require_json=False)
    records = []
    for record in completed:
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


def checked_invocation(case, repo: Path, home: Path, *, observation: dict | None = None):
    if observation is None:
        elapsed, code, output = high_rate.invoke(case, repo, home)
    else:
        observation["start_monotonic_ns"] = time.monotonic_ns()
        try:
            elapsed, code, output = high_rate.invoke(case, repo, home)
        finally:
            observation["end_monotonic_ns"] = time.monotonic_ns()
    try:
        contract = (case.fixture_metadata or {}).get("contract")
        if contract:
            if code or output.get("invalid_stdout") or not guardian_response_matches(
                    case.name.split(".")[0], code, output, case.expected_decision, contract=contract):
                raise ValueError(f"{case.name}: expected {case.expected_decision}, unexpected permission response (exit {code})")
        else:
            high_rate.verify_outcome(case, code, output)
    except (RuntimeError, ValueError) as exc:
        error = ValueError(str(exc))
        error.invocation = {"case": case.name, "elapsed_ms": elapsed, "exit_code": code,
                            "expected_decision": case.expected_decision,
                            "contract": (case.fixture_metadata or {}).get("contract"), "output": output,
                            **(observation or {})}
        raise error from exc
    return elapsed, {"exit_code": code, "decision": guardian_decision(case.name.split(".", 1)[0], output, contract=contract),
                     "output": output}


def logging_error(proof: dict) -> None:
    if proof["records"] != proof["required_records"]:
        raise ValueError(f"expected {proof['required_records']} completed guard records, found {proof['records']}")


def retain_warm_sample(row: dict, index: int, warmups: int, elapsed: float, output: dict) -> None:
    if index == 0:
        row["first_process_ms"] = elapsed
        row["first_output"] = output
    elif index > warmups:
        row["samples_ms"].append(elapsed)
        row["outputs"].append(output)


def finalize_warm_run(row: dict, case, home: Path, calls: int) -> None:
    row["summary"] = high_rate.summary(row["samples_ms"])
    row["provider_bytecode_after"] = len(list(case.script.parent.rglob("*.pyc")))
    row["logging"] = verify_logging(home, case, calls)


def warm_run(case, root: Path, repo: Path, home: Path, samples: int, warmups: int, row: dict) -> None:
    home.mkdir(parents=True)
    case = prepared_case(case, root, home=home)
    row.update({"samples_ms": [], "outputs": []})
    for index in range(1 + warmups + samples):
        elapsed, output = checked_invocation(case, repo, home)
        retain_warm_sample(row, index, warmups, elapsed, output)
    finalize_warm_run(row, case, home, 1 + warmups + samples)
    logging_error(row["logging"])


def warm_pair_run(cases: dict, roots: dict, repo: Path, homes: dict,
                  samples: int, warmups: int, pair: int, rows: dict) -> None:
    """Keep each matched launch adjacent while retaining independent samples."""
    baseline, candidate = cases["baseline"], cases["candidate"]
    if baseline.name != candidate.name:
        raise ValueError("warm pair requires equal exact case IDs")
    if baseline.payload != candidate.payload:
        raise ValueError("warm pair requires identical payload bytes")
    prepared = {}
    for label in ORDER[pair]:
        homes[label].mkdir(parents=True)
        prepared[label] = prepared_case(cases[label], roots[label], home=homes[label])
        rows[label].update({"samples_ms": [], "outputs": [], "invocations": []})
    last = {}
    for index in range(1 + warmups + samples):
        kind = "first" if index == 0 else "warmup" if index <= warmups else "measured"
        for label in ORDER[pair]:
            row = rows[label]
            observation = {"call_index": index, "kind": kind}
            row["invocations"].append(observation)
            elapsed, output = checked_invocation(prepared[label], repo, homes[label], observation=observation)
            last[label] = {"case": cases[label].name, "condition": label,
                           "elapsed_ms": elapsed, "expected_decision": cases[label].expected_decision,
                           **output, **observation}
            retain_warm_sample(row, index, warmups, elapsed, output)
    for label in ORDER[pair]:
        row = rows[label]
        finalize_warm_run(row, prepared[label], homes[label], 1 + warmups + samples)
    for label in ORDER[pair]:
        try:
            logging_error(rows[label]["logging"])
        except ValueError as exc:
            exc.invocation = last[label]
            raise


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
    partition = report.get("throughput_partition")
    if partition is not None:
        for row in rows:
            observation = (report["comparison_reference"] == "original"
                           and row["case"] in partition["observations"])
            row["classification"] = "changed-workload-observation" if observation else "gated"
            if observation:
                row["met"] = None
    return rows


def validate_measurements(report: dict, selected: dict, mode: str, samples: int,
                          warmups: int, cold_samples: int, *, reference="original", partition=None) -> None:
    """Require complete call evidence against independently selected contracts."""
    def require(condition, message):
        if not condition:
            raise ValueError("incomplete or inconsistent measurement evidence: " + message)

    def elapsed(value):
        require(type(value) in (int, float) and math.isfinite(value) and value > 0, "elapsed time")

    def checksum(value):
        return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)

    def response(observation, case):
        contract = case.fixture_metadata["contract"]
        require(isinstance(observation, dict) and type(observation.get("exit_code")) is int
                and observation["exit_code"] == 0 and isinstance(observation.get("output"), dict), "call response")
        output = observation["output"]
        require(not output.get("invalid_stdout") and observation.get("decision") == case.expected_decision
                and guardian_decision(case.name.split(".", 1)[0], output, contract=contract) == case.expected_decision,
                "call decision")
        validate_response(contract, output, provider=case.name.split(".", 1)[0])

    def audit(proof, case, calls):
        contract = case.fixture_metadata["contract"]
        expected = contract["audit"]
        required = calls * expected["records_per_call"]
        require(isinstance(proof, dict) and "failure_injection" in proof, "audit proof")
        require(all(type(proof.get(key)) is int and proof[key] == value
                    for key, value in (("calls", calls), ("records", required), ("required_records", required))),
                "audit call/record counts")
        require(proof.get("status") == proof.get("audit_outcome") == expected["outcome"]
                and proof.get("verified_after_elapsed") is True and proof.get("legacy_exception") is False,
                "audit outcome")
        files = proof.get("files")
        require(isinstance(files, list) and bool(files) == bool(required), "audit files")
        for file in files:
            require(isinstance(file, dict) and isinstance(file.get("path"), str) and bool(file["path"])
                    and type(file.get("bytes")) is int and file["bytes"] > 0 and checksum(file.get("sha256")),
                    "audit file fingerprint")
        injection = case.fixture_metadata["injection"]
        failure = proof.get("failure_injection")
        if injection == "none":
            require(failure is None, "unexpected failure injection")
        elif injection == "raw-envelope" or injection == "malformed-json" and "reader_limits" in case.fixture_metadata:
            from hook_benchmark_support import reader_boundary_proof
            require(failure == reader_boundary_proof(case), "reader boundary proof")
        elif injection == "malformed-json":
            require(failure == {"kind": injection, "invalid_json": True}, "malformed-input proof")
        elif injection == "missing-policy":
            require(failure == {"kind": injection, "policy_absent": True}, "bootstrap proof")
        elif injection == "audit-unavailable":
            require(isinstance(failure, dict) and set(failure) == {"kind", "parent_is_regular_file", "sha256"}
                    and failure["kind"] == injection and failure["parent_is_regular_file"] is True
                    and checksum(failure["sha256"]), "audit failure proof")
        else:
            require(False, "unknown failure injection")

    def row_contract(row, cases):
        case = cases[row["condition"]][row["case"]]
        require(row.get("contract") == case.fixture_metadata["contract"]
                and row.get("expected_decision") == case.expected_decision
                and row.get("input_sha256") == hashlib.sha256(case.payload).hexdigest(), "selected contract/hash")
        return case

    def sampled(row, case, calls):
        values, outputs = row.get("samples_ms"), row.get("outputs")
        require(isinstance(values, list) and len(values) == samples
                and isinstance(outputs, list) and len(outputs) == samples, "measured sample/output counts")
        elapsed(row.get("first_process_ms"))
        response(row.get("first_output"), case)
        for value, observation in zip(values, outputs, strict=True):
            elapsed(value)
            response(observation, case)
        require(row.get("summary") == high_rate.summary(values), "sample summary")
        audit(row.get("logging"), case, calls)
        if partition is not None:
            require(max(row["first_process_ms"], *values) <= 500, "finite-case 500 ms ceiling")

    try:
        require(report.get("mode") == mode and isinstance(report.get("method"), dict)
                and all(type(report["method"].get(key)) is int and report["method"][key] == value
                        for key, value in (("samples", samples), ("warmups", warmups),
                                           ("cold_launches_per_case_condition", cold_samples))), "declared method")
        require(isinstance(selected, dict) and set(selected) == {"baseline", "candidate"}, "selected cases")
        cases = {label: {case.name: case for case in values} for label, values in selected.items()}
        names = set(cases["baseline"])
        require(bool(names) and names == set(cases["candidate"])
                and all(len(cases[label]) == len(selected[label]) for label in cases), "complete unique selected cases")
        require(report.get("comparison_reference", "original") == reference
                and report.get("throughput_partition") == partition, "reviewed reference/partition")
        if mode == "resources":
            rows = report["resources"]
            identities = [(row.get("case"), row.get("condition")) for row in rows]
            wanted = {(name, label) for name in names for label in ORDER[0]}
            require(len(identities) == len(wanted) and set(identities) == wanted, "resource rows")
            for row in rows:
                case = row_contract(row, cases)
                sampled(row, case, 2 + warmups + samples)
                met = max(row["first_process_ms"], *row["samples_ms"]) <= 500
                require(row.get("ceiling_ms") == 500 and row.get("ceiling_met") is met
                        and type(row.get("peak_rss_bytes")) is int and row["peak_rss_bytes"] > 0, "resource ceiling/RSS")
            return
        warm = [(row.get("case"), row.get("condition"), row.get("pair")) for row in report["warm"]]
        wanted = {(name, label, pair) for name in names for label in ORDER[0] for pair in (0, 1)}
        cold = [(row.get("case"), row.get("condition"), row.get("index")) for row in report["cold"]]
        wanted_cold = {(name, label, index) for name in names for label in ORDER[0] for index in range(cold_samples)}
        require(len(warm) == len(wanted) and set(warm) == wanted and len(cold) == len(wanted_cold)
                and set(cold) == wanted_cold, "timing rows")
        for row in report["warm"]:
            case = row_contract(row, cases)
            sampled(row, case, 1 + warmups + samples)
            invocations = row.get("invocations")
            kinds = ["first"] + ["warmup"] * warmups + ["measured"] * samples
            require(type(row.get("pair")) is int and isinstance(invocations, list) and len(invocations) == len(kinds),
                    "warm invocation count")
            previous = 0
            for index, (call, kind) in enumerate(zip(invocations, kinds, strict=True)):
                require(type(call.get("call_index")) is int and call["call_index"] == index and call.get("kind") == kind
                        and type(call.get("start_monotonic_ns")) is int and type(call.get("end_monotonic_ns")) is int
                        and previous <= call["start_monotonic_ns"] < call["end_monotonic_ns"], "warm invocation order")
                previous = call["end_monotonic_ns"]
        for row in report["cold"]:
            case = row_contract(row, cases)
            elapsed(row.get("elapsed_ms"))
            response(row.get("outcome"), case)
            audit(row.get("logging"), case, 1)
            require(type(row.get("index")) is int
                    and all(type(row.get(key)) is int and row[key] == 0 for key in ("bytecode_before", "bytecode_after"))
                    and all(isinstance(row.get(key), str) and bool(row[key]) for key in ("copy_id", "home_id")),
                    "fresh cold copy")
            if partition is not None:
                require(row["elapsed_ms"] <= 500, "finite-case 500 ms ceiling")
        require(all(len({row[key] for row in report["cold"]}) == len(report["cold"]) for key in ("copy_id", "home_id")),
                "unique cold copies/homes")
        expected_comparisons = comparisons(report)
        require(report.get("comparisons") == expected_comparisons, "comparison values/classification/gates")
        require(all(actual["met"] is expected["met"]
                    for actual, expected in zip(report["comparisons"], expected_comparisons, strict=True)),
                "exact Boolean gates or observation None")
        require(len(report["comparisons"]) == 3 * len(names), "complete comparisons")
    except (KeyError, TypeError, AttributeError, IndexError) as error:
        raise ValueError("incomplete measurement evidence: " + type(error).__name__) from error


def compare(name: str, phase: str, conditions: dict, median_limit: float, p95_limit: float) -> dict:
    delta = {key: conditions["candidate"][key] - conditions["baseline"][key]
             for key in ("median_ms", "p95_ms")}
    return {"case": name, "phase": phase, "conditions": conditions, "delta_ms": delta,
            "allowance_ms": {"median_ms": median_limit, "p95_ms": p95_limit},
            "met": delta["median_ms"] <= median_limit and delta["p95_ms"] <= p95_limit}


def harness_fingerprints(expectations: Path | None = None) -> dict[str, str]:
    result = {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
            for name in (Path(__file__).name, "benchmark-high-rate-hooks.py", "benchmark-tool-guard-resources.py",
                         "tool_guard_corpus.py", "fixtures/tool_guard_vectors.py", "hook_benchmark_support.py",
                         "hook_test_support.py", "fixtures/tool_guard_resource_cases.py")}
    result["reviewed_expectations"] = hashlib.sha256((expectations or DEFAULT_EXPECTATIONS).read_bytes()).hexdigest()
    return result


def measure_timing(report: dict, roots: dict, selected: dict, temporary: Path, samples: int, warmups: int, cold_samples: int) -> None:
    repo = temporary / "repo"
    high_rate.make_repo(repo, "clean")
    frozen = {}
    for condition, root in roots.items():
        frozen[condition] = temporary / "warm-source" / condition
        for provider in PROVIDERS:
            copy_provider(root, frozen[condition], provider)
    indexed = {label: {case.name: case for case in cases} for label, cases in selected.items()}
    if (set(indexed["baseline"]) != set(indexed["candidate"])
            or any(len(indexed[label]) != len(selected[label]) for label in indexed)):
        raise ValueError("warm pair requires equal unique exact case IDs")
    for pair, order in enumerate(ORDER):
        for name in indexed["baseline"]:
            cases = {label: indexed[label][name] for label in order}
            rows = {}
            homes = {}
            for condition in order:
                case = cases[condition]
                print(f"warm pair {pair + 1}: {condition} {case.name}", file=sys.stderr, flush=True)
                row = {"pair": pair, "condition": condition, "case": case.name,
                       "expected_decision": case.expected_decision,
                       "contract": (case.fixture_metadata or {}).get("contract"),
                       "fixture_metadata": case.fixture_metadata,
                       "input_sha256": hashlib.sha256(case.payload).hexdigest()}
                report["warm"].append(row)
                rows[condition] = row
                homes[condition] = temporary / f"pair-{pair}" / condition / case.name
            warm_pair_run(cases, frozen, repo, homes, samples, warmups, pair, rows)
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
                       "contract": (case.fixture_metadata or {}).get("contract"),
                       "fixture_metadata": case.fixture_metadata,
                       "input_sha256": hashlib.sha256(case.payload).hexdigest(),
                       "copy_id": identity + "/source", "home_id": identity + "/home",
                       "bytecode_before": len(list(source.rglob("*.pyc")))}
                report["cold"].append(row)
                current = prepared_case(case, source, cold=True, home=home)
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
            current = prepared_case(case, frozen[condition], home=home)
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
            row = {"condition": condition, "case": case.name, "ceiling_ms": 500,
                   "expected_decision": case.expected_decision,
                   "input_sha256": hashlib.sha256(case.payload).hexdigest(),
                   "contract": (case.fixture_metadata or {}).get("contract"),
                   "fixture_metadata": case.fixture_metadata}
            report["resources"].append(row)
            home = temporary / condition / case.name
            warm_run(case, frozen, repo, home, samples, warmups, row)
            current = prepared_case(case, frozen, home=home)
            env = high_rate.invocation_environment(current, home)
            memory, rss = collect_macos_rss([sys.executable, str(current.script)],
                                          lambda argv: resources.checked_run(argv, current.payload, env,
                                                                             case.name.split(".", 1)[0],
                                                                             case.expected_decision, cwd=repo, contract=(case.fixture_metadata or {}).get("contract")))
            if rss is None:
                raise ValueError("native macOS time did not report peak RSS: " + memory.stderr.decode("utf-8", errors="replace")[:512])
            row["peak_rss_bytes"] = rss
            row["logging"] = verify_logging(home, current, 2 + warmups + samples)
            logging_error(row["logging"])
            row["ceiling_met"] = max(row["first_process_ms"], *row["samples_ms"]) <= 500


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-root", type=Path, help=f"git archive of {BASELINE_REF}")
    parser.add_argument("--baseline-ref", default=BASELINE_REF, help="Git revision used to verify the baseline runtime archive")
    parser.add_argument("--fixture-set", choices=FIXTURE_SETS, default="historical-v1")
    parser.add_argument("--expectations", type=Path, help="reviewed hash-pinned per-condition expectations")
    parser.add_argument("--candidate-root", type=Path, help="frozen final candidate checkout")
    parser.add_argument("--baseline-condition", choices=("baseline", "candidate"), default="baseline", help="reviewed reference expectation condition")
    parser.add_argument("--comparison-reference", choices=("original", "equivalent"), default="original", help="original baseline or fixed equivalent-work candidate reference")
    parser.add_argument("--candidate-condition", choices=("baseline", "candidate"), default="candidate", help="baseline observations for an A/A check")
    parser.add_argument("--mode", choices=("timing", "resources"), default="timing")
    parser.add_argument("--case", action="append", default=[], help="exact case name; repeat this flag for an isolated repeat")
    parser.add_argument("--output", type=Path, help="new evidence JSON path; existing evidence is never replaced")
    parser.add_argument("--list", action="store_true", help="list maintained cases and explicit condition expectations")
    parser.add_argument("--mechanics-only", action="store_true", help="two samples and no warmups; NOT release evidence")
    args = parser.parse_args()
    if ((args.comparison_reference == "equivalent" and (args.baseline_condition != "candidate" or args.candidate_condition != "candidate"))
            or (args.comparison_reference == "original" and args.baseline_condition != "baseline")):
        parser.error("comparison reference and expectation condition mismatch")
    if args.fixture_set != "historical-v1" and args.expectations is None:
        parser.error("--expectations is required for an explicit new fixture set")
    if args.list:
        try:
            candidate = selected_cases(Path("."), args.candidate_condition, args.case, args.mode, args.fixture_set, args.expectations)
            baseline = {case.name: case for case in selected_cases(Path("."), args.baseline_condition, args.case, args.mode, args.fixture_set, args.expectations)}
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
        selected = {condition: selected_cases(root, args.candidate_condition if condition == "candidate" else args.baseline_condition, args.case, args.mode, args.fixture_set, args.expectations) for condition, root in roots.items()}
        before = {condition: resources.fingerprints(root) for condition, root in roots.items()}
        if not args.mechanics_only and before["baseline"] != baseline_fingerprints(args.baseline_ref):
            raise ValueError("baseline runtime fingerprints do not match " + args.baseline_ref)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    partition = None
    if args.fixture_set == "file-operations-v2":
        document = json.loads(args.expectations.read_text(encoding="utf-8"))
        partition = document["fixture_sets"][args.fixture_set]["throughput_partition"]
    counts = (2, 0, 2) if args.mechanics_only else (25, 3, 25)
    report = {"baseline_reference": args.baseline_ref, "fixture_set": args.fixture_set, "mode": args.mode,
              "release_acceptance_eligible": not args.mechanics_only and not args.case and args.candidate_condition == "candidate",
              "candidate_expectation_condition": args.candidate_condition,
              "baseline_expectation_condition": args.baseline_condition,
              "comparison_reference": args.comparison_reference,
              "throughput_partition": {key: list(value) for key, value in partition.items()} if partition is not None else None,
              "environment": {"platform": platform.platform(), "machine": platform.machine(),
                              "python": sys.version, "python_executable": sys.executable,
                              "git": subprocess.check_output(["git", "--version"], text=True).strip()},
              "method": {"samples": counts[0], "warmups": counts[1], "cold_launches_per_case_condition": counts[2],
                         "warm_order": ORDER, "exact_case_filter": args.case,
                         "warm_schedule": "pair, exact case, call index, source: adjacent baseline/candidate launches in pair 1; candidate/baseline in pair 2",
                         "clock": "maintained high-rate invoke: whole Python subprocess only",
                         "logging": "OBSERVABILITY_TESTING=1; disposable homes retained until completed-log verification; validation outside elapsed",
                         "cold": "independent fresh provider copy/home per launch; zero provider bytecode; OS and stdlib caches uncleared",
                         "warm_bytecode": "normal Python bytecode reuse within disposable warm/resource copies after first process",
                         "resources": "maintained resource fixtures and checked_run; separate native /usr/bin/time -l launch; RSS bytes",
                         "repeat_policy": "retain original failures; exact isolated repeats require separate output and an attributable explanation before acceptance"},
              "script_sha256": before,
              "baseline_archive_verified": not args.mechanics_only,
              "harness_sha256": harness_fingerprints(args.expectations),
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
            report["sources_unchanged"] = before == after and report["harness_sha256"] == harness_fingerprints(args.expectations)
            if not report["sources_unchanged"]:
                report["errors"].append("hook or harness sources changed during verification")
                report["script_sha256_after"] = after
        except OSError as exc:
            report["sources_unchanged"] = False
            report["errors"].append(f"cannot recheck frozen source: {exc}")
        try:
            validate_measurements(report, selected, args.mode, *counts,
                                  reference=args.comparison_reference, partition=partition)
        except (ValueError, KeyError) as exc:
            report["errors"].append(str(exc))
        report["gate_partition"] = {
            "gated_comparisons": sum(row.get("classification", "gated") == "gated" for row in report.get("comparisons", [])),
            "changed_workload_observations": sum(row.get("classification") == "changed-workload-observation" for row in report.get("comparisons", []))}
        passed = not report["errors"] and all(row["met"] is not False for row in report.get("comparisons", [])) and all(row.get("ceiling_met", False) for row in report["resources"])
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
