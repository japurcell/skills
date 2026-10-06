"""Optional configured canonical scanner boundary and foreground evidence checks."""
from __future__ import annotations

import subprocess
import sys
import json
import tempfile
import shutil
from pathlib import Path

from .config import _keys, _object, _relative_path, _string
from .state import LifecycleError, local_path


def snapshot(config, root: Path, *, reconcile: bool = False) -> dict | None:
    if not config.source_ingestion["enabled"]:
        return None
    from .lifecycle import file_revision, read_json
    try:
        engine = local_path(root, config.source_ingestion["engine_path"])
        if file_revision(engine) != config.source_ingestion["engine_revision"]:
            raise ValueError("configured source engine bytes no longer match their trusted revision")
        result = subprocess.run([sys.executable, str(engine), "--repository-root", str(root), "--json",
            *(["--reconcile"] if reconcile else [])], cwd=root, capture_output=True, timeout=60, check=False)
        value = read_json(result.stdout.decode("utf-8"))
        if result.returncode or value.get("schema_version") != 1:
            raise ValueError("canonical source engine could not provide current checked inputs")
        _keys(value, "source snapshot", {"schema_version", "entries", "blocking", "orphans", "changes", "files", "skill_path", "skill_available"})
        if type(value["skill_available"]) is not bool or not isinstance(value["files"], dict):
            raise ValueError("canonical source snapshot is invalid")
        for path, revision in value["files"].items():
            if file_revision(local_path(root, _relative_path(path, "source input path"))) != revision:
                raise ValueError("source input changed while the canonical scanner ran")
        for group in ("entries", "blocking", "orphans"):
            if not isinstance(value[group], list):
                raise ValueError("source entry list is invalid")
            for entry in value[group]:
                _relative_path(entry["source_path"], "source identity")
                local_path(root, entry["summary_path"])
        if not isinstance(value["changes"], list):
            raise ValueError("source change list is invalid")
        for name in value["changes"]:
            _relative_path(name, "source changed identity")
        return value
    except (ValueError, OSError, UnicodeError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        raise LifecycleError("SOURCE_INGESTION_UNAVAILABLE", str(exc), exit_code=1,
            retry_eligible=True) from exc


def pending(value: dict | None) -> list[str]:
    return sorted({entry["source_path"] for entry in value["blocking"] + value["orphans"]} | set(value["changes"])) if value else []


def package(config, root, session):
    value = snapshot(config, root)
    if value is not None:
        value["required_source_work"] = session.get("source_work", [])
        value["instruction"] = ("In this eligible foreground learn pass, load the focused ingest-source skill once for all blocking entries. "
            "Review renamed/removed orphan provenance separately. Author proposed summaries and knowledge outside canonical paths, "
            "then use this learn invocation to prepare, publish and complete their exact reversible set with attributable source evidence. "
            "Never directly overwrite semantic artifacts and relabel them through recovery. Verified pre-pass facts may justify scoped no-change. "
            "Missing access keeps this pass incomplete.")
    return value


def validate_review(payload, config, root, scope, guidance, source_work=None):
    value = snapshot(config, root)
    if value is None:
        if "source_ingestion" in payload:
            raise LifecycleError("SOURCE_EVIDENCE_UNEXPECTED", "source ingestion is not configured")
        return
    work = source_work if source_work is not None else pending(value)
    if (work or value["blocking"]) and not value["skill_available"]:
        raise LifecycleError("SOURCE_INGESTION_UNAVAILABLE", "focused ingest-source skill access is unavailable", exit_code=1)
    if any(not entry["summary_resolved"] for entry in value["blocking"]):
        raise LifecycleError("SOURCE_INGESTION_PENDING", "existing blocking sources still require focused semantic ingestion", exit_code=1)
    if not work and "source_ingestion" not in payload:
        return
    evidence = payload.get("source_ingestion")
    if not isinstance(evidence, dict):
        raise LifecycleError("SOURCE_EVIDENCE_REQUIRED", "scanner exit and manifest state cannot establish semantic integration", exit_code=1)
    _keys(evidence, "source ingestion evidence", {"entries", "orphans"})
    current = {item["source_path"]: item for item in value["entries"]}
    orphans = {item["source_path"]: item for item in value["orphans"]}
    required = set(work) | set(pending(value))
    seen = set()
    known = {item["id"]: item for item in guidance["units"]}
    from .knowledge import load_knowledge
    actual_units = {unit.id: unit for unit in load_knowledge(config, repository_root=root, ignore_publication=True).units}
    for group in ("entries", "orphans"):
        if not isinstance(evidence[group], list):
            raise LifecycleError("SOURCE_EVIDENCE_REQUIRED", "source evidence must enumerate exact current work", exit_code=1)
        for entry in evidence[group]:
            _object(entry, "source evidence entry")
            fields = {"source_path", "summary_revision", "note"} | ({"source_revision", "knowledge_ids"} if group == "entries" else {"disposition"})
            _keys(entry, "source evidence entry", fields)
            name = _relative_path(entry["source_path"], "source evidence identity")
            _string(entry["note"], "semantic integration note")
            if name in seen or name not in required:
                raise LifecycleError("SOURCE_EVIDENCE_INVALID", "source evidence is duplicated or outside the current joined work", exit_code=1)
            seen.add(name)
            actual = current.get(name) if group == "entries" else orphans.get(name)
            if group == "entries":
                ids = entry["knowledge_ids"]
                if (not actual or actual["source_revision"] != entry["source_revision"] or
                        not isinstance(ids, list) or not ids or len(set(ids)) != len(ids) or not set(ids).issubset(known)):
                    raise LifecycleError("SOURCE_EVIDENCE_STALE", "integration must name exact current source and delivered knowledge identities", exit_code=1)
                raw_path = ".agents/sources/" + name
                for identity in ids:
                    notes = actual_units[identity].evidence
                    if (not isinstance(notes.get("sources"), list) or not any(isinstance(source, dict)
                            and source.get("source") == raw_path and isinstance(source.get("revision"), str)
                            for source in notes["sources"]) or not notes.get("verification_note") or not notes.get("verified_at")):
                        raise LifecycleError("SOURCE_EVIDENCE_REQUIRED", "integrated knowledge retains attributable current source notes; a caller assertion alone is insufficient", exit_code=1)
            elif name in current or entry["disposition"] not in ("retained", "removed"):
                raise LifecycleError("SOURCE_ORPHAN_INVALID", "orphan review is separate from existing-source ingestion", exit_code=1)
            actual_revision = actual["summary_revision"] if actual else None
            if actual_revision != entry["summary_revision"] or (group == "orphans" and (entry["disposition"] == "removed") != (actual_revision is None)):
                raise LifecycleError("SOURCE_EVIDENCE_STALE", "source evidence differs from the actual current summary artifact", exit_code=1)
    if seen != required:
        raise LifecycleError("SOURCE_EVIDENCE_REQUIRED", "every joined source and orphan requires a current semantic disposition", exit_code=1)


def knowledge_bases(config, root, source_state=None):
    from .knowledge import load_knowledge
    from .history import revision
    value = source_state if source_state is not None else snapshot(config, root)
    if value is None:
        return {}
    knowledge = load_knowledge(config, repository_root=root, ignore_publication=True)
    result = {path: revision(content) for path, content in knowledge.documents.items()
        if not path.startswith(".agents/sources/") and any(owner.ownership == "agent_brain" and
            (owner.path == "." or path.startswith(owner.path + "/")) for owner in config.knowledge_roots)}
    result.update({path: fingerprint for path, fingerprint in value["files"].items() if path.endswith(".summary.md")})
    return result


def validate_bases(config, root, session, source_state=None):
    if not session.get("source_work"):
        return
    actual = knowledge_bases(config, root, source_state)
    expected = session.get("source_baseline", {})
    if actual != expected:
        raise LifecycleError("SOURCE_UNJOURNALED_CHANGE", "foreground source integration changed canonical artifacts outside checked reversible publication; preserve edits and restore exact pre-pass bases", exit_code=1)


def prior_work(config, root, state, current_key, scope, source_state, config_path):
    """A new task cannot erase a known unresolved source provenance gap."""
    if source_state is None:
        return []
    import fnmatch
    from .lifecycle import guidance, inputs, file_revision
    delivered_paths = {item["path"] for item in guidance(config, root, scope, ignore_publication=True)["artifacts"]}
    actual = knowledge_bases(config, root, source_state)
    resolved = set()
    for session in state["sessions"].values():
        if session.get("source_checked") == session["input_revision"] and session.get("source_work"):
            current = inputs(config, root, file_revision(config_path), session["scope"], guidance(config, root, session["scope"], ignore_publication=True))
            if session["source_checked"] == current:
                resolved.update(session["source_work"])
    carried = set()
    for key, session in state["sessions"].items():
        if key == current_key or not session.get("source_work") or session.get("source_checked") == session["input_revision"]:
            continue
        if set(session["source_work"]).issubset(resolved):
            continue
        expected = dict(session.get("source_baseline", {}))
        for entry in source_state["blocking"]:
            if not entry["summary_resolved"] and entry["summary_path"] not in expected:
                expected[entry["summary_path"]] = entry["summary_revision"]
        changed = {path for path in set(actual) | set(expected) if actual.get(path) != expected.get(path)}
        overlaps = any(fnmatch.fnmatchcase(left, right) or fnmatch.fnmatchcase(right, left)
            or left.startswith(right.rstrip("/") + "/") or right.startswith(left.rstrip("/") + "/")
            for left in scope["paths"] for right in session["scope"]["paths"])
        if not overlaps and not changed.intersection(delivered_paths):
            continue
        if changed:
            raise LifecycleError("SOURCE_UNJOURNALED_CHANGE", "an unresolved prior source pass changed dependent canonical artifacts outside checked publication; preserve edits and restore its exact bases", exit_code=1)
        if session["status"] not in ("paused", "cancelled"):
            raise LifecycleError("SOURCE_PRIOR_WORK_PENDING", "a prior objective retains dependent source learning; restore that registered foreground obligation before dependent work", exit_code=1)
        carried.update(session["source_work"])
    return sorted(carried)


def validate_stage(payload, config, root, scope, current, session, stage):
    if stage == "dream" and session.get("source_work"):
        if session.get("source_checked") != session["input_revision"]:
            raise LifecycleError("SOURCE_INGESTION_PENDING", "current source learning must settle before assigned maintenance", exit_code=1)
        if "source_ingestion" in payload:
            raise LifecycleError("SOURCE_EVIDENCE_UNEXPECTED", "assigned dream joins checked source learning without another ingest pass", exit_code=1)
        return
    validate_review(payload, config, root, scope, current, session.get("source_work", []))


def validate_preview(payload, changes, config, root, scope, source_work):
    """Use real canonical scanner and knowledge loader on an isolated exact set."""
    if not config.source_ingestion["enabled"]:
        return
    from .knowledge import load_knowledge
    from .lifecycle import guidance
    source_state = snapshot(config, root)
    with tempfile.TemporaryDirectory(prefix="agent-brain-source-preview-") as directory:
        preview = Path(directory).resolve()
        paths = set(source_state["files"]) | {config.source_ingestion["engine_path"]}
        for path in paths:
            target = preview / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(local_path(root, path), target)
        for path, content in load_knowledge(config, repository_root=root, ignore_publication=True).documents.items():
            target = preview / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        for change in changes:
            target = preview / change["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            if change["after"] is None:
                target.unlink(missing_ok=True)
            else:
                target.write_bytes(change["after"].encode("utf-8"))
        validate_review(payload, config, preview, scope, guidance(config, preview, scope, ignore_publication=True), source_work)


def settle(payload, config, root):
    if not config.source_ingestion["enabled"] or "source_ingestion" not in payload:
        return
    from .lifecycle import read_json
    before = snapshot(config, root)
    evidence = payload["source_ingestion"]
    reviewed = {item["source_path"] for item in evidence["entries"] + evidence["orphans"]}
    if not set(pending(before)).issubset(reviewed):
        raise LifecycleError("SOURCE_EVIDENCE_STALE", "new source work appeared before checked settlement", exit_code=1)
    with tempfile.TemporaryDirectory(prefix="agent-brain-source-settle-") as directory:
        evidence_path = Path(directory) / "evidence.json"
        evidence_path.write_text(json.dumps(evidence | {"checked_files": before["files"]}), encoding="utf-8")
        result = subprocess.run([sys.executable, str(local_path(root, config.source_ingestion["engine_path"])),
            "--repository-root", str(root), "--settle", str(evidence_path), "--json"], cwd=root,
            capture_output=True, timeout=60, check=False)
        after = read_json(result.stdout.decode("utf-8"))
        if result.returncode or after.get("schema_version") != 1:
            raise LifecycleError("SOURCE_INGESTION_UNAVAILABLE", "current source manifest settlement did not finish; retain pending foreground work", exit_code=1)
        expected = {path: revision for path, revision in before["files"].items() if path != ".agents/memory/sources/source-ingest-manifest.json"}
        actual = {path: revision for path, revision in after["files"].items() if path != ".agents/memory/sources/source-ingest-manifest.json"}
        if actual != expected or after["blocking"] or after["changes"]:
            raise LifecycleError("SOURCE_EVIDENCE_STALE", "source inputs changed during settlement; retain current foreground work", exit_code=1)
