"""Finite UTC review cycles; semantic judgment remains in foreground dream."""
from __future__ import annotations

from datetime import datetime, timezone, date
import json
from pathlib import Path

from .config import _keys, _object, _relative_path, _string, _uuid
from .knowledge import load_knowledge
from .records import RetrievalScope
from .retrieval import SCOPE_FIELDS, retrieve
from .state import LifecycleError, digest, local_path, uid


def utc_day(config, root: Path, config_path: Path) -> str:
    """A fixture clock affects cadence/retention, never authority or leases."""
    clock = local_path(root, config.state_dir + "/fixture-clock.json")
    if clock.exists():
        from .lifecycle import configured_provider, file_revision, read_json
        provider_id = next((key for key, value in config.providers.items()
                            if value["enabled"] and value["kind"] == "protocol_fixture"), None)
        if provider_id is None:
            raise LifecycleError("FIXTURE_SCOPE_INVALID", "fixture clock requires a registered disposable protocol fixture")
        provider = config.providers[provider_id]
        # configured_provider also checks the actual disposable root and support.
        identity = {"id": provider_id, "core_version": provider["core_version"],
                    "adapter_version": provider["adapter_version"], "certification_id": provider["certification_id"],
                    "config_revision": file_revision(config_path)}
        configured_provider(config, config_path, root, identity)
        value = read_json(clock.read_bytes().decode("utf-8"))
        _keys(value, "fixture clock", {"utc"})
        moment = datetime.fromisoformat(_string(value["utc"], "fixture clock utc").replace("Z", "+00:00"))
        if moment.tzinfo is None:
            raise LifecycleError("FIXTURE_CLOCK_INVALID", "fixture clock needs an explicit UTC offset")
        return moment.astimezone(timezone.utc).date().isoformat()
    return datetime.now(timezone.utc).date().isoformat()


def batch_guidance(config, root, ids, *, store=None, ignore_publication=False):
    knowledge = load_knowledge(config, repository_root=root, state_store=store,
                               ignore_publication=ignore_publication)
    return retrieve(config, knowledge, RetrievalScope(None, {}, investigate=True, show_evidence=True),
                    target_ids=tuple(ids)).recall.as_json_object()


def guidance_size(delivery):
    """Count complete UTF-8 Markdown and delivered guidance metadata once."""
    markdown = sum(item["content_bytes"] for item in delivery["artifacts"])
    metadata = {"units": delivery["units"], "artifacts": [
        {key: value for key, value in item.items() if key not in ("content", "content_bytes")}
        for item in delivery["artifacts"]], "gaps": delivery["gaps"]}
    metadata_bytes = len(json.dumps(metadata, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    return markdown + metadata_bytes, markdown, metadata_bytes


def snapshot(config, root, *, store=None):
    knowledge = load_knowledge(config, repository_root=root, state_store=store)
    library = retrieve(config, knowledge, RetrievalScope(None, {}, investigate=True,
                       show_evidence=True, all_guidance=True)).recall.as_json_object()
    targets = {unit["id"]: {"id": unit["id"], "path": unit["path"], "status": unit["status"],
                          "revision": unit["input_revision"]} for unit in library["units"]}
    for mapped in config.mapped_units:
        targets.setdefault(mapped.id, {"id": mapped.id, "path": mapped.path, "status": mapped.status,
                                     "revision": digest(["unavailable", mapped.id, mapped.path])})
    return targets, library["complete"]


def detect(record, config, current, complete, today, flags=()):
    if not config.maintenance["enabled"]:
        return
    maintenance = record.setdefault("maintenance", {"last_completed_on": None, "cycle": None,
        "closed_cycles": [], "flags": [], "retired_sessions": [], "cleanup": {"pending_files": [], "removed_files": 0}})
    maintenance["flags"] = sorted(set(maintenance["flags"]) | set(flags))
    cycle = maintenance["cycle"]
    if cycle is None:
        last = maintenance["last_completed_on"]
        if last and (date.fromisoformat(today) - date.fromisoformat(last)).days < config.maintenance["interval_days"]:
            return
        cycle = {"id": uid(), "started_on": today, "targets": {key: value | {"credit": None}
                 for key, value in current.items()}, "later_ids": [], "structural_complete": complete}
        maintenance["cycle"] = cycle
    cycle["structural_complete"] = complete
    cycle["later_ids"] = sorted(set(current) - set(cycle["targets"]))
    for identity, target in cycle["targets"].items():
        now = current.get(identity)
        if now is None:
            if not target["credit"] or target["credit"].get("disposition") != "resolved":
                target["credit"] = None
            continue
        if now["revision"] != target["revision"]:
            target.update(now, credit=None)


def projection(record):
    value = record.get("maintenance")
    if value is None:
        return {"due": False, "cycle": None, "closed_cycles": []}
    cycle = value["cycle"]
    return {"due": cycle is not None, "last_completed_on": value["last_completed_on"],
            "cycle": cycle, "closed_cycles": value["closed_cycles"],
            "retired_sessions": value["retired_sessions"], "cleanup": value["cleanup"]}


def assign(record, session, config, root, current, *, store=None):
    existing = next((item for item in session["obligations"].values() if item["kind"] == "dream"), None)
    if existing:
        changed = any(identity in current and revision != current[identity]["revision"]
                      for identity, revision in existing["batch"]["targets"].items())
        if changed:
            # Changed input invalidates the assignment. Re-budget whole closures
            # while keeping deferred targets in the frozen cycle, not truncating.
            temporary = dict(session, obligations={})
            assign(record, temporary, config, root, current, store=store)
            replacement = next(iter(temporary["obligations"].values()), None)
            if replacement:
                existing.update(batch=replacement["batch"], scope=replacement["scope"])
                return
        for identity in existing["batch"]["targets"]:
            if identity in current:
                existing["batch"]["targets"][identity] = current[identity]["revision"]
        return
    cycle = record.get("maintenance", {}).get("cycle")
    if cycle is None:
        return
    remaining = [target for target in cycle["targets"].values() if target["credit"] is None]
    flags = set(record["maintenance"]["flags"])
    quiet = sorted((target for target in remaining if target["id"] not in flags and target["status"] != "candidate"),
                   key=lambda target: (target["path"], target["id"]))
    priority = sorted(remaining, key=lambda target: (target["id"] not in flags,
                      target["status"] != "candidate", target["path"], target["id"]))
    ordered = (quiet[:1] + [target for target in priority if not quiet or target["id"] != quiet[0]["id"]])
    selected = []
    delivery = None
    for target in ordered:
        trial = batch_guidance(config, root, [item["id"] for item in selected] + [target["id"]], store=store)
        size, _, _ = guidance_size(trial)
        if selected and size > config.maintenance["guidance_bytes"]:
            continue
        selected.append(target)
        delivery = trial
        if size > config.maintenance["guidance_bytes"] or len(selected) >= config.maintenance["primary_limit"]:
            break
    if not selected:
        return
    from .lifecycle import merge_scope
    scope = {field: [] for field in SCOPE_FIELDS}
    for unit in delivery["units"]:
        scope = merge_scope(scope, unit["applies"])
    scope["paths"] = sorted(set(scope["paths"]) | {item["path"] for item in delivery["artifacts"]})
    size, markdown, metadata_bytes = guidance_size(delivery)
    batch = {"cycle_id": cycle["id"], "primary_ids": [item["id"] for item in selected],
             "targets": {item["id"]: item["revision"] for item in selected},
             "content_bytes": size, "oversized": size > config.maintenance["guidance_bytes"],
             "markdown_content_bytes": markdown, "guidance_metadata_bytes": metadata_bytes,
             "quiet_id": quiet[0]["id"] if quiet else None}
    item = {"id": uid(), "kind": "dream", "scope": scope, "batch": batch,
            "input_generation": session["input_generation"], "status": "pending", "stage_outcome": "incomplete",
            "attempt_count": 0, "semantic_repairs": 0, "assigned_agent_id": None, "check_receipts": []}
    session["obligations"][item["id"]] = item


def assigned_guidance(config, root, obligation, *, store=None, ignore_publication=False):
    if obligation["kind"] == "dream":
        return batch_guidance(config, root, obligation["batch"]["primary_ids"], store=store,
                              ignore_publication=ignore_publication)
    from .lifecycle import guidance
    return guidance(config, root, obligation["scope"], store=store, ignore_publication=ignore_publication)


def session_completion(record, session, config, root, today):
    """All assigned obligations settle; unassigned cycle work may remain due."""
    if session.get("source_work") and session["checkpoint"] not in ("ready_to_complete", "completed"):
        session["status"] = session["checkpoint"]
        return
    pending = any(item["status"] != "completed" for item in session["obligations"].values())
    session.update(status="ready_to_complete" if pending else "completed",
                   checkpoint="ready_to_complete" if pending else "completed")
    if not pending:
        session["closed_on"] = today


def validate_review(payload, obligation, config, root, *, store=None):
    dispositions = payload.get("dispositions")
    if not isinstance(dispositions, list):
        raise LifecycleError("DREAM_DISPOSITIONS_REQUIRED", "dream identifies a disposition for every exact assigned primary revision")
    targets = obligation["batch"]["targets"]
    seen = set()
    for item in dispositions:
        _keys(_object(item, "dream disposition"), "dream disposition", {"id", "revision", "disposition", "factual_verification", "note"})
        if item["id"] in seen or targets.get(item["id"]) != item["revision"]:
            raise LifecycleError("DREAM_SCOPE_MISMATCH", "dispositions must bind only the exact assigned primary revisions")
        seen.add(item["id"])
        if item["disposition"] not in ("reviewed", "unresolved", "resolved") or item["factual_verification"] not in ("verified", "uncertain", "unavailable"):
            raise LifecycleError("DREAM_DISPOSITION_INVALID", "review completion and factual verification are separate explicit outcomes")
        _string(item["note"], "disposition note")
        if item["disposition"] == "resolved" and (payload.get("outcome") != "changed" or item["factual_verification"] != "verified"):
            raise LifecycleError("DREAM_DISPOSITION_INVALID", "resolved retirement needs checked changed evidence; missing access cannot prove pruning")
    if seen != set(targets):
        raise LifecycleError("DREAM_SCOPE_MISMATCH", "dispositions must cover every assigned primary identity")
    current, _ = snapshot(config, root, store=store)
    if any(current.get(identity, {}).get("revision") != revision for identity, revision in targets.items()):
        raise LifecycleError("DREAM_TARGET_STALE", "assigned target changed; restore and review its current revision at an eligible event")
    return {key: value for key, value in payload.items() if key != "dispositions"}, dispositions


def verified_publications(config, config_path, root, state):
    """Only exact checked resulting files may earn changed-target credit."""
    from .history import read, text_bytes
    from .publication import validate_inputs
    verified = {}
    for session in state["sessions"].values():
        for item in session["obligations"].values():
            if item["kind"] != "dream" or item["status"] != "completed" or not item.get("publication"):
                continue
            journal = read(root, item["publication"]["history_path"])
            if journal["status"] != "completed" or not journal["check_receipts"] or any(
                    check["exit_code"] != 0 or check["timed_out"] for check in journal["check_receipts"]):
                continue
            try:
                validate_inputs(journal, config, config_path, root)
                if all((text_bytes(local_path(root, change["path"])) if local_path(root, change["path"]).exists() else None) == change["after"]
                       for change in journal["changes"]):
                    verified[item["id"]] = journal["affected_ids"]
            except (LifecycleError, OSError):
                continue
    return verified


def credit(record, session, config, root, today, current, complete, publications):
    """Credit only after successful output delivery at the current revision."""
    cycle = record.get("maintenance", {}).get("cycle")
    if not cycle:
        return
    detect(record, config, current, complete, today)
    cycle = record["maintenance"]["cycle"]
    for item in session["obligations"].values():
        if item["kind"] != "dream" or item["status"] != "completed" or item["batch"]["cycle_id"] != cycle["id"]:
            continue
        for disposition in item.get("dispositions", []):
            identity = disposition["id"]
            target = cycle["targets"][identity]
            now = current.get(identity)
            if now and now["revision"] == item["batch"]["targets"][identity]:
                target["credit"] = disposition | {"obligation_id": item["id"], "reviewed_on": today}
            elif identity in publications.get(item["id"], []) and disposition["factual_verification"] == "verified":
                target.update(revision=now["revision"] if now else target["revision"],
                              credit=disposition | {"obligation_id": item["id"], "reviewed_on": today,
                              "reviewed_revision": disposition["revision"],
                              "revision": now["revision"] if now else target["revision"],
                              "publication_id": item["publication"]["id"]})
    cycle["structural_complete"] = complete
    cycle_sessions = [value for value in record["sessions"].values() if any(
        item["kind"] == "dream" and item["batch"]["cycle_id"] == cycle["id"] for item in value["obligations"].values())]
    if complete and all(target["credit"] is not None for target in cycle["targets"].values()) and not any(
            item["status"] != "completed" for value in cycle_sessions for item in value["obligations"].values()):
        cycle["closed_on"] = today
        record["maintenance"]["closed_cycles"].append(cycle)
        record["maintenance"].update(last_completed_on=today, cycle=None)


def validate_state(value, record):
    if not isinstance(value, dict) or set(value) != {"last_completed_on", "cycle", "closed_cycles", "flags", "retired_sessions", "cleanup"}:
        raise ValueError("invalid durable maintenance record")
    def revision(raw):
        if not isinstance(raw, str) or len(raw) != 64 or any(char not in "0123456789abcdef" for char in raw):
            raise ValueError("invalid maintenance revision")
    def day(raw):
        if not isinstance(raw, str) or date.fromisoformat(raw).isoformat() != raw:
            raise ValueError("invalid UTC calendar date")
    def identities(raw):
        if not isinstance(raw, list) or len(set(raw)) != len(raw):
            raise ValueError("invalid maintenance identity list")
        for identity in raw:
            if _uuid(identity, "maintenance identity") != identity:
                raise ValueError("noncanonical maintenance identity")
    def count(raw):
        if type(raw) is not int or raw < 0:
            raise ValueError("invalid maintenance count")
    def disposition(raw, *, credit=False):
        required = {"id", "revision", "disposition", "factual_verification", "note"}
        optional = {"reviewed_revision", "publication_id"} if credit else set()
        if credit:
            required |= {"obligation_id", "reviewed_on"}
        _keys(_object(raw, "durable disposition"), "durable disposition", required | (set(raw) & optional))
        _uuid(raw["id"], "disposition identity")
        revision(raw["revision"])
        _string(raw["note"], "disposition note")
        if raw["disposition"] not in ("reviewed", "unresolved", "resolved") or raw["factual_verification"] not in ("verified", "uncertain", "unavailable"):
            raise ValueError("invalid maintenance disposition")
        if credit:
            _uuid(raw["obligation_id"], "credit obligation")
            day(raw["reviewed_on"])
            if "reviewed_revision" in raw:
                revision(raw["reviewed_revision"])
            if "publication_id" in raw:
                _uuid(raw["publication_id"], "credit publication")
    if value["last_completed_on"] is not None:
        day(value["last_completed_on"])
    if not isinstance(value["closed_cycles"], list):
        raise ValueError("invalid closed cycle list")
    identities(value["flags"])
    identities(value["retired_sessions"])
    cleanup = _object(value["cleanup"], "cleanup")
    _keys(cleanup, "cleanup", {"pending_files", "removed_files"})
    count(cleanup["removed_files"])
    if not isinstance(cleanup["pending_files"], list) or len(set(cleanup["pending_files"])) != len(cleanup["pending_files"]):
        raise ValueError("invalid cleanup queue")
    for path in cleanup["pending_files"]:
        _relative_path(path, "cleanup path")
        if not path.startswith(".agents/context/") or Path(path).parent.name != "invocations" or Path(path).suffix != ".json":
            raise ValueError("invalid operational cleanup path")
        _uuid(Path(path).stem, "cleanup filename")
    cycles = {}
    obligations = {item["id"]: item for session in record["sessions"].values() for item in session["obligations"].values()}
    for cycle in value["closed_cycles"] + ([value["cycle"]] if value["cycle"] is not None else []):
        _keys(_object(cycle, "cycle"), "cycle", {"id", "started_on", "targets", "later_ids", "structural_complete"} | ({"closed_on"} if "closed_on" in cycle else set()))
        _uuid(cycle["id"], "cycle id")
        if cycle["id"] in cycles:
            raise ValueError("duplicate maintenance cycle")
        cycles[cycle["id"]] = cycle
        day(cycle["started_on"])
        if "closed_on" in cycle:
            day(cycle["closed_on"])
        elif cycle in value["closed_cycles"]:
            raise ValueError("closed cycle lacks closure date")
        if type(cycle["structural_complete"]) is not bool:
            raise ValueError("invalid cycle structural outcome")
        _object(cycle["targets"], "finite targets")
        identities(cycle["later_ids"])
        if set(cycle["later_ids"]) & set(cycle["targets"]):
            raise ValueError("later targets overlap frozen coverage")
        for identity, target in cycle["targets"].items():
            _uuid(identity, "target id")
            _keys(_object(target, "target"), "target", {"id", "path", "status", "revision", "credit"})
            if target["id"] != identity or target["status"] not in ("established", "candidate"):
                raise ValueError("invalid target identity/status")
            _relative_path(target["path"], "target path")
            revision(target["revision"])
            checked = target["credit"]
            if checked is not None:
                disposition(checked, credit=True)
                item = obligations[checked["obligation_id"]]
                if (checked["id"] != identity or checked["revision"] != target["revision"] or item["kind"] != "dream"
                        or item["status"] != "completed" or item["batch"]["cycle_id"] != cycle["id"]
                        or item["batch"]["targets"].get(identity) != checked.get("reviewed_revision", checked["revision"])):
                    raise ValueError("credit does not bind an exact completed assigned revision")
                if "publication_id" in checked and (not item.get("publication") or item["publication"]["id"] != checked["publication_id"]
                        or identity not in item["publication"]["affected_ids"]):
                    raise ValueError("credit publication does not change its target")
            elif "closed_on" in cycle:
                raise ValueError("closed cycle contains unchecked coverage")
    for item in obligations.values():
        if item["kind"] != "dream":
            continue
        batch = _object(item["batch"], "dream batch")
        _keys(batch, "dream batch", {"cycle_id", "primary_ids", "targets", "content_bytes", "markdown_content_bytes",
                                      "guidance_metadata_bytes", "oversized", "quiet_id"})
        cycle = cycles[batch["cycle_id"]]
        identities(batch["primary_ids"])
        if not 0 < len(batch["primary_ids"]) <= 5 or set(batch["targets"]) != set(batch["primary_ids"]) or not set(batch["primary_ids"]).issubset(cycle["targets"]):
            raise ValueError("invalid finite dream assignment")
        for checked in batch["targets"].values():
            revision(checked)
        for field in ("content_bytes", "markdown_content_bytes", "guidance_metadata_bytes"):
            count(batch[field])
        if batch["content_bytes"] != batch["markdown_content_bytes"] + batch["guidance_metadata_bytes"] or type(batch["oversized"]) is not bool:
            raise ValueError("invalid dream measurement")
        if batch["oversized"] and len(batch["primary_ids"]) != 1:
            raise ValueError("oversized closure must run alone")
        if batch["quiet_id"] is not None and batch["quiet_id"] not in batch["primary_ids"]:
            raise ValueError("invalid quiet slot")
        if "dispositions" in item:
            if not isinstance(item["dispositions"], list):
                raise ValueError("invalid dream dispositions")
            identities([part["id"] for part in item["dispositions"]])
            if {part["id"] for part in item["dispositions"]} != set(batch["primary_ids"]):
                raise ValueError("dispositions differ from assignment")
            for part in item["dispositions"]:
                disposition(part)
                if part["revision"] != batch["targets"][part["id"]]:
                    raise ValueError("disposition revision differs from assignment")


def prepare_cleanup(record, config, root, today, *, retain_session=None):
    """Retire only an unreferenced closed component of operational records."""
    value = record.get("maintenance")
    if value is None:
        return
    value["retired_sessions"] = []
    from .lifecycle import read_json
    from .history import read
    pins_path = local_path(root, config.state_dir + "/validation-pins.json")
    pins = {"schema_version": 1, "work_session_ids": [], "cycle_ids": []}
    if pins_path.exists():
        pins = read_json(pins_path.read_bytes().decode("utf-8"))
        _keys(pins, "validation pins", {"schema_version", "work_session_ids", "cycle_ids"})
        if type(pins["schema_version"]) is not int or pins["schema_version"] != 1:
            raise LifecycleError("RETENTION_REFERENCES_UNAVAILABLE", "preserve records with invalid validation pins", exit_code=1)
        for field in ("work_session_ids", "cycle_ids"):
            if not isinstance(pins[field], list):
                raise LifecycleError("RETENTION_REFERENCES_UNAVAILABLE", "preserve records with invalid validation pins", exit_code=1)
            for identity in pins[field]:
                _uuid(identity, "validation pin")
    protected = set(pins["work_session_ids"]) | ({retain_session} if retain_session else set())
    history_root = local_path(root, config.history_dir)
    if history_root.exists():
        for path in history_root.glob("*.json"):
            journal = read(root, path.relative_to(root).as_posix())
            protected.add(journal["work_session_id"])
    retention = config.maintenance["retention_days"]
    def old(closed):
        return closed is not None and (date.fromisoformat(today) - date.fromisoformat(closed)).days >= retention
    retained_cycles = [cycle for cycle in value["closed_cycles"]
                       if cycle["id"] in pins["cycle_ids"] or not old(cycle.get("closed_on"))]
    references = {credit["obligation_id"] for cycle in retained_cycles + ([value["cycle"]] if value["cycle"] else [])
                  for target in cycle["targets"].values() if (credit := target["credit"]) is not None}
    for key, session in list(record["sessions"].items()):
        if (session["id"] in protected or session["status"] != "completed" or not old(session.get("closed_on"))
                or any(item["status"] != "completed" or item["id"] in references for item in session["obligations"].values())):
            continue
        invocations = [(identity, invocation) for identity, invocation in record["invocations"].items()
                       if invocation["session_key"] == key]
        owner = record["owner"]
        if any(not invocation["revoked"] for _, invocation in invocations) or (owner and owner["obligation_id"] in session["obligations"]):
            continue
        for identity, invocation in invocations:
            path = Path(invocation["file"]).relative_to(root).as_posix()
            if not path.startswith(config.state_dir + "/invocations/"):
                raise LifecycleError("RETENTION_REFERENCES_UNAVAILABLE", "preserve unexpected invocation path", exit_code=1)
            value["cleanup"]["pending_files"].append(path)
            del record["invocations"][identity]
        value["retired_sessions"].append(session["id"])
        del record["sessions"][key]
    referenced_cycles = {item["batch"]["cycle_id"] for session in record["sessions"].values()
                         for item in session["obligations"].values() if item["kind"] == "dream"}
    value["closed_cycles"] = [cycle for cycle in value["closed_cycles"]
                              if cycle in retained_cycles or cycle["id"] in referenced_cycles]


def clean_files(store, config):
    state = store.read()
    pending = state.get("maintenance", {}).get("cleanup", {}).get("pending_files", [])
    removed = []
    for path in pending:
        # No database, binding, evidence, history, candidate or recovery path is eligible.
        if not path.startswith(config.state_dir + "/invocations/") or Path(path).parent.as_posix() != config.state_dir + "/invocations":
            raise LifecycleError("RETENTION_REFERENCES_UNAVAILABLE", "preserve unexpected cleanup path", exit_code=1)
        _uuid(Path(path).stem, "retired invocation filename")
        try:
            local_path(store.root, path).unlink(missing_ok=True)
            removed.append(path)
        except OSError:
            break
    if removed:
        def settle(record):
            cleanup = record["maintenance"]["cleanup"]
            cleanup["pending_files"] = [path for path in cleanup["pending_files"] if path not in removed]
            cleanup["removed_files"] += len(removed)
        store.change(state["revision"], settle)
