"""Frozen native registration, deterministic callbacks, issued foreground work."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time

from . import __version__
from .config import load_config, _keys, _string
from .lifecycle import (actual_binding, bridge_event, error_result, file_revision,
    read_json, scope_record, settle_output, validate_event, session_key, agent_key, mark_output_pending)
from .state import LifecycleError, StateStore, digest, local_path, uid, write_private

ADAPTER_VERSION = "native-1"
EVENTS = {
    "codex": {"SessionStart": "startup", "UserPromptSubmit": "task", "PreToolUse": "scope",
        "PreCompact": "context_lost", "SubagentStart": "child_start", "SubagentStop": "child_stop", "Stop": "checkpoint"},
    "copilot": {"sessionStart": "startup", "userPromptTransformed": "task", "preToolUse": "scope",
        "preCompact": "context_lost", "subagentStart": "child_start", "subagentStop": "child_stop", "agentStop": "checkpoint"},
    "gemini": {"SessionStart": "startup", "BeforeAgent": "task", "BeforeTool": "scope",
        "BeforeModel": "context_lost", "AfterAgent": "checkpoint", "PreCompress": "context_lost"},
}


def bundle_revision(path: Path) -> str:
    files = []
    scripts = local_path(path, "scripts")
    inventory = []
    for file in scripts.rglob("*"):
        if len(inventory) >= 2000:
            raise LifecycleError("NATIVE_UNSUPPORTED", "runnable inventory exceeds its bounded scope")
        local_path(path, file.relative_to(path).as_posix())
        inventory.append(file)
    for file in sorted(inventory):
        if file.is_file() and file.suffix == ".py":
            files.append((file.relative_to(path).as_posix(), file_revision(file)))
    return hashlib.sha256(json.dumps(files, separators=(",", ":")).encode()).hexdigest()


def source_topology(config, root):
    directories = {".agents/sources", ".agents/memory/sources"} | {value.path for value in config.knowledge_roots}
    result = {}
    for name in sorted(directories):
        directory = local_path(root, name)
        files = []
        if directory.exists():
            for path in directory.rglob("*"):
                relative = path.relative_to(root).as_posix()
                if relative.startswith(config.state_dir + "/") or relative.startswith(".git/"):
                    continue
                local_path(root, relative)
                if path.is_file():
                    files.append(relative)
                if len(files) > 2000:
                    raise LifecycleError("RECOVERY_FOREGROUND_REQUIRED", "native source freshness inventory exceeds its bounded scope", exit_code=1)
        result[name] = sorted(files)
    return result


def capture_sources(config, root, config_path, store):
    """Foreground-only canonical scan records exact immutable input inventory."""
    from .source_ingestion import snapshot
    value = snapshot(config, root)
    cache = {"config_revision": file_revision(config_path), "snapshot": value,
        "snapshot_revision": digest(value), "topology": source_topology(config, root)}
    state = store.read()
    store.change(state["revision"], lambda record: record.update(native_sources=cache))


def captured_sources(config, root, config_revision):
    """Callback freshness uses recorded paths/hashes only, never scanner/checks."""
    store = StateStore(root, config.state_dir, min(0.2, float(config.limits["contention_seconds"])))
    cache = store.read().get("native_sources")
    try:
        if not cache or cache["config_revision"] != config_revision or source_topology(config, root) != cache["topology"]:
            raise ValueError("source inventory changed")
        value = cache["snapshot"]
        if digest(value) != cache["snapshot_revision"] or any(file_revision(local_path(root, path)) != revision for path, revision in value["files"].items()):
            raise ValueError("source bytes changed")
        return value
    except (ValueError, OSError, KeyError, TypeError) as exc:
        raise LifecycleError("RECOVERY_FOREGROUND_REQUIRED", "recorded source freshness changed or is unavailable; restore canonical foreground work", exit_code=1) from exc


def support_record(config, root: Path, provider: dict) -> dict:
    """Exact reviewed pins are prerequisites, never inferred from process exit."""
    record = read_json(local_path(root, provider["support_record"]).read_bytes().decode("utf-8"))
    fields = {"schema_version", "kind", "status", "repository_id", "repository_root", "worktree_root",
        "core_version", "adapter_version", "certification_id", "events", "provider", "provider_version",
        "entry_mode", "platform", "filesystem_id", "permissions", "lifecycle_config", "native_events",
        "adapter_path", "adapter_revision", "bundle_path", "bundle_revision", "native_deadline_seconds",
        "immediate_model_boundary", "child_delivery", "evidence", "scope"}
    _keys(record, "native support record", fields)
    repository, worktree = actual_binding(root)
    expected = {"schema_version": 1, "kind": "native", "repository_id": config.repository_id,
        "repository_root": repository, "worktree_root": worktree, "platform": sys.platform,
        "filesystem_id": str(root.stat().st_dev), "events": provider["events"]}
    expected.update({key: provider[key] for key in ("core_version", "adapter_version", "certification_id")})
    if any(type(record[key]) is not type(value) or record[key] != value for key, value in expected.items()):
        raise LifecycleError("SUPPORT_RECORD_INVALID", "native support identity differs from the actual configured worktree")
    if record["core_version"] != __version__ or record["adapter_version"] != ADAPTER_VERSION:
        raise LifecycleError("INTEGRATION_MISMATCH", "native core/adapter versions differ")
    if record["provider"] not in EVENTS or record["entry_mode"] not in ({"cli", "desktop"} if record["provider"] == "codex" else {"cli"}):
        raise LifecycleError("NATIVE_UNSUPPORTED", "provider entry mode is unsupported; VS Code remains deferred")
    for name in ("provider_version", "bundle_revision", "adapter_revision"):
        _string(record[name], name)
    scope_record(record["scope"])
    for name in ("immediate_model_boundary", "child_delivery"):
        if type(record[name]) is not bool:
            raise LifecycleError("SUPPORT_RECORD_INVALID", "native capability binding must be boolean")
    if not isinstance(record["native_events"], list) or not record["native_events"] or len(set(record["native_events"])) != len(record["native_events"]) or set(record["native_events"]) - EVENTS[record["provider"]].keys():
        raise LifecycleError("NATIVE_UNSUPPORTED", "native event binding is unavailable")
    for name in ("permissions", "lifecycle_config"):
        _keys(record[name], name, {"path", "revision"})
        if file_revision(local_path(root, record[name]["path"])) != record[name]["revision"]:
            raise LifecycleError("INTEGRATION_MISMATCH", "native permissions/lifecycle configuration changed")
    if file_revision(local_path(root, record["adapter_path"])) != record["adapter_revision"] or bundle_revision(local_path(root, record["bundle_path"])) != record["bundle_revision"]:
        raise LifecycleError("INTEGRATION_MISMATCH", "native runnable bytes changed")
    deadline = record["native_deadline_seconds"]
    if type(deadline) not in (float, int) or not 0.1 < deadline <= 600:
        raise LifecycleError("SUPPORT_RECORD_INVALID", "native deadline is invalid")
    if record["status"] == "offline_fixture":
        if not (root.is_relative_to(Path(tempfile.gettempdir()).resolve()) or root.is_relative_to(Path("/private/tmp"))):
            raise LifecycleError("FIXTURE_SCOPE_INVALID", "offline native fixtures require disposable temporary Git repositories")
        if record["evidence"] != "offline_translation_only":
            raise LifecycleError("SUPPORT_RECORD_INVALID", "offline fixture is not native consumption evidence")
    elif record["status"] == "certified":
        # M10 owns production of these build-specific observed records. No
        # example or translation fixture in this bundle is such a record.
        _keys(record["evidence"], "native evidence", {"path", "revision"})
        proof = local_path(root, record["evidence"]["path"])
        if file_revision(proof) != record["evidence"]["revision"]:
            raise LifecycleError("NATIVE_SUPPORT_UNAVAILABLE", "observed native certification evidence is unavailable")
        evidence = read_json(proof.read_bytes().decode("utf-8"))
        if evidence != {"schema_version": 1, "certification_id": record["certification_id"],
            "provider": record["provider"], "provider_version": record["provider_version"],
            "entry_mode": record["entry_mode"], "context_consumed": True, "decisions_consumed": True,
            "events": record["native_events"], "watchdog_observed": True, "foreground_route_observed": True}:
            raise LifecycleError("NATIVE_SUPPORT_UNAVAILABLE", "exact observed native certification is required")
    else:
        raise LifecycleError("NATIVE_SUPPORT_UNAVAILABLE", "unconfigured/unverified native paths are unsupported")
    return record


def registration(value: dict, root: Path):
    _keys(value, "native registration", {"schema_version", "integration_id", "config_path", "bundle_path", "provider", "provider_version", "entry_mode"})
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise LifecycleError("INPUT_INVALID", "native registration schema must be 1")
    config_path = local_path(root, value["config_path"])
    config = load_config(config_path)
    provider = config.providers.get(value["integration_id"])
    if not provider or not provider["enabled"] or provider["kind"] != "native":
        raise LifecycleError("INTEGRATION_DISABLED", "native integration is not configured and enabled")
    support = support_record(config, root, provider)
    if any(value[key] != support[key] for key in ("provider", "provider_version", "entry_mode", "bundle_path")):
        raise LifecycleError("INTEGRATION_MISMATCH", "launcher does not match the frozen native binding")
    return config, config_path, provider, support


def normalized(value: dict, payload: dict, root: Path) -> tuple[dict, tuple]:
    binding = registration(value, root)
    config, config_path, provider, support = binding
    native_event = payload.get("_native_event")
    if native_event not in support["native_events"]:
        raise LifecycleError("EVENT_INELIGIBLE", "native event is outside the exact configured binding")
    if payload.get("cwd") != str(root):
        raise LifecycleError("BINDING_INVALID", "native cwd does not match the exact worktree root")
    name = support["provider"]
    session = payload.get("sessionId" if name == "copilot" else "session_id")
    _string(session, "native session id")
    kind = EVENTS[name][native_event]
    if kind == "startup":
        source = payload.get("source")
        allowed = {"startup", "resume", "new"} if name == "copilot" else {"startup", "resume", "clear", "compact"} if name == "codex" else {"startup", "resume", "clear"}
        if source not in allowed:
            raise LifecycleError("NATIVE_UNSUPPORTED", "native startup source is unsupported")
        if source == "resume":
            kind = "resume"
        if source == "compact":
            if not support["immediate_model_boundary"]:
                raise LifecycleError("NATIVE_UNSUPPORTED", "immediate post-compaction delivery is unverified")
            kind = "context_lost"
    if native_event == "BeforeModel":
        if not support["immediate_model_boundary"] or not isinstance(payload.get("llm_request"), dict) or not isinstance(payload["llm_request"].get("messages"), list):
            raise LifecycleError("NATIVE_UNSUPPORTED", "request boundary shape/order is unverified")
        request = payload["llm_request"]
        _string(request.get("model"), "request model")
        for message in request["messages"]:
            _keys(message, "stable model message", {"role", "content"})
            if message["role"] not in ("user", "model", "system") or not isinstance(message["content"], str):
                raise LifecycleError("NATIVE_UNSUPPORTED", "stable model message shape is unverified")
    scope = scope_record(support["scope"])
    tool = payload.get("toolArgs" if name == "copilot" else "tool_input", {})
    if kind == "scope":
        if not isinstance(tool, dict):
            raise LifecycleError("INPUT_INVALID", "native tool input must be an object")
        for field in ("file_path", "path"):
            if field in tool:
                path = tool[field]
                _string(path, "native path")
                if Path(path).is_absolute():
                    try:
                        path = Path(path).relative_to(root).as_posix()
                    except ValueError:
                        raise LifecycleError("BINDING_INVALID", "native path is outside the configured worktree") from None
                if path not in scope["paths"]:
                    scope["paths"].append(path)
    agent = "root"
    if kind in ("child_start", "child_stop"):
        if not support["child_delivery"] or payload.get("agentName", payload.get("agent_type")) == "general-purpose":
            raise LifecycleError("NATIVE_UNSUPPORTED", "child lifecycle/context is unverified")
        agent = payload.get("agentId" if name == "copilot" else "agent_id")
        # Copilot start exposes agentName, not agentId. The exact configured
        # wrapper must use that stable name for both start and stop.
        if name == "copilot":
            agent = payload.get("agentName")
        _string(agent, "native child identity")
    repository, worktree = actual_binding(root)
    task_id = session
    objective_key = digest([value["integration_id"], session])
    store = StateStore(root, config.state_dir, min(0.2, float(config.limits["contention_seconds"])))
    if store.path.exists() or store.marker.exists():
        state = store.read()
        task_id = state.get("native_objectives", {}).get(objective_key, {}).get("task_id", session)
        previous_key = session_key(value["integration_id"], {"provider_session_id": session, "provider_task_id": task_id})
        previous = state["sessions"].get(previous_key)
        if kind == "task" and previous and previous["status"] == "completed":
            task_id = digest([session, payload])
    event = {"schema_version": 1, "event_id": digest([value, payload]), "event": kind,
        "integration": {"id": value["integration_id"], "core_version": provider["core_version"],
            "adapter_version": provider["adapter_version"], "certification_id": provider["certification_id"],
            "config_revision": file_revision(config_path)},
        "binding": {"repository_root": repository, "worktree_root": worktree,
            "provider_session_id": session, "provider_task_id": task_id, "provider_agent_id": session + ":" + agent},
        "scope": scope}
    if kind == "child_start":
        event.update(parent_agent_id=session + ":root", assigned_obligations=["scope_review"])
    return validate_event(event), binding


def store_for(config, root, repository):
    store = StateStore(root, config.state_dir, min(0.2, float(config.limits["contention_seconds"])))
    ignored = subprocess.run(["git", "check-ignore", "-q", "--", str(store.path)], cwd=root,
        capture_output=True, timeout=0.5, check=False)
    if ignored.returncode != 0:
        raise LifecycleError("STATE_NOT_IGNORED", "native runtime state must be ignored")
    store.initialize(config.repository_id, repository)
    state = store.read()
    if state["repository_id"] != config.repository_id or state["repository_root"] != repository:
        raise LifecycleError("BINDING_INVALID", "native state binding differs")
    return store


def ticket_key(event, value):
    return digest([{key: item for key, item in event.items() if key not in ("event_id", "timestamp")}, value])


def invalidate_turn(event, value, store):
    """A new work boundary consumes a prior parent turn release."""
    if event["event"] not in ("startup", "task", "scope", "resume", "context_lost", "child_start"):
        return
    key = session_key(value["integration_id"], event["binding"])
    state = store.read()
    if any(ticket["session_key"] == key and "turn_release" in ticket for ticket in state.get("native_foreground", {}).values()):
        def invalidate(record):
            for ticket in record["native_foreground"].values():
                if ticket["session_key"] == key:
                    ticket.pop("turn_release", None)
        store.change(state["revision"], invalidate)


def released_turn(event, value, config, config_path, store):
    """Release only the same flushed parent checkpoint, never child review."""
    if event["event"] != "checkpoint":
        return False
    state = store.read()
    ticket = state.get("native_foreground", {}).get(ticket_key(event, value), {})
    released = ticket.get("turn_release")
    session = state["sessions"].get(session_key(value["integration_id"], event["binding"]))
    if not released and session and session["status"] in ("paused", "cancelled"):
        ticket = next((item for item in state.get("native_foreground", {}).values()
            if item["session_key"] == session_key(value["integration_id"], event["binding"])
            and item.get("turn_release", {}).get("status") == session["status"]), {})
        released = ticket.get("turn_release")
    agent = (session or {}).get("agents", {}).get(agent_key(value["integration_id"], event["binding"]["provider_agent_id"]))
    if not released or not session or not agent or local_path(store.root, config.state_dir + "/output-pending.json").exists():
        return False
    if (ticket["config_revision"] != file_revision(config_path) or released["registration_revision"] != digest(value)
            or released["status"] != session["status"] or session["status"] not in ("active", "awaiting_user", "paused", "cancelled")
            or released["input_generation"] != session["input_generation"] or released["input_revision"] != session["input_revision"]
            or released["scope_revision"] != digest(event["scope"])
            or released["context_generation"] != agent["context_generation"] or released["receipt_revision"] != digest(agent.get("delivery"))):
        return False
    from .lifecycle import guidance, inputs
    try:
        delivered = guidance(config, store.root, session["scope"], store=store)
        return inputs(config, store.root, file_revision(config_path), session["scope"], delivered, native_callback=True) == session["input_revision"]
    except LifecycleError as error:
        if error.code == "RECOVERY_FOREGROUND_REQUIRED":
            return False
        raise


def issue(event, config, config_path, value, store):
    """Issue deterministic foreground recovery without consuming learn attempts."""
    state = store.read()
    key = ticket_key(event, value)
    pending = state.get("native_foreground", {}).get(key)
    if pending and pending["expires_at"] > time.time():
        path = local_path(store.root, pending["path"])
        if file_revision(path) != pending["revision"]:
            raise LifecycleError("INVOCATION_INVALID", "issued foreground record is damaged; preserve pending work")
    else:
        path = local_path(store.root, config.state_dir + "/foreground/" + uid() + ".json")
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        private = {"schema_version": 1, "registration": value, "event": event, "expires_at": time.time() + float(config.limits["lease_seconds"])}
        write_private(path, private)
        def update(record):
            record.setdefault("native_foreground", {})[key] = {"path": path.relative_to(store.root).as_posix(),
                "revision": file_revision(path), "config_revision": file_revision(config_path), "expires_at": private["expires_at"],
                "session_key": session_key(value["integration_id"], event["binding"])}
        store.change(state["revision"], update)
        if pending:
            # Reissue only this expired opaque ticket. Semantic ownership,
            # attempt counters and pending publication remain untouched.
            local_path(store.root, pending["path"]).unlink(missing_ok=True)
    command = shlex.join([sys.executable, str(local_path(store.root, value["bundle_path"]) / "scripts/native-integration.py"),
        "foreground", "--invocation-file", str(path)])
    current = store.read()["sessions"].get(session_key(value["integration_id"], event["binding"]))
    intent = event["event"] == "task" and current and current["status"] in ("paused", "cancelled")
    return {"schema_version": 1, "operation_status": "ok", "stage_outcome": "incomplete", "work_session_status": "incomplete",
        "error": {"code": "RECOVERY_FOREGROUND_REQUIRED"}, "foreground_file": str(path),
        "next_action": {"kind": "recover", "command": command,
            "instruction": ("The prior objective remains stopped. Run this issued command with --objective new for independent user work, --objective resume for an explicitly resumed paused objective, or --objective retain_stopped to keep it stopped. Cancelled objectives cannot resume. " if intent else "") + "Run this issued foreground continuation before dependent work. At a completion boundary classify the same objective using --classification active|awaiting_user|ready_to_complete. Then follow any registered learn/dream procedure."}}


def context(result):
    content = ""
    delivery = result.get("delivery") or {}
    for artifact in delivery.get("artifacts", []):
        content += artifact["content"] + "\n"
    for unit in delivery.get("units", []):
        if not any(unit["id"] in item.get("contained_unit_ids", []) for item in delivery.get("artifacts", [])):
            content += unit.get("content", "") + "\n"
    action = result.get("next_action", {})
    if action.get("kind") not in (None, "none", "recall"):
        content += "agent-brain: " + action.get("instruction", "Complete the registered " + str(action.get("kind")) + " procedure.") + "\n"
        if action.get("command"):
            content += action["command"] + "\n"
        if result.get("invocation_file"):
            content += "Invocation file: " + result["invocation_file"] + "\n" + action.get("procedure", "")
    if not delivery.get("complete", True):
        content += "agent-brain: CONTEXT_INCOMPLETE. Restore required context before dependent work.\n"
    return content.strip()


def envelope(support, payload, result):
    name, event = support["provider"], payload["_native_event"]
    text = context(result)
    blocked = bool(result.get("foreground_file") or result.get("invocation_file") or
        result.get("next_action", {}).get("kind") == "checkpoint" or result.get("operation_status") != "ok" or
        not (result.get("delivery") or {}).get("complete", True) or result.get("action_ready") is False)
    reason = text or "agent-brain: pending registered foreground work remains incomplete."
    if name == "codex":
        if event == "PreToolUse":
            return {"hookSpecificOutput": {"hookEventName": event, "permissionDecision": "deny" if blocked else "allow",
                **({"permissionDecisionReason": reason} if blocked else {})}}
        if event in ("Stop", "SubagentStop", "PreCompact"):
            return {"decision": "block", "reason": reason} if blocked else {}
        if event == "UserPromptSubmit" and blocked:
            return {"decision": "block", "reason": reason}
        return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}
    if name == "copilot":
        if event == "preToolUse":
            return {"permissionDecision": "deny" if blocked else "allow", **({"permissionDecisionReason": reason} if blocked else {})}
        if event in ("agentStop", "subagentStop"):
            return {"decision": "block", "reason": reason} if blocked else {}
        if event == "userPromptTransformed":
            original = payload.get("transformedPrompt")
            _string(original, "transformedPrompt")
            return {"modifiedTransformedPrompt": original + "\n\n" + text}
        if event == "preCompact":
            return {}  # documented advisory output, no enforcement claim
        return {"additionalContext": text}
    if event == "PreCompress":
        return {"systemMessage": "agent-brain: context restoration pending at the validated next boundary."}
    if blocked and event in ("BeforeAgent", "BeforeTool", "BeforeModel", "AfterAgent"):
        return {"decision": "deny", "reason": reason}
    if event == "BeforeModel":
        request = dict(payload["llm_request"])
        request["messages"] = list(request["messages"]) + [{"role": "user", "content": text}]
        return {"hookSpecificOutput": {"hookEventName": event, "llm_request": request}}
    if event in ("BeforeTool", "AfterAgent"):
        return {}
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}


def callback(value, payload):
    root = Path.cwd().resolve()
    event, (config, config_path, provider, support) = normalized(value, payload, root)
    store = store_for(config, root, event["binding"]["repository_root"])
    invalidate_turn(event, value, store)
    state = store.read()
    objective_key = digest([value["integration_id"], event["binding"]["provider_session_id"]])
    if state.get("native_objectives", {}).get(objective_key, {}).get("task_id") != event["binding"]["provider_task_id"]:
        def register_objective(record):
            record.setdefault("native_objectives", {})[objective_key] = {"task_id": event["binding"]["provider_task_id"],
                "session_key": session_key(value["integration_id"], event["binding"])}
        store.change(state["revision"], register_objective)
    command = payload.get("toolArgs" if support["provider"] == "copilot" else "tool_input", {}).get("command") if event["event"] == "scope" else None
    if command is not None and foreground_command(command, value, config, config_path, store):
        result = {"operation_status": "ok", "next_action": {"kind": "none"}}
        return {"envelope": envelope(support, payload, result)}
    current = store.read().get("sessions", {}).get(session_key(value["integration_id"], event["binding"]))
    if released_turn(event, value, config, config_path, store):
        result = {"operation_status": "ok", "next_action": {"kind": "none"}}
        return {"envelope": envelope(support, payload, result), "completed": False}
    # The callback never reconciles scanner or publication work, even when a
    # fixture would allow it. A single issued stage carries the validated event.
    if (event["event"] == "task" and current and current["status"] in ("paused", "cancelled")
            or local_path(root, config.state_dir + "/publication.json").exists()
            or config.source_ingestion["enabled"] and (not current or current.get("source_checked") != current["input_revision"])
            or event["event"] in ("checkpoint", "child_stop") and (not current or current["status"] != "completed")):
        result = issue(event, config, config_path, value, store)
        return {"envelope": envelope(support, payload, result), "completed": False, "reason": context(result)}
    try:
        result, _, store = bridge_event(event, config_path, native_callback=True)
    except LifecycleError as error:
        if error.code != "RECOVERY_FOREGROUND_REQUIRED":
            raise
        result = issue(event, config, config_path, value, store)
        return {"envelope": envelope(support, payload, result), "completed": False, "reason": context(result)}
    if event["event"] == "scope":
        previous_agent = (current or {}).get("agents", {}).get(agent_key(value["integration_id"], event["binding"]["provider_agent_id"]), {})
        receipt = previous_agent.get("delivery", {})
        if not receipt.get("available") or receipt.get("guidance_revision") != digest(result.get("delivery")):
            issued = issue(event, config, config_path, value, store)
            return {"envelope": envelope(support, payload, issued), "completed": False, "reason": context(issued)}
    if payload["_native_event"] in ("PreCompact", "preCompact", "PreCompress"):
        issued = issue(event, config, config_path, value, store)
        # Advisory callbacks cannot deliver replacement model context. The
        # invalidated receipt remains unavailable until a subsequent boundary.
        return {"envelope": envelope(support, payload, issued), "completed": False, "reason": context(issued)}
    if result.get("delivery"):
        mark_output_pending(store, result["identities"], result["input_generation"], result["context_generation"])
    settlement = None
    if result.get("delivery"):
        handle = uid() + uid()
        state = store.read()
        def register_output(record):
            record.setdefault("native_output", {})[digest(handle)] = {"result_revision": digest(result),
                "registration_revision": digest(value), "expires_at": time.time() + 10,
                "session_key": session_key(value["integration_id"], event["binding"]),
                "agent_key": agent_key(value["integration_id"], event["binding"]["provider_agent_id"]),
                "input_generation": result["input_generation"], "context_generation": result["context_generation"]}
        store.change(state["revision"], register_output)
        settlement = {"handle": handle, "result": result}
    return {"envelope": envelope(support, payload, result), "settlement": settlement,
        "completed": result.get("work_session_status") == "completed", "reason": context(result)}


def literal_command_words(command):
    """Parse a literal POSIX invocation, rejecting shell evaluation syntax."""
    quote = None
    escaped = False
    for character in command:
        if character in "\r\n":
            raise ValueError("multiline command")
        if escaped:
            escaped = False
            continue
        if quote == "'":
            if character == "'":
                quote = None
            continue
        if character == "\\":
            escaped = True
        elif quote == '"':
            if character == '"':
                quote = None
            elif character in "$`":
                raise ValueError("shell expansion")
        elif character in "'\"":
            quote = character
        elif character in "$`;|&<>()*?[]{}~#":
            raise ValueError("shell evaluation")
    return shlex.split(command)


def foreground_command(command, value, config, config_path, store):
    """Admit only the exact issued continuation or a current registered stage."""
    if not isinstance(command, str):
        return False
    try:
        words = literal_command_words(command)
    except ValueError:
        return False
    if len(words) < 5 or words[0] != sys.executable:
        return False
    bundle = local_path(store.root, value["bundle_path"])
    if words[1:4] == [str(bundle / "scripts/native-integration.py"), "foreground", "--invocation-file"]:
        path = local_path(store.root, Path(words[4]).relative_to(store.root).as_posix())
        private = read_json(path.read_bytes().decode("utf-8"))
        expected = store.read().get("native_foreground", {}).get(ticket_key(private["event"], private["registration"]))
        return bool(private["registration"] == value and expected and expected["revision"] == file_revision(path)
            and expected["config_revision"] == file_revision(config_path) and expected["expires_at"] > time.time()
            and (len(words) == 5 or len(words) == 7 and (words[5] == "--classification" and words[6] in ("active", "awaiting_user", "ready_to_complete")
                or words[5] == "--objective" and words[6] in ("new", "resume", "retain_stopped") or words[5] == "--control" and words[6] in ("pause", "cancel"))))
    if words[1] == str(bundle / "scripts/agent-brain.py") and words[2] in ("learn", "dream") and words[3] in ("start", "prepare", "publish", "complete"):
        try:
            options = {}
            index = 4
            while index < len(words):
                flag = words[index]
                if flag in options:
                    return False
                if flag in ("--json", "--no-color"):
                    options[flag] = True
                    index += 1
                elif flag in ("--invocation-file", "--input", "--config") and index + 1 < len(words) and not words[index + 1].startswith("--"):
                    options[flag] = words[index + 1]
                    index += 2
                else:
                    return False
            selected = Path(options.get("--config", ".agents/context/config.json"))
            if not selected.is_absolute():
                selected = store.root / selected
            if local_path(store.root, selected.relative_to(store.root).as_posix()) != config_path:
                return False
            file = Path(options["--invocation-file"])
            if not file.is_absolute():
                file = store.root / file
            file = local_path(store.root, file.relative_to(store.root).as_posix())
            handle = read_json(file.read_bytes().decode("utf-8"))["handle"]
            from .lifecycle import validate_invocation
            validate_invocation(store.read(), handle, words[2], config, store.root, config_path)
            return True
        except (ValueError, KeyError, OSError):
            return False
    return False


def gate(payload):
    """Existing canonical source gates join ordinary native payloads."""
    root = Path.cwd().resolve()
    path = local_path(root, ".agents/context/native-registration.json")
    value = read_json(path.read_bytes().decode("utf-8"))
    event = payload.get("hook_event_name", payload.get("hookEventName"))
    if not event:
        if "source" in payload:
            event = "sessionStart" if value["provider"] == "copilot" else "SessionStart"
        elif value["provider"] == "copilot":
            event = "userPromptTransformed" if "transformedPrompt" in payload else "agentStop"
        else:
            event = "BeforeAgent"
    payload["_native_event"] = event
    normalized_event, (config, config_path, _, _) = normalized(value, payload, root)
    store = store_for(config, root, normalized_event["binding"]["repository_root"])
    invalidate_turn(normalized_event, value, store)
    if released_turn(normalized_event, value, config, config_path, store):
        # The legacy protocol's boolean means this stopping turn may proceed;
        # it neither changes session completion nor settles pending source work.
        return {"completed": True, "reason": "Source-ingest gate joined a verified parent turn checkpoint; unfinished work remains retained."}
    state = store.read()
    key = session_key(value["integration_id"], normalized_event["binding"])
    current = state["sessions"].get(key)
    agent = (current or {}).get("agents", {}).get(agent_key(value["integration_id"], normalized_event["binding"]["provider_agent_id"]))
    if current and agent and current["status"] == "completed" and agent.get("delivery", {}).get("available") and normalized_event["event"] in ("checkpoint", "task"):
        from .lifecycle import guidance, inputs
        from .source_ingestion import pending
        delivered = guidance(config, root, current["scope"], store=store)
        if (not local_path(root, config.state_dir + "/output-pending.json").exists()
                and not pending(captured_sources(config, root, file_revision(config_path)) if config.source_ingestion["enabled"] else None)
                and inputs(config, root, file_revision(config_path), current["scope"], delivered, native_callback=True) == current["input_revision"]
                and agent["delivery"]["guidance_revision"] == digest(delivered)
                and (not config.source_ingestion["enabled"] or current.get("source_checked") == current["input_revision"])):
            return {"completed": True, "reason": "Source-ingest gate joined the current checked agent-brain learn obligation."}
    # This nested gate cannot observe the outer native hook's output flush.
    # It therefore issues foreground restoration without a delivery settlement.
    # Invalidate existing context before returning even if that outer output
    # is lost. No normalized/core or legacy success exit grants fresh authority.
    if agent and normalized_event["event"] in ("startup", "resume", "context_lost"):
        def invalidate(record):
            bound = record["sessions"][key]["agents"][agent_key(value["integration_id"], normalized_event["binding"]["provider_agent_id"])]
            bound["context_generation"] += 1
            bound.pop("delivery", None)
            from .lifecycle import revoke_agent
            revoke_agent(record, bound["id"])
        store.change(state["revision"], invalidate)
    result = issue(normalized_event, config, config_path, value, store)
    return {"completed": False,
        "reason": "Source-ingest gate joined the current agent-brain learn obligation. " + context(result)}


def settle_native(value, payload):
    config, config_path, _, _ = registration(value, Path.cwd().resolve())
    store = StateStore(Path.cwd().resolve(), config.state_dir, min(0.2, float(config.limits["contention_seconds"])))
    state = store.read()
    expected = state.get("native_output", {}).get(digest(payload["handle"]))
    if (not expected or expected["result_revision"] != digest(payload["result"])
            or expected["registration_revision"] != digest(value) or expected["expires_at"] <= time.time()):
        raise LifecycleError("INVOCATION_INVALID", "native output settlement requires its exact issued receipt")
    settle_output(payload["result"], str(config_path), delivered=True, store=store, native_callback=True)
    state = store.read()
    store.change(state["revision"], lambda record: record["native_output"].pop(digest(payload["handle"])))


def foreground(path: Path, classification: str | None, control: str | None = None, objective: str | None = None):
    root = Path.cwd().resolve()
    path = local_path(root, path.absolute().relative_to(root).as_posix())
    private = read_json(path.read_bytes().decode("utf-8"))
    _keys(private, "issued foreground stage", {"schema_version", "registration", "event", "expires_at"})
    config, config_path, _, _ = registration(private["registration"], root)
    store = StateStore(root, config.state_dir, float(config.limits["contention_seconds"]))
    state = store.read()
    key = ticket_key(private["event"], private["registration"])
    expected = state.get("native_foreground", {}).get(key)
    if (not expected or expected["path"] != path.relative_to(root).as_posix() or expected["revision"] != file_revision(path)
            or expected["config_revision"] != file_revision(config_path) or expected["expires_at"] <= time.time()):
        raise LifecycleError("INVOCATION_INVALID", "foreground stage is unregistered, stale, or expired before work")
    event = validate_event(private["event"])
    parent_checkpoint = event["event"] == "checkpoint"
    old_session = state["sessions"].get(expected["session_key"])
    stopped_task = event["event"] == "task" and old_session and old_session["status"] in ("paused", "cancelled")
    if stopped_task and objective is None:
        raise LifecycleError("OBJECTIVE_INTENT_REQUIRED", "the issued task boundary requires --objective new or retain_stopped before work")
    if objective is not None and not stopped_task:
        raise LifecycleError("INVOCATION_MISMATCH", "objective intent applies only to an issued task arrival on a stopped objective")
    if objective == "resume" and old_session["status"] != "paused":
        raise LifecycleError("OBJECTIVE_RESUME_INVALID", "cancelled objectives cannot resume; independent work requires a new objective")
    if objective == "new":
        event["binding"]["provider_task_id"] = digest([expected["revision"], "new_objective"])
    if control is not None:
        event["event"] = control
    if classification is not None:
        if event["event"] not in ("checkpoint", "child_stop"):
            raise LifecycleError("INVOCATION_MISMATCH", "classification applies only to the issued checkpoint")
        event["classification"] = classification
    result, code, store = bridge_event(event, config_path, native_foreground=True, resume_paused=objective == "resume")
    if objective == "new":
        state = store.read()
        objective_key = digest([private["registration"]["integration_id"], event["binding"]["provider_session_id"]])
        def register_objective(record):
            record.setdefault("native_objectives", {})[objective_key] = {"task_id": event["binding"]["provider_task_id"],
                "session_key": session_key(private["registration"]["integration_id"], event["binding"])}
        store.change(state["revision"], register_objective)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    sys.stdout.flush()
    if result.get("delivery"):
        settle_output(result, str(config_path), delivered=True, store=store)
    from .maintenance import utc_day
    close_day = utc_day(config, root, config_path)
    state = store.read()
    def close_ticket(record):
        record["native_foreground"][key]["closed_on"] = close_day
        if objective == "new":
            record["native_foreground"][key]["session_key"] = session_key(private["registration"]["integration_id"], event["binding"])
        if (parent_checkpoint and (control in ("pause", "cancel") or classification in ("active", "awaiting_user"))
                or objective == "retain_stopped") and result["operation_status"] == "ok":
            session = record["sessions"][expected["session_key"]]
            agent = session["agents"][agent_key(private["registration"]["integration_id"], private["event"]["binding"]["provider_agent_id"])]
            record["native_foreground"][key]["turn_release"] = {
                "registration_revision": digest(private["registration"]), "status": session["status"],
                "input_generation": session["input_generation"], "input_revision": session["input_revision"],
                "scope_revision": digest(event["scope"]),
                "context_generation": agent["context_generation"], "receipt_revision": digest(agent.get("delivery"))}
    store.change(state["revision"], close_ticket)
    # Retain the registration for deterministic retries. Lifecycle generations,
    # current inputs, finite ownership and attempts remain the authority.
    return code


def main(argv=None):
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="strict")
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("action", choices=("callback", "settle", "foreground", "gate"))
    parser.add_argument("--invocation-file")
    parser.add_argument("--classification", choices=("active", "awaiting_user", "ready_to_complete"))
    parser.add_argument("--control", choices=("pause", "cancel"))
    parser.add_argument("--objective", choices=("new", "resume", "retain_stopped"))
    args = parser.parse_args(argv)
    try:
        if args.action == "foreground":
            if not args.invocation_file:
                raise LifecycleError("INVOCATION_INVALID", "foreground recovery requires an issued file before inputs")
            return foreground(Path(args.invocation_file), args.classification, args.control, args.objective)
        request = read_json(sys.stdin.read(1024 * 1024 + 1))
        if args.action == "settle":
            settle_native(request["registration"], request["payload"])
            result = {"settled": True}
        elif args.action == "gate":
            result = gate(request)
        else:
            result = callback(request["registration"], request["payload"])
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (ValueError, TypeError, KeyError, OSError, subprocess.SubprocessError) as exc:
        error = exc if isinstance(exc, LifecycleError) else LifecycleError("NATIVE_UNSUPPORTED", "native binding or input is unavailable")
        print(json.dumps(error_result(error), sort_keys=True))
        print("agent-brain native: " + error.code, file=sys.stderr)
        return error.exit_code
    except KeyboardInterrupt:
        print(json.dumps(error_result(LifecycleError("INTERRUPTED", "issued foreground work remains incomplete", exit_code=130)), sort_keys=True))
        return 130
