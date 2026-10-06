"""Deterministic normalized lifecycle coordination; semantic work stays foreground."""
from __future__ import annotations

import argparse
from collections.abc import Sequence
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from typing import Any

from . import __version__
from .config import (BUILTIN_CHECKS, ConfigurationError, LIFECYCLE_EVENTS, _keys,
                     _object, _relative_path, _string, _strings, _unique_object, _reject_constant, _finite_float, load_config)
from .knowledge import load_knowledge
from .records import AgentBrainConfig, RetrievalScope
from .retrieval import SCOPE_FIELDS, retrieve
from .state import LifecycleError, StateStore, digest, local_path, uid, write_private


def read_json(source: str) -> dict[str, Any]:
    try:
        value = json.loads(source, object_pairs_hook=_unique_object, parse_constant=_reject_constant, parse_float=_finite_float)
        return _object(value, "record")
    except (ValueError, TypeError) as exc:
        raise LifecycleError("INPUT_INVALID", f"invalid versioned JSON: {exc}") from exc


def file_revision(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def actual_binding(root: Path) -> tuple[str, str]:
    try:
        def git(*args: str) -> str:
            result = subprocess.run(["git", "-C", str(root), "rev-parse", *args],
                                    capture_output=True, text=True, timeout=1, check=True)
            return result.stdout.strip()
        worktree = Path(git("--show-toplevel")).resolve()
        common = Path(git("--path-format=absolute", "--git-common-dir")).resolve()
        repository = common.parent if common.name == ".git" else common
        if worktree != root:
            raise LifecycleError("BINDING_INVALID", "integration must run at the actual worktree root")
        return str(repository), str(worktree)
    except (subprocess.SubprocessError, OSError) as exc:
        raise LifecycleError("BINDING_INVALID", "actual Git repository/worktree binding is unavailable") from exc


def scope_record(value: object) -> dict[str, list[str]]:
    item = _object(value, "scope")
    if item.keys() - set(SCOPE_FIELDS):
        raise ConfigurationError("scope contains an unsupported selector")
    result = {field: _strings(item.get(field, []), f"scope.{field}", nonempty=False)
              for field in SCOPE_FIELDS}
    for path in result["paths"]:
        _relative_path(path, "scope path")
    return result


def merge_scope(left: dict, right: dict) -> dict[str, list[str]]:
    return {field: sorted(set(left.get(field, [])) | set(right.get(field, []))) for field in SCOPE_FIELDS}


def guidance(config: AgentBrainConfig, root: Path, scope: dict, *, ignore_publication: bool = False, store: StateStore | None = None) -> dict:
    result = retrieve(config, load_knowledge(config, repository_root=root, ignore_publication=ignore_publication, state_store=store),
        RetrievalScope(None, {field: tuple(scope.get(field, [])) for field in SCOPE_FIELDS}))
    return result.recall.as_json_object()


def inputs(config: AgentBrainConfig, root: Path, config_revision: str,
           scope: dict, delivery: dict, *, native_callback: bool = False) -> str:
    from .source_ingestion import snapshot
    if native_callback and config.source_ingestion["enabled"]:
        from .native import captured_sources
        source_inputs = captured_sources(config, root, config_revision)
    else:
        source_inputs = snapshot(config, root)
    files: dict[str, str] = {}
    for selector in scope["paths"]:
        if any(char in selector for char in "*?["):
            # Unknown file scope remains explicit in retrieval's completeness.
            candidates = sorted(root.glob(selector))
        else:
            path = local_path(root, selector)
            candidates = sorted(path.rglob("*")) if path.is_dir() else [path]
        if len(candidates) > 2000:
            raise LifecycleError("INPUT_SCOPE_UNBOUNDED", "narrow the relevant file scope before checked maintenance", exit_code=1)
        for path in candidates:
            relative = path.relative_to(root).as_posix()
            if relative.startswith(config.state_dir + "/"):
                continue
            checked = local_path(root, relative)
            files[relative] = file_revision(checked) if checked.is_file() else "missing"
    return digest({"config_revision": config_revision, "scope": scope, "files": files,
        "source_ingestion": source_inputs,
        "units": [(unit["id"], unit["content_revision"], unit["input_revision"]) for unit in delivery["units"]],
        "artifacts": [(item["id"], item["loading_mode"], item["content_revision"], item["input_revision"])
                      for item in delivery["artifacts"]], "gaps": delivery["gaps"]})


def configured_provider(config: AgentBrainConfig, config_path: Path, root: Path,
                        identity: dict, event: str | None = None) -> dict:
    _keys(identity, "integration", {"id", "core_version", "adapter_version", "certification_id", "config_revision"})
    provider = config.providers.get(identity["id"])
    if not provider or not provider["enabled"]:
        raise LifecycleError("INTEGRATION_DISABLED", "this integration is not configured and enabled")
    if identity["config_revision"] != file_revision(config_path):
        raise LifecycleError("CONFIGURATION_STALE", "effective configuration revision no longer matches")
    if identity["core_version"] != __version__:
        raise LifecycleError("INTEGRATION_MISMATCH", "core version is outside the configured support identity")
    for field in ("core_version", "adapter_version", "certification_id"):
        if identity[field] != provider[field]:
            raise LifecycleError("INTEGRATION_MISMATCH", f"{field} is outside the configured support identity")
    if event is not None and event not in provider["events"]:
        raise LifecycleError("EVENT_INELIGIBLE", "event is outside the configured supported events")
    if provider["kind"] == "native":
        from .native import support_record
        support_record(config, root, provider)
        return provider
    # A fixture is only eligible in a disposable Git repository below the OS
    # temporary directory. Its registration must bind that exact worktree.
    if not root.is_relative_to(Path(tempfile.gettempdir()).resolve()) and not root.is_relative_to(Path("/private/tmp")):
        raise LifecycleError("FIXTURE_SCOPE_INVALID", "protocol fixture registration requires a disposable temporary repository")
    support_path = local_path(root, str(provider["support_record"]))
    support = read_json(support_path.read_text(encoding="utf-8"))
    _keys(support, "support record", {"schema_version", "kind", "repository_id", "worktree_root",
                                     "core_version", "adapter_version", "certification_id", "events"})
    expected = {"schema_version": 1, "kind": "protocol_fixture", "repository_id": config.repository_id,
                "worktree_root": str(root), "events": provider["events"]}
    expected.update({field: provider[field] for field in ("core_version", "adapter_version", "certification_id")})
    if support != expected:
        raise LifecycleError("SUPPORT_RECORD_INVALID", "fixture support record does not match the exact configured binding")
    return provider


def validate_event(event: dict) -> dict:
    required = {"schema_version", "event_id", "event", "integration", "binding", "scope"}
    optional = {"classification", "parent_agent_id", "assigned_obligations", "stage_generated", "timestamp", "review_flags"}
    _keys(event, "event", required | (event.keys() & optional))
    if type(event["schema_version"]) is not int or event["schema_version"] != 1:
        raise ConfigurationError("event schema_version must be 1")
    _string(event["event_id"], "event_id")
    if event["event"] not in LIFECYCLE_EVENTS:
        raise LifecycleError("EVENT_INELIGIBLE", "unknown normalized lifecycle event")
    _object(event["integration"], "integration")
    binding = _object(event["binding"], "binding")
    _keys(binding, "binding", {"repository_root", "worktree_root", "provider_session_id", "provider_task_id", "provider_agent_id"})
    for name, value in binding.items():
        _string(value, name)
    event["scope"] = scope_record(event["scope"])
    if "classification" in event and event["classification"] not in ("active", "awaiting_user", "ready_to_complete"):
        raise ConfigurationError("checkpoint classification must be active, awaiting_user, or ready_to_complete")
    if "parent_agent_id" in event:
        _string(event["parent_agent_id"], "parent_agent_id")
    if "assigned_obligations" in event:
        assignments = _strings(event["assigned_obligations"], "assigned_obligations", nonempty=False)
        if set(assignments) - {"scope_review"}:
            raise ConfigurationError("only assigned scope_review obligations are available")
    if "stage_generated" in event:
        _string(event["stage_generated"], "stage_generated attempt id")
    if "timestamp" in event and type(event["timestamp"]) not in (str, float, int):
        raise ConfigurationError("event timestamp must be a string or finite number; it never grants authority")
    if "review_flags" in event:
        from .config import _uuid
        for identity in _strings(event["review_flags"], "review_flags", nonempty=False):
            _uuid(identity, "review flag")
    return event


def session_key(integration_id: str, binding: dict) -> str:
    return digest([integration_id, binding["provider_session_id"], binding["provider_task_id"]])


def agent_key(integration_id: str, provider_agent_id: str) -> str:
    return digest([integration_id, provider_agent_id])


def project_obligation(item: dict) -> dict:
    fields = ("id", "kind", "status", "stage_outcome", "input_generation", "attempt_count",
              "semantic_repairs", "owner_agent_id", "owner_generation", "scope", "reason", "check_receipts", "publication", "batch", "dispositions")
    return {field: item[field] for field in fields if field in item}


def project_session(item: dict) -> dict:
    result = {"work_session_id": item["id"], "task_id": item["task_id"],
            "checkpoint": item["checkpoint"], "work_session_status": item["status"],
            "input_generation": item["input_generation"], "input_revision": item["input_revision"],
            "obligations": [project_obligation(value) for value in item["obligations"].values()],
            "agents": [{"agent_id": value["id"], "parent_agent_id": value["parent"],
                        "context_generation": value["context_generation"], "status": value["status"],
                        "delivery_complete": bool(value.get("delivery", {}).get("complete") and value.get("delivery", {}).get("available")
                                                  and value.get("delivery", {}).get("input_generation") == item["input_generation"]
                                                  and value.get("delivery", {}).get("context_generation") == value["context_generation"]),
                        "assigned_obligations": value["assigned"]} for value in item["agents"].values()]}
    if item.get("source_work"):
        result.update(source_work=item["source_work"], action_ready=item.get("source_checked") == item["input_revision"])
    return result


def inspection(config: AgentBrainConfig, root: Path, config_path: Path | None = None) -> dict:
    result: dict[str, object] = {"state_status": "absent", "work_sessions": [], "sqlite_capabilities": {}}
    try:
        store = StateStore(root, config.state_dir, float(config.limits["contention_seconds"]))
        if not store.path.exists() and not store.marker.exists():
            return result
        state = store.read()
        from .source_ingestion import snapshot
        source_state = snapshot(config, root)
        if local_path(root, config.state_dir + "/output-pending.json").exists():
            raise LifecycleError("DELIVERY_RECONCILIATION_REQUIRED", "unfinished output settlement is retained; next eligible event restores authority/context", exit_code=1)
        from .history import pending
        outstanding = pending(root, config, store)
        if outstanding:
            result["publication_recovery"] = outstanding
        if state["repository_id"] != config.repository_id:
            raise LifecycleError("STATE_UNAVAILABLE", "repository identity differs from expected local state", exit_code=1)
        result.update(state_status="available", worktree_id=state["worktree_id"],
                      work_sessions=[project_session(value) for value in state["sessions"].values()],
                      sqlite_capabilities=store.capabilities)
        tickets = list(state.get("native_foreground", {}).values())
        result["native_foreground"] = {"pending": sum("closed_on" not in value for value in tickets),
                                       "closed": sum("closed_on" in value for value in tickets)}
        if result["native_foreground"]["pending"]:
            result["work_session_status"] = "incomplete"
        if source_state is not None:
            for session, projected in zip(state["sessions"].values(), result["work_sessions"]):
                current = inputs(config, root, file_revision(config_path or root / ".agents/context/config.json"), session["scope"], guidance(config, root, session["scope"], store=store))
                if current != session["input_revision"]:
                    projected.update(action_ready=False, work_session_status="incomplete")
        from .maintenance import projection
        result["maintenance"] = projection(state)
    except (LifecycleError, ValueError, KeyError, TypeError, OSError) as exc:
        if not isinstance(exc, LifecycleError):
            exc = LifecycleError("STATE_UNAVAILABLE", "expected lifecycle structure is unavailable; preserve recoverable state", exit_code=1)
        result.update(state_status="unavailable", work_session_status="incomplete", pending_work="unknown",
                      error={"code": exc.code, "cause": str(exc), "retry_eligible": exc.retry_eligible,
                             "next_action": exc.next_action})
    return result


def identities(state: dict, session: dict, agent: dict) -> dict:
    return {"repository_id": state["repository_id"], "worktree_id": state["worktree_id"],
            "work_session_id": session["id"], "task_id": session["task_id"], "agent_id": agent["id"]}


def bridge_event(event: dict, config_path: Path, *, native_callback: bool = False,
                 native_foreground: bool = False, resume_paused: bool = False) -> tuple[dict, int, StateStore]:
    root = Path.cwd().resolve()
    event = validate_event(event)
    if resume_paused and (not native_foreground or event["event"] != "task"):
        raise LifecycleError("OBJECTIVE_RESUME_INVALID", "paused resumption requires an issued native foreground task intent")
    config_path = local_path(root, config_path.relative_to(root).as_posix())
    config = load_config(config_path)
    actual_repository, actual_worktree = actual_binding(root)
    if (event["binding"]["repository_root"], event["binding"]["worktree_root"]) != (actual_repository, actual_worktree):
        raise LifecycleError("BINDING_INVALID", "event binding does not match the actual repository/worktree")
    candidate = config.providers.get(event["integration"].get("id"))
    if candidate and candidate["kind"] == "native" and not (native_callback or native_foreground):
        raise LifecycleError("NATIVE_SUPPORT_UNAVAILABLE", "native events require the validated adapter or issued foreground boundary")
    provider = configured_provider(config, config_path, root, event["integration"], event["event"])
    from .source_ingestion import snapshot, pending
    # Fixture callbacks are explicit foreground process boundaries. Native
    # adapters must defer this lock/scan work before claiming a semantic attempt.
    if native_callback and config.source_ingestion["enabled"]:
        from .native import captured_sources
        source_state = captured_sources(config, root, file_revision(config_path))
    else:
        source_state = snapshot(config, root, reconcile=provider["kind"] == "protocol_fixture" or native_foreground)
    source_pending = pending(source_state)
    for knowledge_root in config.knowledge_roots:
        if knowledge_root.ownership == "agent_brain":
            local_path(root, knowledge_root.path)
    store = StateStore(root, config.state_dir, float(config.limits["contention_seconds"]),
                       min(int(config.limits["max_attempts"]), int(provider["max_attempts"])))
    ignored = subprocess.run(["git", "check-ignore", "-q", "--", str(store.path)], cwd=root,
                             timeout=1, check=False, capture_output=True)
    if ignored.returncode != 0:
        raise LifecycleError("STATE_NOT_IGNORED", "the configured worktree-local state directory must be ignored")
    if not store.path.exists() and not store.marker.exists() and event["event"] not in ("startup", "task"):
        raise LifecycleError("OBJECTIVE_UNREGISTERED", "only eligible startup/task events initialize local state")
    store.initialize(config.repository_id, actual_repository)
    state = store.read()

    if state["repository_id"] != config.repository_id or state["repository_root"] != actual_repository:
        raise LifecycleError("BINDING_INVALID", "expected durable repository identity differs")
    recovery = None
    from .publication import recover
    if event["event"] in ("startup", "task", "resume", "recover", "context_lost"):
        reconcile_output(store, config, config_path)
        state = store.read()
        recovery = recover(store, config, config_path, allow_checks=provider["kind"] == "protocol_fixture" or native_foreground)
        state = store.read()
        if recovery is not None:
            source_state = snapshot(config, root, reconcile=provider["kind"] == "protocol_fixture" or native_foreground)
            source_pending = pending(source_state)
    key = session_key(str(event["integration"]["id"]), event["binding"])
    akey = agent_key(str(event["integration"]["id"]), event["binding"]["provider_agent_id"])
    previous = state["sessions"].get(key)
    from .source_ingestion import prior_work
    if event["event"] not in ("pause", "cancel"):
        source_pending = sorted(set(source_pending) | set(prior_work(config, root, state, key, event["scope"], source_state, config_path, native_callback=native_callback)))
    if source_state is not None and previous and previous.get("source_work") and event["event"] not in ("pause", "cancel"):
        from .source_ingestion import validate_bases
        # Only the canonical scanner can add inert scaffolds without a semantic
        # journal. Existing summaries and guidance keep their pre-pass bases.
        for entry in source_state["blocking"]:
            if not entry["summary_resolved"] and entry["summary_path"] not in previous.get("source_baseline", {}):
                previous.setdefault("source_baseline", {})[entry["summary_path"]] = entry["summary_revision"]
        validate_bases(config, root, previous, source_state)
    scope = merge_scope(previous["scope"] if previous else {}, event["scope"])
    aggregate_guidance = guidance(config, root, scope, store=store)
    previous_agent = previous["agents"].get(akey) if previous else None
    is_child = event["event"] == "child_start" or bool(previous_agent and previous_agent["parent"])
    assigned_scope = merge_scope(previous_agent["scope"] if previous_agent else {}, event["scope"])
    delivery = guidance(config, root, assigned_scope, store=store) if is_child else aggregate_guidance
    revision = inputs(config, root, str(event["integration"]["config_revision"]), scope, aggregate_guidance,
                      native_callback=native_callback)
    if native_callback and source_state is not None and (source_pending or not previous
            or previous.get("source_checked") != revision):
        raise LifecycleError("RECOVERY_FOREGROUND_REQUIRED", "source reconciliation/checks require the issued foreground stage before effects or attempt claims", exit_code=1)
    from . import maintenance
    today = maintenance.utc_day(config, root, config_path)
    current_targets, structural_complete = maintenance.snapshot(config, root, store=store)
    from copy import deepcopy
    planning = deepcopy(state)
    if event["event"] in ("startup", "task", "resume", "recover"):
        maintenance.detect(planning, config, current_targets, structural_complete, today, event.get("review_flags", []))
        maintenance.prepare_cleanup(planning, config, root, today, retain_session=previous["id"] if previous else None)
    planning_session = deepcopy(previous) if previous else {"obligations": {}, "input_generation": 1}
    eligible_completion = (event.get("classification") == "ready_to_complete" or
                          bool(previous and previous["checkpoint"] == "ready_to_complete"))
    if eligible_completion and not is_child:
        maintenance.assign(planning, planning_session, config, root, current_targets, store=store)
    planned_dream = next((item for item in planning_session["obligations"].values() if item["kind"] == "dream"), None)
    dream_delivery = maintenance.assigned_guidance(config, root, planned_dream, store=store) if planned_dream else None
    from .source_ingestion import knowledge_bases
    source_bases = knowledge_bases(config, root, source_state) if source_state is not None else None

    def update(record: dict) -> tuple[dict, int]:
        if "maintenance" in planning:
            record["maintenance"] = planning["maintenance"]
            if "native_foreground" in planning:
                record["native_foreground"] = planning["native_foreground"]
            if "native_output" in planning:
                record["native_output"] = planning["native_output"]
            if "native_objectives" in planning:
                record["native_objectives"] = planning["native_objectives"]
            for retired_key in set(record["sessions"]) - set(planning["sessions"]):
                del record["sessions"][retired_key]
            for retired_invocation in set(record["invocations"]) - set(planning["invocations"]):
                del record["invocations"][retired_invocation]
        session = record["sessions"].get(key)
        if session is None:
            if event["event"] not in ("startup", "task"):
                raise LifecycleError("OBJECTIVE_UNREGISTERED", "only eligible startup/task events register a new objective")
            session = {"id": uid(), "task_id": uid(), "status": "active", "checkpoint": "active",
                       "scope": scope, "input_generation": 1, "input_revision": revision,
                       "agents": {}, "obligations": {}, "root_agent": akey}
            record["sessions"][key] = session
        if source_state is not None:
            session["source_work"] = sorted(set(session.get("source_work", [])) | set(source_pending))
            if session["source_work"]:
                if previous and "source_baseline" in previous:
                    session["source_baseline"] = previous["source_baseline"]
                elif "source_baseline" not in session:
                    session["source_baseline"] = source_bases
        agent = session["agents"].get(akey)
        if agent is None:
            if akey != session["root_agent"] and event["event"] not in ("startup", "task", "child_start"):
                raise LifecycleError("AGENT_UNREGISTERED", "new agents require an eligible startup/task or registered child event")
            parent = None
            if event["event"] == "child_start":
                parent_key = agent_key(str(event["integration"]["id"]), str(event.get("parent_agent_id", "")))
                parent_agent = session["agents"].get(parent_key)
                if parent_agent is None:
                    raise LifecycleError("CHILD_UNREGISTERED", "child parent is not registered for this objective")
                parent = parent_agent["id"]
            agent = {"id": uid(), "parent": parent, "context_generation": 1,
                     "status": "active", "scope": event["scope"],
                     "assigned": event.get("assigned_obligations", ["scope_review"] if parent else [])}
            session["agents"][akey] = agent
            if parent and session["obligations"]:
                session["input_generation"] += 1
                session["status"] = "incomplete"
                if session["checkpoint"] == "completed":
                    session["checkpoint"] = "ready_to_complete"
                invalidate_results(record, session, "new registered child requires current aggregate settlement")
        elif event["event"] == "child_start":
            expected_parent = agent_key(str(event["integration"]["id"]), str(event.get("parent_agent_id", "")))
            if session["agents"].get(expected_parent, {}).get("id") != agent["parent"]:
                raise LifecycleError("CHILD_UNREGISTERED", "child parent binding changed")
        if resume_paused:
            if session["status"] != "paused":
                raise LifecycleError("OBJECTIVE_RESUME_INVALID", "only the exact paused objective may explicitly resume")
            session.update(status="active", checkpoint="active")
        if session["status"] in ("paused", "cancelled"):
            return event_result(record, session, agent, None, "none"), 0
        agent["scope"] = merge_scope(agent["scope"], event["scope"])
        if revision != session["input_revision"]:
            session["input_generation"] += 1
            session["input_revision"] = revision
            session["scope"] = scope
            session["status"] = "incomplete" if session["obligations"] else "active"
            invalidate_results(record, session, "relevant inputs changed")
        existing_dream = next((item for item in session["obligations"].values() if item["kind"] == "dream"), None)
        if existing_dream and planned_dream and existing_dream["batch"]["targets"] != planned_dream["batch"]["targets"]:
            session["input_generation"] += 1
            session["status"] = "incomplete"
            invalidate_results(record, session, "assigned dream target revisions changed")
        if event["event"] in ("pause", "cancel"):
            session["status"] = "paused" if event["event"] == "pause" else "cancelled"
            revoke_session(record, session)
            return event_result(record, session, agent, None, "none"), 0
        if event["event"] == "context_lost":
            agent["context_generation"] += 1
            agent.pop("delivery", None)
            revoke_agent(record, agent["id"])
            for obligation in session["obligations"].values():
                if obligation.get("owner_agent_id") == agent["id"]:
                    obligation.pop("prepared", None)
                    obligation["check_receipts"] = []
                    obligation.update(status="pending", stage_outcome="incomplete", reason="context generation changed")
            if agent["parent"]:
                agent["status"] = "incomplete"
            if session["status"] == "completed":
                session["status"] = "incomplete"
                session["checkpoint"] = "ready_to_complete"
        if "stage_generated" in event:
            if not any(inv["attempt_id"] == event["stage_generated"] and inv["agent_id"] == agent["id"]
                       for inv in record["invocations"].values()):
                raise LifecycleError("CALLBACK_INVALID", "stage-generated callback does not belong to this agent/attempt")
            return event_result(record, session, agent, None, "none"), 0
        # An early source pass settles prerequisite knowledge, not the user's
        # active objective. Its final checkpoint must review post-work inputs.
        early_learn = next((item for item in session["obligations"].values() if item["kind"] == "learn"), None)
        if (event.get("classification") == "ready_to_complete" and session["checkpoint"] != "ready_to_complete"
                and early_learn and early_learn["status"] == "completed" and session.get("source_work")):
            session["input_generation"] += 1
            invalidate_results(record, session, "final objective learning requires a post-work review")
        agent["delivery"] = {"complete": delivery["complete"], "context_generation": agent["context_generation"],
                             "input_generation": session["input_generation"], "input_revision": revision,
                             "guidance_revision": digest(delivery), "config_revision": event["integration"]["config_revision"],
                             "delivered_at": time.time(), "available": False}
        if session["status"] == "completed":
            response = event_result(record, session, agent, delivery, "none")
            response["stage_outcome"] = "no_change"
            return response, 0 if delivery["complete"] else 1
        kind = event["event"]
        if kind in ("task", "startup", "scope", "resume", "recover") and session["status"] != "completed":
            session["status"] = session["checkpoint"] if session["checkpoint"] == "ready_to_complete" else "active"
            if session["status"] == "active":
                session["checkpoint"] = "active"
        next_kind = "recall"
        if kind in ("checkpoint", "child_stop"):
            classification = event.get("classification")
            if classification is None:
                next_kind = "checkpoint"
            elif classification == "ready_to_complete":
                session["checkpoint"] = classification if not agent["parent"] else session["checkpoint"]
                if not agent["parent"]:
                    session["status"] = "ready_to_complete"
                next_kind = "learn" if not agent["parent"] or agent["assigned"] else "none"
                if next_kind == "none":
                    agent["status"] = "completed" if delivery["complete"] else "incomplete"
            else:
                if not agent["parent"]:
                    session["checkpoint"] = classification
                    session["status"] = classification
                next_kind = "none"
        if kind in ("startup", "task", "resume", "recover", "context_lost") and session["checkpoint"] == "ready_to_complete":
            next_kind = "learn"
        if (not agent["parent"] and session.get("source_work") and session.get("source_checked") != revision
                and kind in ("startup", "task", "scope", "resume", "recover", "context_lost")):
            next_kind = "learn"
        if resume_paused:
            # Intent restores the same objective and context. It never claims
            # another semantic attempt; pending source/action gates survive.
            next_kind = "recall"
        if next_kind == "learn":
            claim = claim_obligation(record, session, agent, config, config_path, event, provider, store)
            if not agent["parent"] and planned_dream:
                existing = session["obligations"].get(planned_dream["id"])
                if existing:
                    existing.update(batch=planned_dream["batch"], scope=planned_dream["scope"])
                else:
                    session["obligations"][planned_dream["id"]] = planned_dream
            selected = next((item for item in session["obligations"].values()
                             if item["kind"] == "learn"), None)
            if not agent["parent"] and selected and selected["status"] == "completed":
                next_kind = "dream"
                batch_item = next((item for item in session["obligations"].values() if item["kind"] == "dream"), None)
                if batch_item:
                    delivery.clear()
                    delivery.update(dream_delivery)
                    agent["delivery"].update(complete=delivery["complete"], guidance_revision=digest(delivery))
                claim = claim_obligation(record, session, agent, config, config_path, event, provider, store, kind="dream")
            response = event_result(record, session, agent, delivery, next_kind)
            response.update(claim)
        else:
            response = event_result(record, session, agent, delivery, next_kind)
        return response, 0 if delivery["complete"] else 1

    result, code = store.change(state["revision"], update)
    maintenance.clean_files(store, config)
    result["maintenance"] = maintenance.projection(store.read())
    private = result.pop("_invocation", None)
    if private:
        invocation_path = local_path(root, str(Path(result["invocation_file"]).relative_to(root)))
        invocation_path.parent.mkdir(mode=0o700, exist_ok=True)
        write_private(invocation_path, private)
    result["sqlite_capabilities"] = store.capabilities
    if recovery:
        result["publication_recovery"] = recovery
    return result, code, store


def claim_obligation(state: dict, session: dict, agent: dict, config: AgentBrainConfig,
                     config_path: Path, event: dict, provider: dict, store: StateStore, *, kind: str | None = None) -> dict:
    kind = kind or ("child_review" if agent["parent"] else "learn")
    obligation = next((value for value in session["obligations"].values()
                       if value["kind"] == kind and (kind in ("learn", "dream") or value["assigned_agent_id"] == agent["id"])), None)
    if obligation is None:
        obligation = {"id": uid(), "kind": kind, "scope": agent["scope"] if agent["parent"] else session["scope"],
                      "input_generation": session["input_generation"], "status": "pending",
                      "stage_outcome": "incomplete", "attempt_count": 0, "semantic_repairs": 0,
                      "assigned_agent_id": agent["id"] if agent["parent"] else None, "check_receipts": []}
        session["obligations"][obligation["id"]] = obligation
    if obligation["input_generation"] != session["input_generation"]:
        obligation.update(input_generation=session["input_generation"], scope=agent["scope"] if agent["parent"] else session["scope"],
                          status="pending", stage_outcome="incomplete", attempt_count=0, semantic_repairs=0, check_receipts=[])
        obligation.pop("prepared", None)
        obligation.pop("retry_needed", None)
        obligation.pop("repair_exhausted", None)
    if obligation["status"] == "completed":
        return {"stage_outcome": obligation["stage_outcome"]}
    if not agent["parent"] and children_pending(session):
        obligation["reason"] = "registered child scope obligations must settle before aggregate learning"
        return {"pending_reason": obligation["reason"]}
    cap = min(int(config.limits["max_attempts"]), int(provider["max_attempts"]))
    if obligation.get("repair_exhausted") or (obligation.get("retry_needed") and obligation["attempt_count"] >= cap):
        obligation["reason"] = "bounded attempts/semantic repair exhausted; preserve pending work"
        if not agent["parent"]:
            session["status"] = "incomplete"
        return {"pending_reason": obligation["reason"]}
    if not agent.get("delivery", {}).get("complete"):
        obligation["reason"] = "required guidance is incomplete"
        return {"pending_reason": obligation["reason"]}
    now = time.time()
    owner = state["owner"]
    if owner and owner["expires_at"] > now:
        if owner["obligation_id"] != obligation["id"] or owner["agent_id"] != agent["id"]:
            obligation["reason"] = "a different live mutation owner retains its finite lease"
            return {"pending_reason": obligation["reason"]}
        current = next((inv for inv in state["invocations"].values()
                        if inv["obligation_id"] == obligation["id"] and not inv["revoked"]
                        and inv["owner_generation"] == owner["generation"] and inv["expires_at"] > now), None)
        if current and Path(current["file"]).is_file():
            current["expires_at"] = now + float(config.limits["lease_seconds"])
            owner["expires_at"] = current["expires_at"]
            return {"invocation_file": current["file"], "attempt_id": current["attempt_id"],
                    "ownership_generation": owner["generation"]}
    elif owner and event["event"] not in ("startup", "task", "resume", "recover", "context_lost"):
        obligation["reason"] = "expired ownership requires an eligible recovery event"
        return {"pending_reason": obligation["reason"]}
    if obligation["attempt_count"] >= cap:
        obligation["reason"] = "attempt limit exhausted; preserve pending work for an eligible changed-input recovery"
        session["status"] = "incomplete" if not agent["parent"] else session["status"]
        return {"pending_reason": obligation["reason"]}
    if owner:
        revoke_agent(state, owner["agent_id"])
    state["ownership_generation"] += 1
    generation = state["ownership_generation"]
    expiry = now + float(config.limits["lease_seconds"])
    state["owner"] = {"obligation_id": obligation["id"], "agent_id": agent["id"],
                      "generation": generation, "expires_at": expiry}
    obligation.update(status="active", owner_agent_id=agent["id"], owner_generation=generation,
                      attempt_count=obligation["attempt_count"] + 1)
    obligation.pop("reason", None)
    handle, attempt_id = uid() + uid(), uid()
    invocation_file = str(store.directory / "invocations" / f"{uid()}.json")
    state["invocations"][digest(handle)] = {
        "file": invocation_file, "attempt_id": attempt_id, "stage": "dream" if kind == "dream" else "learn", "session_key": session_key(str(event["integration"]["id"]), event["binding"]),
        "agent_key": agent_key(str(event["integration"]["id"]), event["binding"]["provider_agent_id"]),
        "agent_id": agent["id"], "obligation_id": obligation["id"], "owner_generation": generation,
        "input_generation": session["input_generation"], "context_generation": agent["context_generation"],
        "input_revision": session["input_revision"], "integration": event["integration"],
        "config_path": str(config_path), "expires_at": expiry, "revoked": False,
    }
    return {"invocation_file": invocation_file, "attempt_id": attempt_id, "ownership_generation": generation,
            "_invocation": {"schema_version": 1, "handle": handle}}


def validate_invocation(state: dict, handle: str, stage: str, config: AgentBrainConfig,
                        root: Path, config_path: Path) -> tuple[dict, dict, dict, dict]:
    invocation = state["invocations"].get(digest(handle))
    if invocation is None:
        raise LifecycleError("INVOCATION_INVALID", "invocation handle is not registered in this worktree")
    if invocation["stage"] != stage or invocation["config_path"] != str(config_path):
        raise LifecycleError("INVOCATION_MISMATCH", "invocation stage or effective configuration binding differs")
    configured_provider(config, config_path, root, invocation["integration"])
    session = state["sessions"][invocation["session_key"]]
    agent = session["agents"][invocation["agent_key"]]
    obligation = session["obligations"][invocation["obligation_id"]]
    if invocation["revoked"] or session["status"] in ("paused", "cancelled"):
        raise LifecycleError("INVOCATION_REVOKED", "invocation authority was completed, paused, cancelled, or superseded")
    if invocation["expires_at"] <= time.time():
        raise LifecycleError("INVOCATION_EXPIRED", "invocation expired according to the actual local clock")
    owner = state["owner"]
    if not owner or owner["generation"] != invocation["owner_generation"] or owner["agent_id"] != agent["id"] or owner["obligation_id"] != obligation["id"] or owner["expires_at"] <= time.time():
        raise LifecycleError("OWNER_STALE", "invocation no longer owns the current finite mutation generation")
    if (invocation["input_generation"] != session["input_generation"] or invocation["input_revision"] != session["input_revision"]
            or invocation["context_generation"] != agent["context_generation"]):
        raise LifecycleError("INVOCATION_STALE", "current input/context generations differ from the registration")
    receipt = agent.get("delivery")
    if not receipt or not receipt["complete"] or not receipt.get("available") or receipt["context_generation"] != agent["context_generation"] or receipt["input_generation"] != session["input_generation"] or receipt["input_revision"] != session["input_revision"]:
        raise LifecycleError("CONTEXT_RESTORATION_REQUIRED", "current complete guidance must be restored before dependent maintenance")
    return invocation, session, agent, obligation


def active_invocation(path_argument: str | None, config_argument: str | None,
                      stage: str) -> tuple[StateStore, dict, str, AgentBrainConfig, Path, tuple]:
    if not path_argument:
        raise LifecycleError("ACTIVE_CONTEXT_REQUIRED", "registered active agent context is required")
    root = Path.cwd().resolve()
    config_path = Path(config_argument or ".agents/context/config.json").absolute()
    config_path = local_path(root, config_path.relative_to(root).as_posix())
    config = load_config(config_path)
    if not any(value["enabled"] for value in config.providers.values()):
        raise LifecycleError("ACTIVE_CONTEXT_REQUIRED", "registered active agent context is required")
    store = StateStore(root, config.state_dir, float(config.limits["contention_seconds"]))
    invocation_path = Path(path_argument).absolute()
    invocation_path = local_path(root, invocation_path.relative_to(root).as_posix())
    if not invocation_path.is_relative_to(store.directory / "invocations"):
        raise LifecycleError("INVOCATION_INVALID", "invocation file must be in its integration-owned local directory")
    raw = read_json(invocation_path.read_text(encoding="utf-8"))
    _keys(raw, "invocation file", {"schema_version", "handle"})
    if type(raw["schema_version"]) is not int or raw["schema_version"] != 1:
        raise LifecycleError("INVOCATION_INVALID", "invocation schema version differs")
    handle = _string(raw["handle"], "handle")
    state = store.read()
    repository, worktree = actual_binding(root)
    if (state["repository_root"], state["worktree_root"], state["repository_id"]) != (repository, worktree, config.repository_id):
        raise LifecycleError("BINDING_INVALID", "durable identity differs from the actual worktree")
    binding = validate_invocation(state, handle, stage, config, root, config_path)
    _, session, _, _ = binding
    current = guidance(config, root, session["scope"], ignore_publication=bool(binding[3].get("publication")), store=store)
    if inputs(config, root, file_revision(config_path), session["scope"], current) != session["input_revision"]:
        raise LifecycleError("INPUTS_STALE", "relevant inputs changed; restore guidance at the next eligible event")
    if stage == "dream" and not binding[3].get("publication"):
        from .maintenance import snapshot
        targets, _ = snapshot(config, root, store=store)
        if any(targets.get(identity, {}).get("revision") != revision for identity, revision in binding[3]["batch"]["targets"].items()):
            raise LifecycleError("DREAM_TARGET_STALE", "assigned target revisions changed; restore before semantic input")
    return store, state, handle, config, config_path, binding


def retry_attempt(store: StateStore, state: dict, handle: str, stage: str,
                  config: AgentBrainConfig, config_path: Path, binding: tuple) -> tuple[dict, tuple]:
    invocation, _, _, obligation = binding
    if obligation.get("repair_exhausted"):
        raise LifecycleError("SEMANTIC_REPAIR_EXHAUSTED", "one semantic repair was already attempted; pending work remains", exit_code=1)
    if not obligation.get("retry_needed"):
        return state, binding
    provider = config.providers[invocation["integration"]["id"]]
    cap = min(int(config.limits["max_attempts"]), int(provider["max_attempts"]))
    if obligation["attempt_count"] >= cap:
        raise LifecycleError("ATTEMPTS_EXHAUSTED", "three-total-attempt or tighter provider cap exhausted; pending work remains", exit_code=1)
    time.sleep((0.25, 0.75)[min(obligation["attempt_count"] - 1, 1)])

    def update(record: dict) -> None:
        inv, _, _, item = validate_invocation(record, handle, stage, config, store.root, config_path)
        if item["attempt_count"] >= cap:
            raise LifecycleError("ATTEMPTS_EXHAUSTED", "attempt limit exhausted", exit_code=1)
        item["attempt_count"] += 1
        item["retry_needed"] = False
        inv["attempt_id"] = uid()

    store.change(state["revision"], update)
    current = store.read()
    return current, validate_invocation(current, handle, stage, config, store.root, config_path)


def semantic_failure(store: StateStore, state: dict, handle: str, stage: str,
                     config: AgentBrainConfig, config_path: Path, cause: str) -> None:
    def update(record: dict) -> None:
        _, session, agent, obligation = validate_invocation(record, handle, stage, config, store.root, config_path)
        if obligation["semantic_repairs"] >= 1:
            obligation["repair_exhausted"] = True
        else:
            obligation["semantic_repairs"] += 1
        obligation.update(stage_outcome="incomplete", retry_needed=True, reason=cause)
        if not agent["parent"]:
            session["status"] = "incomplete"
    store.change(state["revision"], update)


def stage_operation(stage: str, operation: str, path_argument: str | None,
                    config_argument: str | None, input_argument: str | None) -> tuple[dict, int, StateStore]:
    store, state, handle, config, config_path, binding = active_invocation(path_argument, config_argument, stage)
    invocation, session, agent, obligation = binding
    if stage in ("learn", "dream"):
        if (operation in ("publish", "complete") and obligation.get("publication")
                and obligation["publication"]["status"] not in ("checked", "reversed")):
            if input_argument is not None:
                raise LifecycleError("PUBLICATION_INPUT_UNEXPECTED", "publish/complete use the exact prepared set without replacement input")
            from .stages import changed_operation
            return changed_operation(operation, store, state, handle, config, config_path, binding, None)
    if operation == "start":
        from .maintenance import assigned_guidance
        result = event_result(state, session, agent, None, "none")
        result.update(stage=stage, operation=operation, attempt_id=invocation["attempt_id"], ownership_generation=invocation["owner_generation"])
        result["work_package"] = {"obligation": project_obligation(obligation), "scope": obligation["scope"],
            "procedure": procedure(stage), "next_operation": "prepare",
            "guidance": assigned_guidance(config, store.root, obligation, store=store)}
        if stage == "dream":
            result["work_package"]["batch"] = obligation["batch"]
        else:
            from .source_ingestion import package
            source_package = package(config, store.root, session)
            if source_package is not None:
                result["work_package"]["source_ingestion"] = source_package
        return result, 0, store
    if operation not in ("prepare", "complete"):
        raise LifecycleError("OPERATION_UNAVAILABLE", "publish requires an exact prepared change set")
    if input_argument is None:
        raise LifecycleError("INPUT_REQUIRED", "an evidenced proposal or scoped no-change review is required")
    state, binding = retry_attempt(store, state, handle, stage, config, config_path, binding)
    invocation, session, agent, obligation = binding
    from .checks import checked_review
    from .maintenance import assigned_guidance, validate_review, session_completion, utc_day
    current = assigned_guidance(config, store.root, obligation, store=store)
    dispositions = None
    try:
        if input_argument == "-":
            sys.stdin.reconfigure(encoding="utf-8", errors="strict")
        source = sys.stdin.read(1024 * 1024 + 1) if input_argument == "-" else Path(input_argument).read_text(encoding="utf-8")
        payload = read_json(source)
        from .source_ingestion import validate_stage, validate_bases
        validate_bases(config, store.root, session)
        if stage == "dream":
            payload, dispositions = validate_review(payload, obligation, config, store.root, store=store)
            payload["dispositions"] = dispositions
            validate_stage(payload, config, store.root, obligation["scope"], current, session, stage)
        if payload.get("outcome") == "changed":
            from .stages import changed_operation
            return changed_operation(operation, store, state, handle, config, config_path, binding, payload)
        validate_stage(payload, config, store.root, obligation["scope"], current, session, stage)
        checked_payload = {key: value for key, value in payload.items() if key != "dispositions"}
        checks, _ = checked_review(checked_payload, config, store.root, obligation["scope"], current)
        review_revision = digest(payload)
    except KeyboardInterrupt:
        def interrupted(record: dict) -> None:
            _, interrupted_session, interrupted_agent, item = validate_invocation(record, handle, stage, config, store.root, config_path)
            item.update(stage_outcome="incomplete", retry_needed=True, reason="foreground attempt interrupted")
            if not interrupted_agent["parent"]:
                interrupted_session["status"] = "incomplete"
        store.change(state["revision"], interrupted)
        raise
    except (ValueError, OSError, TypeError, KeyError) as exc:
        if isinstance(exc, LifecycleError) and exc.code.startswith("SOURCE_"):
            raise
        semantic_failure(store, state, handle, stage, config, config_path, str(exc))
        raise
    if operation == "complete" and obligation.get("prepared") != review_revision:
        raise LifecycleError("REVIEW_NOT_PREPARED", "the current review has not been prepared by configured checks", exit_code=1)
    # No transaction spans the foreground checks. Re-read actual input files
    # and authority again before saving their attributable receipts.
    latest = guidance(config, store.root, session["scope"], store=store)
    if inputs(config, store.root, file_revision(config_path), session["scope"], latest) != session["input_revision"]:
        raise LifecycleError("INPUTS_STALE", "relevant inputs changed while checks ran", exit_code=1)
    validate_bases(config, store.root, session)
    if operation == "complete":
        mark_output_pending(store, identities(state, session, agent), session["input_generation"], agent["context_generation"])
        from .source_ingestion import settle
        if all(check["exit_code"] == 0 and not check["timed_out"] for check in checks):
            settle(payload, config, store.root)
            resulting_input = inputs(config, store.root, file_revision(config_path), session["scope"], latest)
        else:
            resulting_input = session["input_revision"]
    completed_on = utc_day(config, store.root, config_path)

    def update(record: dict) -> tuple[dict, int]:
        inv, current_session, current_agent, current_obligation = validate_invocation(record, handle, stage, config, store.root, config_path)
        if checks:
            current_obligation["check_receipts"] = [{"id": uid(), "checker_id": check["checker_id"],
                "exit_code": check["exit_code"], "timed_out": check["timed_out"], "input_revision": resulting_input if operation == "complete" else session["input_revision"],
                "config_revision": file_revision(config_path), "owner_generation": inv["owner_generation"],
                "attempt_id": inv["attempt_id"], "checked_at": time.time()} for check in checks]
        passed = all(check["exit_code"] == 0 and not check["timed_out"] for check in checks)
        if not passed:
            current_obligation.update(stage_outcome="incomplete", retry_needed=True, reason="configured check failed")
            result = event_result(record, current_session, current_agent, None, "none")
            result.update(stage=stage, operation=operation, attempt_id=inv["attempt_id"], ownership_generation=inv["owner_generation"])
            result["operation_status"] = "error"
            result["error"] = {"code": "CHECK_FAILED", "cause": "an actual configured check failed or timed out",
                "affected_scope": "assigned maintenance scope", "retry_eligible": True,
                "next_action": "Inspect actual check receipts, then repair inputs or retry within the remaining cap at an eligible foreground operation."}
            result["check_receipts"] = current_obligation["check_receipts"]
            return result, 1
        current_obligation["prepared"] = review_revision
        if dispositions is not None:
            current_obligation["dispositions"] = dispositions
        if operation == "complete":
            if not current_agent["parent"] and children_pending(current_session):
                raise LifecycleError("CHILD_OBLIGATIONS_PENDING", "registered children must settle assigned scope obligations before parent completion", exit_code=1)
            current_obligation.update(status="completed", stage_outcome="no_change")
            if stage == "learn" and current_session.get("source_work"):
                current_session["input_revision"] = resulting_input
                current_session["source_checked"] = resulting_input
                inv["input_revision"] = resulting_input
                current_agent["delivery"]["input_revision"] = resulting_input
            current_obligation.pop("reason", None)
            revoke_agent(record, current_agent["id"])
            if current_agent["parent"]:
                current_agent["status"] = "completed"
            else:
                session_completion(record, current_session, config, store.root, completed_on)
        else:
            expiry = time.time() + float(config.limits["lease_seconds"])
            inv["expires_at"] = expiry
            record["owner"]["expires_at"] = expiry
        result = event_result(record, current_session, current_agent, None, "none")
        result.update(stage=stage, operation=operation, attempt_id=inv["attempt_id"], ownership_generation=inv["owner_generation"])
        result["stage_outcome"] = "no_change" if operation == "complete" else "incomplete"
        result["check_receipts"] = current_obligation["check_receipts"]
        return result, 0

    result, code = store.change(state["revision"], update)
    return result, code, store


def revoke_agent(state: dict, agent_id: str) -> None:
    for invocation in state["invocations"].values():
        if invocation["agent_id"] == agent_id:
            invocation["revoked"] = True
    if state["owner"] and state["owner"]["agent_id"] == agent_id:
        state["owner"] = None
        state["ownership_generation"] += 1


def revoke_session(state: dict, session: dict) -> None:
    for agent in session["agents"].values():
        revoke_agent(state, agent["id"])


def invalidate_results(state: dict, session: dict, reason: str) -> None:
    session.pop("source_checked", None)
    for obligation in session["obligations"].values():
        cycle = state.get("maintenance", {}).get("cycle")
        if obligation["kind"] == "dream" and obligation["status"] == "completed" and (cycle is None or obligation["batch"]["cycle_id"] != cycle["id"]):
            continue
        if cycle:
            for target in cycle["targets"].values():
                if target["credit"] and target["credit"]["obligation_id"] == obligation["id"]:
                    target["credit"] = None
        obligation.update(status="pending", stage_outcome="incomplete", reason=reason, check_receipts=[])
        obligation.pop("prepared", None)
    for agent in session["agents"].values():
        if agent["parent"]:
            agent["status"] = "incomplete"
    revoke_session(state, session)


def children_pending(session: dict) -> bool:
    for child in session["agents"].values():
        if not child["parent"]:
            continue
        receipt = child.get("delivery", {})
        if (child["status"] != "completed" or not receipt.get("complete") or not receipt.get("available")
                or receipt.get("input_generation") != session["input_generation"]
                or receipt.get("context_generation") != child["context_generation"]):
            return True
        if any(item["assigned_agent_id"] == child["id"] and item["status"] != "completed"
               for item in session["obligations"].values()):
            return True
    return False


def procedure(name: str) -> str:
    return (Path(__file__).resolve().parents[2] / "references" / f"{name}.md").read_text(encoding="utf-8")


def event_result(state: dict, session: dict, agent: dict, delivery: dict | None, next_kind: str) -> dict:
    result = {"schema_version": 1, "operation_status": "ok", "stage_outcome": "incomplete",
        "work_session_status": session["status"], "checkpoint": session["checkpoint"],
        "identities": identities(state, session, agent), "input_generation": session["input_generation"],
        "context_generation": agent["context_generation"], "input_revision": session["input_revision"],
        "delivery": delivery, "obligations": [project_obligation(item) for item in session["obligations"].values()],
        "next_action": {"kind": next_kind}, "support": "common_protocol_fixture_only"}
    from .maintenance import projection
    result["maintenance"] = projection(state)
    if session.get("source_work"):
        result["action_ready"] = session.get("source_checked") == session["input_revision"]
        result["source_work"] = session["source_work"]
    if next_kind == "checkpoint":
        result["next_action"]["instruction"] = "Classify this same objective: active, awaiting_user, or ready_to_complete."
    elif next_kind in ("recall", "learn", "dream"):
        result["next_action"]["procedure"] = procedure(next_kind)
    return result


def error_result(error: LifecycleError) -> dict:
    return {"schema_version": 1, "operation_status": "error", "stage_outcome": "incomplete",
            "work_session_status": "incomplete", "error": {"code": error.code, "cause": str(error),
                "affected_scope": "bound worktree lifecycle", "retry_eligible": error.retry_eligible,
                "next_action": error.next_action}}


def bridge_main(argv: Sequence[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="strict")
    parser = argparse.ArgumentParser(prog="agent-brain integration bridge", allow_abbrev=False)
    parser.add_argument("--config", default=".agents/context/config.json")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--native-gate", action="store_true")
    args = parser.parse_args(argv)
    store = None
    try:
        sys.stdin.reconfigure(encoding="utf-8", errors="strict")
        event = read_json(sys.stdin.read(1024 * 1024 + 1))
        if args.native_gate:
            from .native import gate
            result = gate(event)
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
            return 0
        result, code, store = bridge_event(event, Path(args.config).absolute())
    except (ConfigurationError, OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as exc:
        error = exc if isinstance(exc, LifecycleError) else LifecycleError("INPUT_INVALID", str(exc))
        result, code = error_result(error), error.exit_code
        print(f"agent-brain bridge: {error.code}: {error}", file=sys.stderr)
        print(f"Next action: {error.next_action}", file=sys.stderr)
    except KeyboardInterrupt:
        result, code = error_result(LifecycleError("INTERRUPTED", "interrupted operation preserves pending work", exit_code=130)), 130
    try:
        if result.get("publication_recovery", {}).get("status") == "completed":
            from .publication import barrier
            barrier(load_config(Path(args.config).absolute()), Path.cwd().resolve(), "before_bridge_output")
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        sys.stdout.flush()
        if result.get("delivery") is not None:
            settle_output(result, args.config, delivered=True, store=store)
    except BrokenPipeError:
        failed_output(result, args.config, store=store)
        return 1
    except (LifecycleError, ConfigurationError, OSError) as exc:
        print(f"agent-brain: DELIVERY_INCOMPLETE: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        import signal
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        print(json.dumps(error_result(LifecycleError("INTERRUPTED", "unfinished bridge output remains pending", exit_code=130)), sort_keys=True))
        print("agent-brain: INTERRUPTED: pending output reconciliation is retained.", file=sys.stderr)
        return 130
    return code


def settle_output(result: dict, config_argument: str | None, *, delivered: bool, store: StateStore | None = None,
                  native_callback: bool = False) -> None:
    """Flush completion makes pending protocol context available to the next process.

    Failed output revokes authority and invalidates prepared review. Successful
    output is still distinct from certified native provider consumption.
    """
    identity = result.get("identities")
    if not identity:
        return
    root = Path.cwd().resolve()
    config = load_config(Path(config_argument or ".agents/context/config.json"))
    store = store or StateStore(root, config.state_dir, float(config.limits["contention_seconds"]))
    output_marker = local_path(root, config.state_dir + "/output-pending.json")
    if output_marker.exists():
        marker = read_output_pending(output_marker)
        if marker["identities"] != identity and result.get("publication_recovery", {}).get("status") == "completed":
            from .history import read
            journal = read(root, result["publication_recovery"]["history_path"])
            if (journal["id"] != result["publication_recovery"]["id"]
                    or journal["work_session_id"] != marker["identities"]["work_session_id"]
                    or journal["agent_id"] != marker["identities"]["agent_id"]):
                raise LifecycleError("DELIVERY_RECONCILIATION_REQUIRED", "recovered output marker differs from the exact journal identity", exit_code=1)
            recovered_state = store.read()
            recovered_session = next(value for value in recovered_state["sessions"].values() if value["id"] == journal["work_session_id"])
            recovered_obligation = recovered_session["obligations"][journal["obligation_id"]]
            settle_output(marker | {"stage": recovered_obligation["kind"], "operation": "complete"}, config_argument,
                          delivered=delivered, store=store, native_callback=native_callback)
    if not delivered and not output_marker.exists():
        mark_output_pending(store, identity, result["input_generation"], result["context_generation"])
    if delivered and not native_callback and config.source_ingestion["enabled"] and any(
            value["enabled"] and value["kind"] == "native" for value in config.providers.values()):
        from .native import capture_sources
        capture_sources(config, root, Path(config_argument or ".agents/context/config.json").absolute(), store)
    state = store.read()
    from .maintenance import snapshot, credit, utc_day, verified_publications
    completed_output = result.get("operation") == "complete" or result.get("publication_recovery", {}).get("status") == "completed"
    credit_inputs = snapshot(config, root, store=store) if delivered and completed_output and state.get("maintenance", {}).get("cycle") else None
    checked_publications = verified_publications(config, Path(config_argument or ".agents/context/config.json").absolute(), root, state) if credit_inputs else {}
    today = utc_day(config, root, Path(config_argument or ".agents/context/config.json").absolute())

    def update(record: dict) -> None:
        session = next((value for value in record["sessions"].values() if value["id"] == identity["work_session_id"]), None)
        agent = next((value for value in session["agents"].values() if value["id"] == identity["agent_id"]), None) if session else None
        if not agent or agent["context_generation"] != result["context_generation"] or session["input_generation"] != result["input_generation"]:
            raise LifecycleError("DELIVERY_SUPERSEDED", "delivery generations changed while output was in progress", exit_code=1)
        if delivered:
            if result.get("delivery") is not None:
                agent["delivery"]["available"] = bool(result["delivery"]["complete"])
            if credit_inputs is not None:
                credit(record, session, config, root, today, *credit_inputs, checked_publications)
            return
        agent["context_generation"] += 1
        session.pop("source_checked", None)
        agent.pop("delivery", None)
        revoke_agent(record, agent["id"])
        for obligation in session["obligations"].values():
            if obligation.get("owner_agent_id") == agent["id"]:
                obligation.update(status="pending", stage_outcome="incomplete", reason="foreground output delivery failed")
                obligation.pop("prepared", None)
                if obligation["kind"] != "dream" and not local_path(root, config.state_dir + "/publication.json").exists():
                    obligation.pop("publication", None)
        if session["status"] not in ("paused", "cancelled"):
            session["status"] = "incomplete"
            if session["checkpoint"] == "completed":
                session["checkpoint"] = "ready_to_complete"
    store.change(state["revision"], update)
    if output_marker.exists():
        marker = read_output_pending(output_marker)
        if (marker["identities"] == identity and marker["input_generation"] == result["input_generation"]
                and marker["context_generation"] == result["context_generation"]):
            output_marker.unlink()
            from .history import sync_directory
            sync_directory(output_marker.parent)


def mark_output_pending(store: StateStore, identity: dict, input_generation: int, context_generation: int) -> None:
    from .history import sync_directory
    marker = local_path(store.root, str(store.directory.relative_to(store.root)) + "/output-pending.json")
    write_private(marker, {"identities": identity, "input_generation": input_generation, "context_generation": context_generation})
    sync_directory(marker.parent)


def read_output_pending(path: Path) -> dict:
    from .config import _uuid
    try:
        raw = path.read_bytes()
        if len(raw) > 16 * 1024:
            raise ValueError("pending output record exceeds finite bound")
        marker = read_json(raw.decode("utf-8"))
        _keys(marker, "pending output", {"identities", "input_generation", "context_generation"})
        identity = _object(marker["identities"], "pending identities")
        _keys(identity, "pending identities", {"repository_id", "worktree_id", "work_session_id", "task_id", "agent_id"})
        for field, value in identity.items():
            _uuid(value, field)
        for field in ("input_generation", "context_generation"):
            if type(marker[field]) is not int or marker[field] < 1:
                raise ValueError("invalid pending generation")
        return marker
    except (LifecycleError, ValueError, TypeError, OSError, RecursionError) as exc:
        raise LifecycleError("DELIVERY_RECONCILIATION_REQUIRED", "preserve missing/corrupt pending output record; unfinished delivery is unavailable", exit_code=1) from exc


def reconcile_output(store: StateStore, config: AgentBrainConfig, config_path: Path) -> None:
    marker = local_path(store.root, config.state_dir + "/output-pending.json")
    if marker.exists():
        result = read_output_pending(marker)
        settle_output(result, str(config_path), delivered=False, store=store)


def failed_output(result: dict, config_argument: str | None, *, store: StateStore | None = None) -> None:
    reconciled = False
    try:
        if store and result.get("identities"):
            pending_marker = local_path(store.root, str(store.directory.relative_to(store.root)) + "/output-pending.json")
            if not pending_marker.exists():
                mark_output_pending(store, result["identities"], result["input_generation"], result["context_generation"])
        settle_output(result, config_argument, delivered=False, store=store)
        reconciled = True
    except (LifecycleError, ConfigurationError, OSError):
        print("agent-brain: DELIVERY_RECONCILIATION_REQUIRED: preserve pending work and restore context at an eligible event.", file=sys.stderr)
    with open(os.devnull, "w", encoding="utf-8") as sink:
        os.dup2(sink.fileno(), sys.stdout.fileno())
    message = "authority revoked and pending work retained" if reconciled else "reconciliation unavailable; retain pending work and recover at an eligible event"
    print(f"agent-brain: DELIVERY_INCOMPLETE: output closed; {message}.", file=sys.stderr)
