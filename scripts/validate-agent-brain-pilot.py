#!/usr/bin/env python3
"""Offline, standard-library pilot validation. Never starts a provider/model."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import sys

MAX_BYTES = 32 * 1024 * 1024
WORKLOAD = Path(__file__).resolve().parent / "fixtures/agent-brain/pilot-workload.json"


def fail(message):
    raise ValueError(message)


def keys(value, expected, label):
    if type(value) is not dict or set(value) != set(expected):
        fail(label + " has missing or unknown fields")


def number(value, label, *, integer=False):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0 or (integer and type(value) is not int):
        fail(label + " must be a finite nonnegative " + ("integer" if integer else "number"))


def text(value, label):
    if type(value) is not str or not value.strip():
        fail(label + " must be a nonempty string")


def unique(values, label):
    if type(values) is not list or len(values) != len(set(values)):
        fail(label + " must be a unique list")
    for value in values:
        text(value, label)


def read(path):
    data = path.read_bytes()
    if len(data) > MAX_BYTES:
        fail("input exceeds the 32 MiB limit")
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                fail("duplicate JSON key: " + key)
            result[key] = value
        return result
    def floating(value):
        parsed = float(value)
        if not math.isfinite(parsed):
            fail("nonfinite JSON number")
        return parsed
    return json.loads(data.decode("utf-8"), object_pairs_hook=pairs,
        parse_float=floating, parse_constant=lambda _: fail("nonfinite JSON constant"))


def artifact_path(root, relative):
    text(relative, "artifact path")
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        fail("artifact path must remain below the declared artifact root")
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            fail("linked artifact paths are unavailable")
    return current


def validate_spec(spec):
    measured = spec.get("kind") == "measured_pilot" if type(spec) is dict else False
    keys(spec, {"schema_version", "kind", "freeze_id", "checks", "cohorts"} | ({"workload_manifest_revision"} if measured else set()), "specification")
    if type(spec["schema_version"]) is not int or spec["schema_version"] != 1 or spec["kind"] not in ("offline_calculator_fixture", "measured_pilot"):
        fail("unsupported specification")
    text(spec["freeze_id"], "freeze_id")
    manifest = None
    if measured:
        manifest = read(WORKLOAD)
        if spec["workload_manifest_revision"] != hashlib.sha256(WORKLOAD.read_bytes()).hexdigest() or spec["freeze_id"] != manifest["freeze_id"] or spec["checks"] != manifest["checks"]:
            fail("measured specification must bind the independent accepted frozen workload/check manifest")
        if (type(spec["cohorts"]) is not list or any(type(c) is not dict for c in spec["cohorts"])
                or [c.get("id") for c in spec["cohorts"]] != manifest["cohort_ids"]):
            fail("measured specification must retain every frozen cohort, including unsupported/incomplete paths")
    checks = {}
    if type(spec["checks"]) is not list or not spec["checks"]:
        fail("predetermined checks are required")
    for check in spec["checks"]:
        keys(check, {"id", "kind", "path", "expected", "contract"}, "check")
        for field in ("id", "path", "contract"):
            text(check[field], field)
        artifact_path(Path("/"), check["path"])
        if check["id"] in checks or check["kind"] not in ("contains", "absent", "sha256", "independent_human"):
            fail("duplicate or unsupported predetermined check")
        text(check["expected"], "independently predetermined expected assertion")
        checks[check["id"]] = check
    cohorts = {}
    if type(spec["cohorts"]) is not list or not spec["cohorts"]:
        fail("frozen cohorts are required")
    for cohort in spec["cohorts"]:
        keys(cohort, {"id", "configuration", "tokenizer", "window", "model", "settings", "knowledge_revision", "prerequisites", "schedule", "required_checks", "critical_schedule"}, "cohort")
        for field in ("id", "configuration", "tokenizer", "window", "model", "settings", "knowledge_revision"):
            text(cohort[field], field)
        if cohort["id"] in cohorts:
            fail("duplicate cohort")
        keys(cohort["prerequisites"], {"provider_build", "native_certification", "delivery_observation", "tokenizer_validation"}, "prerequisites")
        for value in cohort["prerequisites"].values():
            if measured:
                keys(value, {"status", "identity", "evidence"}, "measured prerequisite")
                if value["status"] == "observed":
                    text(value["identity"], "observed prerequisite identity")
                    keys(value["evidence"], {"path", "revision"}, "observed prerequisite evidence")
                    artifact_path(Path("/"), value["evidence"]["path"])
                    text(value["evidence"]["revision"], "evidence revision")
                elif value["status"] not in ("pending", "unavailable", "unsupported") or value["identity"] is not None or value["evidence"] is not None:
                    fail("unobserved prerequisite cannot carry native authority")
            elif value is not None:
                text(value, "prerequisite")
        unique(cohort["required_checks"], "required checks")
        if not cohort["required_checks"] or set(cohort["required_checks"]) - checks.keys():
            fail("missing or unknown required checks")
        if type(cohort["schedule"]) is not list or not cohort["schedule"]:
            fail("frozen ordered schedule required")
        ids = set()
        for pair in cohort["schedule"]:
            keys(pair, {"id", "variant", "order", "checks"}, "scheduled pair")
            text(pair["id"], "pair id")
            text(pair["variant"], "variant")
            if pair["id"] in ids or pair["order"] not in ("baseline_first", "candidate_first"):
                fail("duplicate pair or invalid order")
            ids.add(pair["id"])
            unique(pair["checks"], "pair checks")
            if not pair["checks"] or set(pair["checks"]) - set(cohort["required_checks"]):
                fail("pair requires predetermined cohort checks")
        critical_ids = set()
        if type(cohort["critical_schedule"]) is not list:
            fail("critical schedule must be a list")
        for critical in cohort["critical_schedule"]:
            keys(critical, {"id", "check_id", "pair_id"}, "critical schedule")
            text(critical["id"], "critical id")
            if critical["id"] in critical_ids or critical["check_id"] not in checks:
                fail("duplicate or unknown critical check")
            critical_ids.add(critical["id"])
            if critical["pair_id"] is not None and critical["pair_id"] not in ids:
                fail("critical overlap references unknown pair")
        if spec["kind"] == "measured_pilot" and len(ids) < 60:
            fail("measured cohort requires at least 60 frozen pairs")
        if spec["kind"] == "measured_pilot":
            if cohort["schedule"] != manifest["schedule"] or cohort["critical_schedule"] != manifest["critical_schedule"] or cohort["required_checks"] != [c["id"] for c in manifest["checks"]]:
                fail("incomplete or altered ten-variant/four-repeat/two-cycle/fresh-session/native critical matrix")
            expected_knowledge = hashlib.sha256(json.dumps(manifest["knowledge_inventory"], sort_keys=True).encode()).hexdigest()
            if cohort["knowledge_revision"] != expected_knowledge:
                fail("knowledge differs from the equivalent full frozen pilot inventory")
            counts = {c["check_id"]: sum(x["check_id"] == c["check_id"] for x in cohort["critical_schedule"]) for c in cohort["critical_schedule"]}
            if not counts or any(count != 3 for count in counts.values()):
                fail("every claimed native critical case requires exactly three frozen repetitions")
        cohorts[cohort["id"]] = cohort
    return checks, cohorts


def prerequisite_checks(spec, cohort, root):
    incomplete = []
    if spec["kind"] == "offline_calculator_fixture":
        return [name for name, value in cohort["prerequisites"].items() if value is None]
    provider = cohort["id"].split("-")[0]
    mode = "desktop" if "desktop" in cohort["id"] else "cli"
    kinds = {"provider_build": "passive_provider_metadata", "native_certification": "independent_native_certification",
        "delivery_observation": "validated_native_delivery_capture", "tokenizer_validation": "validated_guidance_tokenizer"}
    build = cohort["prerequisites"]["provider_build"]["identity"]
    for name, value in cohort["prerequisites"].items():
        if value["status"] != "observed":
            incomplete.append(name + "/" + value["status"])
            continue
        pin = value["evidence"]
        path = artifact_path(root, pin["path"])
        if not path.is_file():
            incomplete.append(name + "/missing_evidence")
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != pin["revision"]:
            fail("stale prerequisite evidence")
        proof = read(path)
        expected = {"schema_version": 1, "kind": kinds[name], "status": "observed", "identity": value["identity"],
            "cohort": cohort["id"], "provider": provider, "provider_version": build, "entry_mode": mode,
            "configuration": cohort["configuration"], "model": cohort["model"], "settings": cohort["settings"],
            "tokenizer": cohort["tokenizer"], "workload_manifest_revision": spec["workload_manifest_revision"]}
        keys(proof, set(expected) | {"independent_observer", "observation_method", "source_artifacts"}, "observed prerequisite proof")
        if any(type(proof[k]) is not type(v) or proof[k] != v for k, v in expected.items()):
            fail("prerequisite does not match frozen native/model/configuration/tokenizer identity")
        for field in ("independent_observer", "observation_method"):
            text(proof[field], field)
        for value in (build, cohort["model"], cohort["settings"], cohort["configuration"], cohort["tokenizer"], proof["observation_method"]):
            if value is None or any(word in value.lower() for word in ("fixture", "pending", "not-a-native", "offline-only")):
                fail("fixture or unobserved declarations cannot establish measured native prerequisites")
        if type(proof["source_artifacts"]) is not dict or not proof["source_artifacts"]:
            fail("observed prerequisite requires preserved actual observation artifacts")
        for relative, revision in proof["source_artifacts"].items():
            source = artifact_path(root, relative)
            if not source.is_file():
                incomplete.append(name + "/missing_observation")
            elif hashlib.sha256(source.read_bytes()).hexdigest() != revision:
                fail("actual prerequisite observation changed")
    return incomplete


def validate_arm(arm, cohort, check_ids):
    keys(arm, {"model", "settings", "knowledge_revision", "guidance_tokens", "duration_seconds", "retrieval_seconds", "delivery_complete", "window_complete", "independent_review", "task_outcome", "checks", "usage", "stage_boundaries", "evidence"}, "arm")
    for field in ("model", "settings", "knowledge_revision"):
        if arm[field] != cohort[field]:
            fail("nonequivalent or stale arm " + field)
    for field in ("guidance_tokens", "duration_seconds", "retrieval_seconds"):
        if arm[field] is not None:
            number(arm[field], field, integer=field == "guidance_tokens")
    for field in ("delivery_complete", "window_complete", "independent_review"):
        if type(arm[field]) is not bool:
            fail(field + " must be a boolean observation")
    if arm["task_outcome"] not in ("passed", "failed", "incomplete"):
        fail("invalid task outcome")
    keys(arm["checks"], check_ids, "observed checks")
    if any(value not in ("passed", "failed", "incomplete") for value in arm["checks"].values()):
        fail("invalid check outcome")
    keys(arm["usage"], {"status", "value", "unit"}, "task usage")
    usage = arm["usage"]
    if usage["status"] == "observed":
        number(usage["value"], "provider task usage")
        if usage["unit"] not in ("credits", "input_tokens", "total_tokens", "USD"):
            fail("usage must be task-scoped, never account percentages")
    elif usage != {"status": "unavailable", "value": None, "unit": None}:
        fail("unavailable usage must be explicit")
    unique(arm["stage_boundaries"], "stage boundaries")
    if not arm["stage_boundaries"] or arm["stage_boundaries"][0] != "arrival" or arm["stage_boundaries"][-1] != "settled":
        fail("task window must include arrival through settled maintenance/recovery")
    keys(arm["evidence"], {"snapshot", "artifacts", "review"}, "arm evidence")
    keys(arm["evidence"]["artifacts"], check_ids, "snapshot artifact pins")
    keys(arm["evidence"]["review"], {"path", "revision", "reviewer"}, "independent review reference")
    text(arm["evidence"]["review"]["reviewer"], "attributable independent reviewer")


def observed_quality(root, checks, pair, arm, check_ids, rubric_revision):
    value = pair[arm]
    evidence = value["evidence"]
    snapshot = artifact_path(root, evidence["snapshot"])
    outcomes = {}
    for check_id in check_ids:
        check = checks[check_id]
        path = artifact_path(snapshot, check["path"])
        pin = evidence["artifacts"][check_id]
        text(pin, "artifact revision")
        if not path.is_file():
            outcomes[check_id] = "incomplete"
            continue
        data = path.read_bytes()
        if len(data) > MAX_BYTES or hashlib.sha256(data).hexdigest() != pin:
            fail("observation artifact no longer matches its pinned snapshot")
        if check["kind"] == "independent_human":
            outcomes[check_id] = value["checks"][check_id]
        else:
            passed = (hashlib.sha256(data).hexdigest() == check["expected"] if check["kind"] == "sha256" else
                (check["expected"] in data.decode("utf-8")) == (check["kind"] == "contains"))
            outcomes[check_id] = "passed" if passed else "failed"
    review_ref = evidence["review"]
    review_path = artifact_path(root, review_ref["path"])
    if not review_path.is_file():
        outcomes["independent_review"] = "incomplete"
    else:
        if hashlib.sha256(review_path.read_bytes()).hexdigest() != review_ref["revision"]:
            fail("independent review evidence changed")
        review = read(review_path)
        expected = {"schema_version": 1, "pair_id": pair["pair_id"], "arm": arm,
            "reviewer": review_ref["reviewer"], "kind": "independent_human", "rubric_revision": rubric_revision,
            "snapshot": evidence["snapshot"], "artifacts": evidence["artifacts"]}
        keys(review, set(expected) | {"outcome", "checks"}, "review evidence")
        if any(type(review[k]) is not type(v) or review[k] != v for k, v in expected.items()):
            fail("review does not bind this arm, snapshot or frozen independent rubric")
        keys(review["checks"], check_ids, "reviewed checks")
        if review["checks"] != value["checks"] or review["outcome"] not in ("passed", "failed", "incomplete"):
            fail("reviewed outcome differs from observation")
        outcomes["independent_review"] = review["outcome"]
    return outcomes


def distribution(values):
    if any(value is None for value in values) or not values:
        return {"median": None, "p95": None}
    ordered = sorted(values)
    return {"median": statistics.median(ordered), "p95": ordered[math.ceil(.95 * len(ordered)) - 1]}


def usage_total(arms):
    values = [arm["usage"] for arm in arms]
    observed = [value for value in values if value["status"] == "observed"]
    units = {value["unit"] for value in observed}
    if len(units) > 1:
        fail("provider task usage units differ within an arm")
    if not observed:
        return {"status": "unavailable", "total": None, "unit": None}
    if observed[0]["unit"] == "input_tokens":
        return {"status": "incomplete", "total": None, "unit": None,
            "observed_input_tokens": sum(value["value"] for value in observed)}
    return {"status": "observed" if len(observed) == len(values) else "incomplete",
        "total": sum(value["value"] for value in observed), "unit": observed[0]["unit"]}


def validate_probe_metrics(metrics):
    keys(metrics, {"task_id", "session_id", "executor", "guidance_tokens", "duration_seconds", "retrieval_seconds", "delivery_complete", "window_complete", "usage", "stage_boundaries"}, "standalone task metrics")
    text(metrics["task_id"], "standalone task id")
    text(metrics["session_id"], "standalone session id")
    if metrics["executor"] not in ("primary", "child"):
        fail("unknown standalone executor")
    for field in ("guidance_tokens", "duration_seconds", "retrieval_seconds"):
        if metrics[field] is not None:
            number(metrics[field], field, integer=field == "guidance_tokens")
    for field in ("delivery_complete", "window_complete"):
        if type(metrics[field]) is not bool:
            fail("standalone visibility/window must be explicit")
    usage = metrics["usage"]
    keys(usage, {"status", "value", "unit"}, "standalone usage")
    if usage["status"] == "observed":
        number(usage["value"], "standalone task usage")
        if usage["unit"] not in ("credits", "input_tokens", "total_tokens", "USD"):
            fail("standalone usage must be task-scoped")
    elif usage != {"status": "unavailable", "value": None, "unit": None}:
        fail("standalone unavailable usage must be explicit")
    unique(metrics["stage_boundaries"], "standalone stage boundaries")
    if not metrics["stage_boundaries"] or metrics["stage_boundaries"][0] != "arrival" or metrics["stage_boundaries"][-1] != "settled":
        fail("standalone window must retain maintenance and pending recovery")


def calculate(spec, records, revision, root):
    checks, cohorts = validate_spec(spec)
    keys(records, {"schema_version", "spec_revision", "observations", "critical_observations"}, "records")
    if type(records["schema_version"]) is not int or records["schema_version"] != 1 or records["spec_revision"] != revision:
        fail("unknown/stale records specification revision")
    if type(records["observations"]) is not list:
        fail("observations must be a list")
    grouped = {key: [] for key in cohorts}
    snapshot_roots = set()
    rubric_revision = hashlib.sha256(json.dumps(spec["checks"], sort_keys=True).encode()).hexdigest()
    for pair in records["observations"]:
        keys(pair, {"cohort", "pair_id", "variant", "order", "configuration", "tokenizer", "window", "system_caused_regression", "baseline", "candidate"}, "pair")
        if pair["cohort"] not in cohorts:
            fail("unknown cohort")
        cohort = cohorts[pair["cohort"]]
        for field in ("configuration", "tokenizer", "window"):
            if pair[field] != cohort[field]:
                fail("unfrozen or stale " + field)
        if type(pair["system_caused_regression"]) is not bool:
            fail("regression attribution must be explicit")
        scheduled = next((p for p in cohort["schedule"] if p["id"] == pair["pair_id"]), None)
        if scheduled is None:
            fail("unknown scheduled pair")
        for arm in ("baseline", "candidate"):
            validate_arm(pair[arm], cohort, scheduled["checks"])
            snapshot = artifact_path(root, pair[arm]["evidence"]["snapshot"])
            if snapshot in snapshot_roots:
                fail("each observation/arm requires a distinct preserved snapshot")
            snapshot_roots.add(snapshot)
        grouped[pair["cohort"]].append(pair)
    if type(records["critical_observations"]) is not list:
        fail("critical observations must be a list")
    critical_groups = {key: [] for key in cohorts}
    manifest = read(WORKLOAD) if spec["kind"] == "measured_pilot" else None
    probe_task_keys = set()
    probe_session_owners = {}
    for critical in records["critical_observations"]:
        keys(critical, {"cohort", "id", "check_id", "pair_id", "outcome", "evidence_path", "evidence_revision", "reviewer", "task_metrics"}, "critical observation")
        if critical["cohort"] not in cohorts or critical["outcome"] not in ("passed", "failed", "incomplete"):
            fail("unknown critical cohort/outcome")
        if critical["pair_id"] is None:
            metrics = critical["task_metrics"]
            if type(metrics) is not list or not metrics:
                fail("standalone critical case requires every predetermined executor/task window")
            for value in metrics:
                validate_probe_metrics(value)
                task_key = (critical["cohort"], value["task_id"])
                session_key = (critical["cohort"], value["session_id"])
                if task_key in probe_task_keys or probe_session_owners.get(session_key, critical["id"]) != critical["id"]:
                    fail("standalone repetitions cannot reuse actual task/session executor windows")
                probe_task_keys.add(task_key)
                probe_session_owners[session_key] = critical["id"]
            if manifest and (len(metrics) != manifest["probe_execution_counts"].get(critical["id"]) or len({m["session_id"] for m in metrics}) != manifest["probe_session_counts"].get(critical["id"])):
                fail("standalone critical execution/session counts differ from frozen budget")
            if len({m["task_id"] for m in metrics}) != len(metrics):
                fail("duplicate standalone task executor window")
            if manifest:
                roles = [m["executor"] for m in metrics]
                if critical["check_id"] in ("native-child-delivery", "native-missing-child-hooks"):
                    if roles != ["primary", "child"]:
                        fail("selected child probe must retain both parent and child executor measurements")
                elif any(role != "primary" for role in roles):
                    fail("unexpected child executor outside the frozen child probes")
        elif critical["task_metrics"] is not None:
            fail("overlapping critical checks cannot double-count workload task usage")
        path = artifact_path(root, critical["evidence_path"])
        if not path.is_file():
            critical = dict(critical, outcome="incomplete")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != critical["evidence_revision"]:
            fail("native critical evidence changed")
        else:
            text(critical["reviewer"], "native independent reviewer")
            proof = read(path)
            expected_proof = {key: critical[key] for key in ("cohort", "id", "check_id", "pair_id", "outcome", "reviewer")}
            expected_proof.update(schema_version=1, kind="independent_native_observation",
                configuration=cohorts[critical["cohort"]]["configuration"], spec_revision=revision,
                rubric_revision=rubric_revision, task_metrics=critical["task_metrics"])
            overlap = next((p for p in grouped[critical["cohort"]] if p["pair_id"] == critical["pair_id"]), None)
            expected_proof["overlap"] = None if critical["pair_id"] is None else {
                "pair_id": critical["pair_id"], "window": cohorts[critical["cohort"]]["window"],
                "snapshot": overlap["candidate"]["evidence"]["snapshot"],
                "artifacts": overlap["candidate"]["evidence"]["artifacts"]} if overlap else "missing_pair"
            keys(proof, set(expected_proof) | {"source_artifacts", "review_note"}, "native critical review")
            if any(json.dumps(proof[key], sort_keys=True, allow_nan=False) != json.dumps(value, sort_keys=True, allow_nan=False) for key, value in expected_proof.items()):
                fail("native review does not bind frozen critical case/configuration/rubric")
            text(proof["review_note"], "independent native review note")
            if type(proof["source_artifacts"]) is not dict or not proof["source_artifacts"]:
                fail("native critical review requires actual preserved event/delivery/artifact traces")
            for relative, revision in proof["source_artifacts"].items():
                source = artifact_path(root, relative)
                if not source.is_file():
                    critical = dict(critical, outcome="incomplete")
                elif hashlib.sha256(source.read_bytes()).hexdigest() != revision:
                    fail("native critical observation artifact changed")
        critical_groups[critical["cohort"]].append(critical)
    reports = []
    for identity, cohort in cohorts.items():
        pairs = grouped[identity]
        if pairs and [(p["pair_id"], p["variant"], p["order"]) for p in pairs] != [(p["id"], p["variant"], p["order"]) for p in cohort["schedule"]]:
            fail("partial, duplicated, mismatched or reordered cohort")
        incomplete = prerequisite_checks(spec, cohort, root)
        critical = critical_groups[identity]
        expected_critical = [(c["id"], c["check_id"], c["pair_id"]) for c in cohort["critical_schedule"]]
        if critical and [(c["id"], c["check_id"], c["pair_id"]) for c in critical] != expected_critical:
            fail("partial, mismatched or duplicated critical cohort")
        if not pairs:
            reports.append({"id": identity, "status": "incomplete", "incomplete_checks": incomplete + ["missing_cohort"], "pairs": [], "calculator_gates": "incomplete"})
            continue
        quality = "passed"
        if expected_critical and not critical:
            incomplete.append("missing_native_critical_observations")
        if any(c["outcome"] == "failed" for c in critical):
            quality = "failed"
        if any(c["outcome"] == "incomplete" for c in critical):
            incomplete.append("native_critical_evidence")
        probes = [m for c in critical if c["pair_id"] is None for m in c["task_metrics"]]
        if any(not p["delivery_complete"] or not p["window_complete"] or any(p[k] is None for k in ("guidance_tokens", "duration_seconds", "retrieval_seconds")) for p in probes):
            incomplete.append("standalone_probe_measurement")
        artifact_checks = {}
        for pair in pairs:
            for arm in ("baseline", "candidate"):
                value = pair[arm]
                check_ids = next(p["checks"] for p in cohort["schedule"] if p["id"] == pair["pair_id"])
                outcomes_by_id = observed_quality(root, checks, pair, arm, check_ids, rubric_revision)
                artifact_checks[pair["pair_id"] + "/" + arm] = outcomes_by_id
                if any(not value[name] for name in ("delivery_complete", "window_complete", "independent_review")) or any(value[name] is None for name in ("guidance_tokens", "duration_seconds", "retrieval_seconds")):
                    incomplete.append(pair["pair_id"] + "/" + arm + "/measurement_or_review")
                outcomes = [value["task_outcome"], *value["checks"].values(), *outcomes_by_id.values()]
                if "failed" in outcomes:
                    quality = "failed"
                elif "incomplete" in outcomes:
                    incomplete.append(pair["pair_id"] + "/" + arm + "/quality")
            if pair["system_caused_regression"]:
                quality = "failed"
        arms = {arm: [pair[arm] for pair in pairs] for arm in ("baseline", "candidate")}
        distributions = {arm: {name: distribution([value[name] for value in values]) for name in
            ("guidance_tokens", "duration_seconds", "retrieval_seconds")} for arm, values in arms.items()}
        gates = "failed" if quality == "failed" else "incomplete" if incomplete else "met"
        if gates == "met":
            b, c = distributions["baseline"], distributions["candidate"]
            passed = (c["guidance_tokens"]["median"] <= .75 * b["guidance_tokens"]["median"] and
                c["guidance_tokens"]["p95"] <= b["guidance_tokens"]["p95"] and
                distribution([max(0, p["candidate"]["retrieval_seconds"] - p["baseline"]["retrieval_seconds"]) for p in pairs])["p95"] <= 5 and
                c["duration_seconds"]["p95"] <= 1.2 * b["duration_seconds"]["p95"])
            gates = "met" if passed else "failed"
        reports.append({"id": identity, "status": "complete" if not incomplete else "incomplete",
            "incomplete_checks": sorted(set(incomplete)), "quality": quality if not incomplete or quality == "failed" else "incomplete",
            "artifact_checks": artifact_checks, "calculator_gates": gates, **distributions,
            "added_blocking_retrieval": distribution([None if any(p[a]["retrieval_seconds"] is None for a in arms) else max(0, p["candidate"]["retrieval_seconds"] - p["baseline"]["retrieval_seconds"]) for p in pairs]),
            "usage": {arm: usage_total(values + (probes if arm == "candidate" else [])) for arm, values in arms.items()},
            "paired_usage": {arm: usage_total(values) for arm, values in arms.items()},
            "standalone_probes": probes, "pairs": pairs,
            "critical_observations": critical})
    product = "incomplete" if spec["kind"] == "offline_calculator_fixture" or any(r["calculator_gates"] == "incomplete" for r in reports) else "failed" if any(r["calculator_gates"] == "failed" for r in reports) else "met"
    return {"schema_version": 1, "freeze_id": spec["freeze_id"], "spec_revision": revision,
        "evidence_kind": spec["kind"], "product_acceptance": product, "cohorts": reports,
        "limitations": ["Empirical medians/nearest-rank p95, no population confidence claim.",
            "Process fixtures do not prove native consumption, OS/power-loss durability or accepted product benefit."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.artifact_root.is_symlink() or not args.artifact_root.is_dir():
            fail("artifact root must be an existing unlinked directory")
        spec = read(args.spec)
        report = calculate(spec, read(args.records), hashlib.sha256(args.spec.read_bytes()).hexdigest(), args.artifact_root.resolve())
        write_utf8(sys.stdout, json.dumps(report, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n")
        return 0
    except (ValueError, OSError, UnicodeError, TypeError, KeyError, OverflowError) as exc:
        try:
            write_utf8(sys.stderr, "pilot validation: " + str(exc) + "\n")
        except OSError:
            pass
        return 2


def write_utf8(stream, value):
    # Direct bytes avoid ambient cp1252 and shutdown retrying a broken buffered
    # pipe. A partial or failed report is never a successful calculation.
    data = value.encode("utf-8")
    while data:
        count = os.write(stream.fileno(), data)
        if count <= 0:
            raise OSError("report output is incomplete")
        data = data[count:]


if __name__ == "__main__":
    raise SystemExit(main())
