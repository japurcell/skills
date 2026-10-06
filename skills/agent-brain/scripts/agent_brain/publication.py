"""Journaled exact-set publication and bounded next-event reconciliation."""
from __future__ import annotations

import os
from pathlib import Path
import time

from . import history
from .state import LifecycleError, digest, local_path, uid, write_private


def barrier(config, root: Path, name: str) -> None:
    """Controlled process barrier, enabled only by disposable protocol fixtures.

    Environment data can pause an already authorized operation, never issue
    authority or change proposed bytes. Native provider configurations ignore it.
    """
    for provider in config.providers.values():
        if not provider["enabled"] or provider["kind"] == "protocol_fixture":
            continue
        from .native import support_record
        if support_record(config, root, provider)["status"] != "offline_fixture":
            return
    selected = os.environ.get("AGENT_BRAIN_FIXTURE_BARRIER")
    if selected != name:
        return
    target = local_path(root, config.state_dir + "/barrier.json")
    write_private(target, {"barrier": name})
    while not target.with_suffix(".release").exists():
        time.sleep(0.02)


def summary(path: str, journal: dict) -> dict:
    return {"id": journal["id"], "history_path": path, "status": journal["status"],
            "affected_ids": journal["affected_ids"], "paths": [item["path"] for item in journal["changes"]]}


def current_bytes(root: Path, item: dict) -> str | None:
    target = local_path(root, item["path"])
    if target.exists() and not target.is_file():
        raise LifecycleError("PUBLICATION_CONFLICT", "unexpected destination is not an ordinary file", exit_code=1)
    try:
        return history.text_bytes(target) if target.is_file() else None
    except (OSError, UnicodeError) as exc:
        raise LifecycleError("PUBLICATION_CONFLICT", "unexpected or unavailable destination bytes are preserved", exit_code=1) from exc


def relevant_files(config, root: Path, scope: dict, delivery: dict) -> dict:
    from .lifecycle import file_revision
    paths = {item["path"] for item in delivery["artifacts"]}
    for selector in scope["paths"]:
        if any(char in selector for char in "*?["):
            matches = sorted(root.glob(selector))
        else:
            target = local_path(root, selector)
            matches = sorted(target.rglob("*")) if target.is_dir() else [target]
        if len(matches) > 2000:
            raise LifecycleError("INPUT_SCOPE_UNBOUNDED", "narrow the relevant source scope")
        paths.update(path.relative_to(root).as_posix() for path in matches if path.is_file())
    from .source_ingestion import snapshot
    source_state = snapshot(config, root)
    if source_state is not None:
        # Source integration may introduce required references to existing
        # undisclosed knowledge. Bind their pre-pass bytes as well as delivered
        # artifacts before any source semantic publication.
        from .knowledge import load_knowledge
        paths.update(load_knowledge(config, repository_root=root, ignore_publication=True).documents)
        paths.update(path for path in source_state["files"] if path != ".agents/memory/sources/source-ingest-manifest.json")
    return {path: file_revision(local_path(root, path)) for path in sorted(paths)
            if local_path(root, path).is_file() and not path.startswith(config.state_dir + "/")}


def validate_inputs(journal: dict, config, config_path: Path, root: Path) -> None:
    from .lifecycle import file_revision, guidance
    if file_revision(config_path) != journal["config_revision"]:
        raise LifecycleError("INPUTS_STALE", "publication configuration changed")
    versions = {item["path"]: (item["before_revision"], item["after_revision"]) for item in journal["changes"]}
    for path, revision in journal["relevant_files"].items():
        target = local_path(root, path)
        actual = file_revision(target) if target.is_file() else None
        if actual not in versions.get(path, (revision,)):
            raise LifecycleError("INPUTS_STALE", "publication relevant sources differ from their exact recorded revisions")
    for item in journal["changes"]:
        if current_bytes(root, item) not in (item["before"], item["after"]):
            raise LifecycleError("PUBLICATION_CONFLICT", "unexpected destination edit is preserved", exit_code=1)
    # Catch newly introduced relevant files and guidance, not only old paths.
    current = relevant_files(config, root, journal["scope"], guidance(config, root, journal["scope"], ignore_publication=True))
    for path in set(current) - set(journal["relevant_files"]):
        if path not in versions:
            raise LifecycleError("INPUTS_STALE", "new relevant inputs appeared during publication")


def prepare_journal(validated: dict, payload: dict, config, config_path: Path, root: Path,
                    invocation: dict, session: dict, obligation: dict, checks: list[dict]) -> tuple[str, dict]:
    from .lifecycle import file_revision, guidance
    identity = uid()
    path = config.history_dir + "/" + identity + ".json"
    journal = validated | {"schema_version": 1, "id": identity, "status": "prepared", "intent": "publish exact validated changes",
        "created_at": time.time(), "payload": payload, "obligation_id": obligation["id"],
        "work_session_id": session["id"], "agent_id": invocation["agent_id"], "attempt_id": invocation["attempt_id"],
        "owner_generation": invocation["owner_generation"], "scope": obligation["scope"],
        "base_input_revision": session["input_revision"], "config_revision": file_revision(config_path),
        "relevant_files": relevant_files(config, root, session["scope"], guidance(config, root, session["scope"], ignore_publication=True)),
        "check_receipts": checks}
    if "source_work" in session:
        journal["source_work"] = session["source_work"]
    # Reserve the final bound receipt shape plus small status/recovery metadata.
    # A small proposal can still have a large indivisible before-image.
    final_receipts = [{"id": identity, **check, "input_revision": session["input_revision"],
        "config_revision": journal["config_revision"], "owner_generation": invocation["owner_generation"],
        "attempt_id": invocation["attempt_id"], "checked_at": 315537897599.9999} for check in checks]
    history.validate_size(journal | {"check_receipts": final_receipts, "integrity": "0" * 64}, reserve=4096)
    history.save(root, path, journal)
    return path, journal


def post_checks(journal: dict, config, root: Path) -> list[dict]:
    from .checks import run_checks
    from .knowledge import load_knowledge, validate_guidance_references
    knowledge = load_knowledge(config, repository_root=root, ignore_publication=True)
    from .stages import validate_links
    validate_links(knowledge.documents, root, journal["changes"])
    if knowledge.issues or validate_guidance_references(knowledge):
        raise LifecycleError("GUIDANCE_INVALID", "published metadata/reference integrity is incomplete", exit_code=1)
    if any(current_bytes(root, item) != item["after"] for item in journal["changes"]):
        raise LifecycleError("PUBLICATION_CONFLICT", "actual resulting bytes differ from the validated set", exit_code=1)
    from .source_ingestion import validate_review
    from .lifecycle import guidance
    if journal["payload"].get("dispositions") is None:
        validate_review(journal["payload"], config, root, journal["scope"],
            guidance(config, root, journal["scope"], ignore_publication=True), journal.get("source_work", []))
    receipts = run_checks(config, root)
    if not all(item["exit_code"] == 0 and not item["timed_out"] for item in receipts):
        raise LifecycleError("CHECK_FAILED", "an actual configured publication check failed", exit_code=1, retry_eligible=True)
    return receipts


def write_set(path: str, journal: dict, config, root: Path, validate_owner) -> None:
    barrier(config, root, "before_intent")
    validate_owner()
    journal["status"] = "intent"
    history.save(root, path, journal)
    history.mark_pending(root, config, path, journal["changes"])
    barrier(config, root, "after_intent")
    for index, item in enumerate(journal["changes"]):
        validate_owner()
        actual = current_bytes(root, item)
        if actual == item["before"]:
            history.replace_content(local_path(root, item["path"]), item["after"])
        elif actual != item["after"]:
            raise LifecycleError("PUBLICATION_CONFLICT", "unexpected edits prevent exact publication", exit_code=1)
        if index + 1 < len(journal["changes"]):
            barrier(config, root, "between_replacements")
    barrier(config, root, "after_files")


def reverse(path: str, journal: dict, config, root: Path, cause: str) -> bool:
    conflict = False
    for item in reversed(journal["changes"]):
        try:
            actual = current_bytes(root, item)
        except LifecycleError:
            conflict = True
            continue
        if actual == item["after"]:
            history.replace_content(local_path(root, item["path"]), item["before"])
        elif actual != item["before"]:
            conflict = True
    journal.update(status="conflict" if conflict else "reversed", reason=cause)
    history.save(root, path, journal)
    if not conflict:
        history.clear_pending(root, config)
    return not conflict


def recover(store, config, config_path: Path, *, allow_checks: bool = True) -> dict | None:
    with history.exclusive(store):
        return _recover(store, config, config_path, allow_checks=allow_checks)


def _recover(store, config, config_path: Path, *, allow_checks: bool) -> dict | None:
    """Reconcile a recorded set only, never restart canceled semantic work."""
    indication = history.pending(store.root, config, store)
    if indication is None:
        return None
    if not allow_checks:
        raise LifecycleError("RECOVERY_FOREGROUND_REQUIRED", "publication recovery requires bounded foreground checks; native callbacks must defer before effects or attempt claims", exit_code=1,
            next_action="Restore a supported foreground recovery stage through the native adapter; keep the pending publication visible.")
    path = indication["history_path"]
    journal = history.read(store.root, path)
    state = store.read()
    session = next((item for item in state["sessions"].values() if item["id"] == journal["work_session_id"]), None)
    if journal["status"] == "conflict":
        raise LifecycleError("PUBLICATION_CONFLICT", "unexpected edits remain preserved; affected recovery is pending", exit_code=1)
    can_finish = session is not None and session["status"] not in ("paused", "cancelled")
    try:
        if not can_finish:
            raise LifecycleError("INVOCATION_REVOKED", "paused/canceled objective permits inverse reconciliation only")
        validate_inputs(journal, config, config_path, store.root)
        # Recovery is a deterministic eligible-event operation, independent of
        # expired foreground handles, under the current publication owner.
        owner = state["owner"]
        if owner and owner["obligation_id"] != journal["obligation_id"] and owner["expires_at"] > time.time():
            raise LifecycleError("OWNER_BUSY", "a different live owner prevents publication recovery", exit_code=1)
        item = session["obligations"][journal["obligation_id"]]
        if item["attempt_count"] >= int(config.limits["max_attempts"]) and item.get("retry_needed"):
            raise LifecycleError("ATTEMPTS_EXHAUSTED", "publication retry cap exhausted", exit_code=1)
        cap = min(int(config.limits["max_attempts"]), *(int(value["max_attempts"]) for value in config.providers.values() if value["enabled"]))
        if item["attempt_count"] >= cap:
            raise LifecycleError("ATTEMPTS_EXHAUSTED", "publication recovery attempt cap exhausted", exit_code=1)
        def claim(record):
            bound = next(value for value in record["sessions"].values() if value["id"] == journal["work_session_id"])
            if bound["status"] in ("paused", "cancelled"):
                raise LifecycleError("INVOCATION_REVOKED", "objective was paused/canceled during reconciliation")
            record["ownership_generation"] += 1
            record["owner"] = {"obligation_id": journal["obligation_id"], "agent_id": journal["agent_id"],
                "generation": record["ownership_generation"], "expires_at": time.time() + float(config.limits["lease_seconds"])}
            bound["obligations"][journal["obligation_id"]]["attempt_count"] += 1
        store.change(state["revision"], claim)
        state = store.read()
        generation = state["owner"]["generation"]
        journal["owner_generation"] = generation
        journal["attempt_id"] = uid()
        history.save(store.root, path, journal)
        barrier(config, store.root, "during_recovery")
        def valid_recovery():
            current = store.read()
            bound = next(value for value in current["sessions"].values() if value["id"] == journal["work_session_id"])
            if bound["status"] in ("paused", "cancelled") or not current["owner"] or current["owner"]["generation"] != generation:
                raise LifecycleError("OWNER_STALE", "recovery ownership was revoked or changed")
            validate_inputs(journal, config, config_path, store.root)
        for change in journal["changes"]:
            valid_recovery()
            if current_bytes(store.root, change) == change["before"]:
                history.replace_content(local_path(store.root, change["path"]), change["after"])
        checks = post_checks(journal, config, store.root)
        valid_recovery()
        state = store.read()
        finish(store, state, config, config_path, path, journal, checks, complete=True, recovered=True)
    except LifecycleError as exc:
        if exc.code in ("OWNER_BUSY", "STATE_CONTENDED", "STATE_UNAVAILABLE"):
            raise
        restored = reverse(path, journal, config, store.root, str(exc))
        def update(record):
            bound = next((value for value in record["sessions"].values() if value["id"] == journal["work_session_id"]), None)
            if bound is not None:
                obligation = bound["obligations"][journal["obligation_id"]]
                obligation.update(status="pending", stage_outcome="incomplete", reason=str(exc), retry_needed=True)
                obligation.pop("prepared", None)
                if bound["status"] not in ("paused", "cancelled"):
                    bound["status"] = "incomplete"
        state = store.read()
        store.change(state["revision"], update)
        if not restored:
            raise LifecycleError("PUBLICATION_CONFLICT", "unexpected edits retained with an affected gap", exit_code=1)
    return summary(path, journal)


def finish(store, state, config, config_path: Path, path: str, journal: dict,
           checks: list[dict], *, complete: bool, recovered: bool = False) -> dict:
    from .lifecycle import guidance, inputs, file_revision, revoke_agent, children_pending, mark_output_pending, identities
    bound = next(value for value in state["sessions"].values() if value["id"] == journal["work_session_id"])
    if journal.get("source_work", []) != bound.get("source_work", []):
        raise LifecycleError("SOURCE_EVIDENCE_STALE", "publication source work differs from the current joined obligation", exit_code=1)
    from .source_ingestion import settle, knowledge_bases
    if complete:
        settle(journal["payload"], config, store.root)
    delivery = guidance(config, store.root, bound["scope"], ignore_publication=True)
    resulting_input = inputs(config, store.root, file_revision(config_path), bound["scope"], delivery)
    resulting_bases = knowledge_bases(config, store.root) if bound.get("source_work") else None
    journal.update(status="checked" if complete else "published", resulting_input_revision=resulting_input)
    history.save(store.root, path, journal)
    if complete:
        bound = next(value for value in state["sessions"].values() if value["id"] == journal["work_session_id"])
        executing = next(value for value in bound["agents"].values() if value["id"] == journal["agent_id"])
        mark_output_pending(store, identities(state, bound, executing), bound["input_generation"], executing["context_generation"])
    from .maintenance import session_completion, utc_day
    completed_on = utc_day(config, store.root, config_path)
    def update(record):
        session = next(value for value in record["sessions"].values() if value["id"] == journal["work_session_id"])
        obligation = session["obligations"][journal["obligation_id"]]
        if session["status"] in ("paused", "cancelled"):
            raise LifecycleError("INVOCATION_REVOKED", "objective was explicitly paused/canceled")
        if complete and children_pending(session):
            raise LifecycleError("CHILD_OBLIGATIONS_PENDING", "children must settle before publication completion", exit_code=1)
        owner = record["owner"]
        if not owner or owner["generation"] != journal["owner_generation"] or owner["expires_at"] <= time.time():
            raise LifecycleError("OWNER_STALE", "publication owner changed or expired")
        session["input_revision"] = resulting_input
        if complete and session.get("source_work"):
            session["source_checked"] = resulting_input
        if session.get("source_work"):
            session["source_baseline"] = resulting_bases
        for inv in record["invocations"].values():
            if inv["obligation_id"] == obligation["id"]:
                inv["input_revision"] = resulting_input
        agent = next(value for value in session["agents"].values() if value["id"] == journal["agent_id"])
        if agent.get("delivery"):
            agent["delivery"].update(input_revision=resulting_input, guidance_revision=digest(delivery), complete=delivery["complete"])
        receipts = [{"id": uid(), **check, "input_revision": resulting_input,
                     "config_revision": file_revision(config_path), "owner_generation": journal["owner_generation"],
                     "attempt_id": journal["attempt_id"], "checked_at": time.time()} for check in checks]
        obligation["check_receipts"] = receipts
        obligation["publication"] = summary(path, journal)
        if complete:
            obligation.update(status="completed", stage_outcome="changed")
            obligation.pop("reason", None)
            session_completion(record, session, config, store.root, completed_on)
            revoke_agent(record, agent["id"])
        return receipts
    receipts = store.change(state["revision"], update)
    journal["check_receipts"] = receipts
    journal["status"] = "completed" if complete else "published"
    history.save(store.root, path, journal)
    if complete:
        history.clear_pending(store.root, config)
    return journal
