"""Independent assertions for controlled scheduler/worker observations."""

import math

REPORT_FIELDS = {"owner", "pinned_revision", "completed_evidence", "blocker", "deadline", "next_action"}


def _present(mapping, key):
    return key in mapping and mapping[key] is not None and mapping[key] != ""


def _finite_number(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def grade_turn(observation):
    """Grade observable outcome fields; never trust a fixture's pass flag."""
    errors = []
    if not isinstance(observation, dict):
        return ["missing scheduler observation"]
    before = observation.get("before")
    after = observation.get("after")
    if not isinstance(before, dict) or not isinstance(after, dict):
        return ["missing before/after scheduler state"]

    for label, state in (("before", before), ("after", after)):
        if not _present(state, "id"):
            errors.append(f"missing assignment id in {label} scheduler state")
        if not _present(state, "phase"):
            errors.append(f"missing scheduler phase in {label} state")
        if not _finite_number(state.get("deadline")):
            errors.append(f"missing or invalid deadline in {label} scheduler state")
        if state.get("phase") in ("checkpoint", "decision") and not _finite_number(state.get("phase_deadline")):
            errors.append(f"missing or invalid phase deadline in {label} scheduler state")
    if not _finite_number(observation.get("at")):
        errors.append("missing or invalid observation time")
    actions = observation.get("actions")
    if not isinstance(actions, list):
        errors.append("missing or invalid action list")
    elif any(not isinstance(action, dict) for action in actions):
        errors.append("action list contains a non-object observation")
    if errors:
        return errors

    phase = before.get("phase")
    now = observation["at"]
    deadline_event = None
    if phase == "running" and now >= before.get("deadline", float("inf")):
        deadline_event = "deadline_expired"
    elif phase in ("checkpoint", "decision") and now >= before.get("phase_deadline", float("inf")):
        deadline_event = "checkpoint_expired"
    elif phase == "extended" and now >= before.get("deadline", float("inf")):
        deadline_event = "extension_expired"
    if deadline_event is None:
        if before != after:
            errors.append("scheduler state changed before deadline")
        if observation.get("actions"):
            errors.append("unexpected scheduler action before deadline")
        if observation.get("parent_status_lookups"):
            errors.append("unnecessary parent status lookup before deadline")
    else:
        expected_id = before.get("id")
        events = [a for a in actions if a.get("type") == deadline_event and a.get("assignment") == expected_id]
        if not events:
            errors.append("correct phase deadline action missing")
    if observation.get("dispatches"):
        errors.append("unexpected dispatch during quiet wait")
    if observation.get("setup_reads"):
        errors.append("repeated setup during quiet wait")
    return errors


def grade_transfer(worker_alive, writer_alive, transfer_emitted):
    errors = []
    if not isinstance(worker_alive, bool):
        errors.append("worker state is unknown")
    if not isinstance(writer_alive, bool):
        errors.append("writer state is unknown")
    if errors:
        return errors
    if transfer_emitted and (worker_alive or writer_alive):
        errors.append("ownership transfer while worker or writer remains active")
    if not transfer_emitted and not worker_alive and not writer_alive:
        errors.append("safe shutdown did not reach transfer")
    return errors


def grade_continuity(first, second, worker_observation, replacement_observation, expected):
    errors = []
    observation_fields = (
        ("same-worker", worker_observation, {"worker_id": "worker id", "known_fact_returned": "setup fact"}),
        ("replacement", replacement_observation, {
            "worker_id": "replacement worker id",
            "environment": "handoff environment",
            "pinned_revision": "handoff revision",
            "evidence": "handoff evidence",
        }),
    )
    for label, observation, fields in observation_fields:
        if not isinstance(observation, dict):
            errors.append(f"missing {label} observation")
            continue
        for key, description in fields.items():
            if not _present(observation, key):
                errors.append(f"missing {description}")

    expected_fields = {
        "worker_id": "expected worker id",
        "known_fact": "expected setup fact",
        "replacement_id": "expected replacement worker id",
        "environment": "expected handoff environment",
        "pinned_revision": "expected handoff revision",
        "evidence": "expected handoff evidence",
    }
    if not isinstance(expected, dict):
        errors.append("missing expected continuity values")
        expected = {}
    for key, description in expected_fields.items():
        if not _present(expected, key):
            errors.append(f"missing {description}")

    same_worker = worker_observation if isinstance(worker_observation, dict) else {}
    replacement = replacement_observation if isinstance(replacement_observation, dict) else {}
    def differs(observed, key, expected_key):
        return (_present(observed, key) and _present(expected, expected_key)
                and observed[key] != expected[expected_key])

    if differs(same_worker, "worker_id", "worker_id"):
        errors.append("same-worker ID mismatch")
    if differs(same_worker, "known_fact_returned", "known_fact"):
        errors.append("same-worker follow-up did not recover the known setup fact")
    if differs(replacement, "worker_id", "replacement_id"):
        errors.append("replacement worker identity mismatch")
    for key in ("environment", "pinned_revision", "evidence"):
        if differs(replacement, key, key):
            errors.append(f"replacement handoff {key} mismatch")
    errors.extend(_grade_reports(first, second))
    return errors


def _grade_reports(first, second):
    errors = []
    for report in (first, second):
        if not isinstance(report, dict) or set(report) != REPORT_FIELDS:
            errors.append("report must contain exactly the six continuity fields")
            continue
        if any(report[k] in (None, "") for k in REPORT_FIELDS):
            errors.append("report has an empty required continuity field")
    if isinstance(first, dict) and isinstance(second, dict):
        if first.get("pinned_revision") != second.get("pinned_revision"):
            errors.append("pinned revision changed across reports")
        first_evidence = first.get("completed_evidence")
        second_evidence = second.get("completed_evidence")
        if isinstance(first_evidence, list) and isinstance(second_evidence, list):
            if not set(first_evidence).issubset(second_evidence):
                errors.append("second report dropped completed evidence")
        elif second_evidence != first_evidence and not (isinstance(second_evidence, str) and isinstance(first_evidence, str) and second_evidence.startswith(first_evidence + ";")):
            errors.append("second report dropped or rewrote completed evidence")
        if second.get("setup_dump") or second.get("setup_repeated"):
            errors.append("second report repeats setup instead of compact continuity")
    return errors
