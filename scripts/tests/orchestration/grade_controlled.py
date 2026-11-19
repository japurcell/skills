"""Independent assertions for controlled scheduler/worker observations."""

REPORT_FIELDS = {"owner", "pinned_revision", "completed_evidence", "blocker", "deadline", "next_action"}


def grade_turn(observation):
    """Grade observable outcome fields; never trust a fixture's pass flag."""
    errors = []
    before = observation.get("before")
    after = observation.get("after")
    if not isinstance(before, dict) or not isinstance(after, dict):
        errors.append("missing before/after scheduler state")
        return errors
    phase = before.get("phase")
    now = observation.get("at", 0)
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
        events = [a for a in observation.get("actions", []) if a.get("type") == deadline_event and a.get("assignment") == expected_id]
        if not events:
            errors.append("correct phase deadline action missing")
    if observation.get("dispatches"):
        errors.append("unexpected dispatch during quiet wait")
    if observation.get("setup_reads"):
        errors.append("repeated setup during quiet wait")
    return errors


def grade_transfer(worker_alive, writer_alive, transfer_emitted):
    errors = []
    if transfer_emitted and (worker_alive or writer_alive):
        errors.append("ownership transfer while worker or writer remains active")
    if not transfer_emitted and not worker_alive and not writer_alive:
        errors.append("safe shutdown did not reach transfer")
    return errors


def grade_continuity(first, second, worker_observation, replacement_observation, expected):
    errors = []
    if worker_observation.get("worker_id") != expected.get("worker_id") or worker_observation.get("known_fact_returned") != expected.get("known_fact"):
        errors.append("same-worker follow-up did not recover the known setup fact")
    if replacement_observation.get("worker_id") != expected.get("replacement_id"):
        errors.append("replacement worker identity mismatch")
    if any(replacement_observation.get(k) != expected.get(k) for k in ("environment", "pinned_revision", "evidence")):
        errors.append("replacement handoff lacks required context")
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
