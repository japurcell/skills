"""Deterministic proposal mechanics; the foreground agent owns semantic judgment."""
from __future__ import annotations

from pathlib import Path
import posixpath
import re
import tempfile
import time
import subprocess
from urllib.parse import unquote, urlsplit

from .config import _keys, _object, _relative_path, _string
from .history import revision, text_bytes
from .knowledge import load_knowledge, validate_guidance_references
from .metadata import strip_metadata_comments
from .state import LifecycleError, local_path, uid


def balanced_close(text: str, start: int, opening: str, closing: str) -> int | None:
    depth = 0
    index = start
    while index < len(text):
        if text[index] == "\\":
            index += 2
            continue
        if text[index] == opening:
            depth += 1
        elif text[index] == closing:
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def inline_destinations(text: str):
    index = 0
    while index < len(text):
        if text[index] != "[" or (index and text[index - 1] == "\\"):
            index += 1
            continue
        label_end = balanced_close(text, index, "[", "]")
        if label_end is None or label_end + 1 >= len(text) or text[label_end + 1] != "(":
            index += 1
            continue
        destination_start = label_end + 2
        while destination_start < len(text) and text[destination_start] in " \t":
            destination_start += 1
        if destination_start >= len(text):
            break
        if text[destination_start] == "<":
            end = destination_start + 1
            while end < len(text) and (text[end] != ">" or text[end - 1] == "\\"):
                end += 1
            if end >= len(text):
                index = label_end + 1
                continue
            closing = end + 1
            while closing < len(text) and text[closing] in " \t":
                closing += 1
            if closing >= len(text) or text[closing] != ")":
                index = label_end + 1
                continue
            yield text[destination_start + 1:end], destination_start + 1
            index = closing + 1
            continue
        closing = balanced_close(text, label_end + 1, "(", ")")
        if closing is None:
            index = label_end + 1
            continue
        destination_end = closing
        depth = 1
        cursor = destination_start
        while cursor < closing:
            if text[cursor] == "\\":
                cursor += 2
                continue
            if text[cursor] == "(":
                depth += 1
            elif text[cursor] == ")":
                depth -= 1
            elif text[cursor] in " \t" and depth == 1:
                destination_end = cursor
                break
            cursor += 1
        if destination_end > destination_start:
            yield text[destination_start:destination_end], destination_start
        index = closing + 1


def reference_destinations(text: str):
    line_start = 0
    while line_start < len(text):
        line_end = text.find("\n", line_start)
        if line_end == -1:
            line_end = len(text)
        index = line_start
        while index < line_end and text[index] in " \t":
            index += 1
        if index < line_end and text[index] == "[":
            label_end = balanced_close(text, index, "[", "]")
            if (
                label_end is not None
                and text[index + 1] != "^"
                and label_end < line_end
                and label_end + 1 < line_end
                and text[label_end + 1] == ":"
            ):
                destination_start = label_end + 2
                while destination_start < line_end and text[destination_start] in " \t":
                    destination_start += 1
                if destination_start < line_end and text[destination_start] == "<":
                    destination_end = destination_start + 1
                    while destination_end < line_end and (text[destination_end] != ">" or text[destination_end - 1] == "\\"):
                        destination_end += 1
                    if destination_end < line_end:
                        yield text[destination_start + 1:destination_end], destination_start + 1
                else:
                    destination_end = destination_start
                    while destination_end < line_end and text[destination_end] not in " \t":
                        destination_end += 1
                    if destination_end > destination_start:
                        yield text[destination_start:destination_end], destination_start
        line_start = line_end + 1


def heading_ids(content: str) -> set[str]:
    from .metadata import _mask_markdown_code
    identifiers = set()
    counts = {}
    masked = _mask_markdown_code(content)
    matches = list(re.finditer(r'(?m)^ {0,3}#{1,6} +(.+)$', masked))
    matches += list(re.finditer(r'(?m)^([^\n]+)\n {0,3}(?:=+|-+) *$', masked))
    headings = [content[match.start(1):match.end(1)].strip().rstrip('#').strip() for match in sorted(matches, key=lambda match: match.start())]
    for title in headings:
        title = re.sub(r'\[([^]]+)\]\([^)]*\)', r'\1', title)
        title = re.sub(r'<[^>]+>', '', title)
        slug = re.sub(r'[^\w\- ]', '', title.casefold()).replace(' ', '-')
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        identifiers.add(slug + ('-' + str(count) if count else ''))
    identifiers.update(match.group(1) for match in re.finditer(r'<(?:a|span)\s+[^>]*(?:id|name)=["\']([^"\']+)', masked))
    return identifiers


def validate_links(documents: dict[str, str], root: Path, changes: list[dict]) -> None:
    """Verify affected local Markdown targets against the resulting file set."""
    from .metadata import _mask_markdown_code
    versions = {item["path"]: item["after"] for item in changes}
    for path, content in documents.items():
        masked = _mask_markdown_code(content)
        for destination, _ in (*inline_destinations(masked), *reference_destinations(masked)):
            destination = re.sub(r"\\([\\()<>])", r"\1", destination)
            parts = urlsplit(destination)
            if parts.scheme or parts.netloc or parts.path.startswith("/"):
                continue
            target = posixpath.normpath(posixpath.join(posixpath.dirname(path), unquote(parts.path))) if parts.path else path
            if path not in versions and target not in versions:
                continue
            if target.startswith("../") or (target in versions and versions[target] is None):
                raise LifecycleError("REFERENCE_INVALID", "affected local reference no longer has a valid target")
            if target not in documents and not local_path(root, target).is_file():
                raise LifecycleError("REFERENCE_INVALID", "affected local reference target is unavailable")
            if parts.fragment and target.endswith(".md"):
                target_content = documents.get(target)
                if target_content is None:
                    target_content = text_bytes(local_path(root, target))
                if unquote(parts.fragment) not in heading_ids(target_content):
                    raise LifecycleError("REFERENCE_INVALID", "affected heading fragment is unresolved")


def validate_proposal(payload: dict, config, root: Path, scope: dict, input_revision: str) -> dict:
    _keys(payload, "changed input", {"schema_version", "outcome", "review", "proposal"})
    if payload["schema_version"] != 1 or payload["outcome"] != "changed":
        raise LifecycleError("PROPOSAL_INVALID", "expected a versioned changed proposal")
    proposal = _object(payload["proposal"], "proposal")
    _keys(proposal, "proposal", {"base_input_revision", "rationale", "changes", "claims"})
    _string(proposal["rationale"], "change rationale")
    if proposal["base_input_revision"] != input_revision:
        raise LifecycleError("INPUTS_STALE", "proposal does not bind the exact current relevant inputs")
    if not isinstance(proposal["changes"], list) or not 0 < len(proposal["changes"]) <= 100:
        raise LifecycleError("PROPOSAL_INVALID", "a finite nonempty exact change set is required")
    if not isinstance(proposal["claims"], list) or not proposal["claims"]:
        raise LifecycleError("EVIDENCE_REQUIRED", "every changed stable identity needs proportional evidence")
    before = load_knowledge(config, repository_root=root, ignore_publication=True)
    prior = {unit.id: unit for unit in before.units}
    changes = []
    for value in proposal["changes"]:
        item = _object(value, "change")
        _keys(item, "change", {"path", "base_revision", "content"})
        path = _relative_path(item["path"], "change path")
        target = local_path(root, path)
        owned = [owner for owner in config.knowledge_roots if path.startswith(owner.path + "/") or owner.path == "."]
        if len(owned) != 1 or owned[0].ownership != "agent_brain" or not path.endswith(".md") or path.startswith(config.state_dir + "/"):
            raise LifecycleError("WRITABLE_SCOPE_INVALID", "publication requires one exclusively owned Markdown knowledge path")
        if target.exists() and not target.is_file():
            raise LifecycleError("WRITABLE_SCOPE_INVALID", "destination is not an ordinary file")
        content = item["content"]
        if content is not None and not isinstance(content, str):
            raise LifecycleError("PROPOSAL_INVALID", "proposed content must be complete UTF-8 text or null")
        old = text_bytes(target) if target.exists() else None
        if revision(old) != item["base_revision"]:
            raise LifecycleError("BASE_STALE", "destination differs from the exact proposed base")
        if old == content or any(change["path"].casefold() == path.casefold() for change in changes):
            raise LifecycleError("PROPOSAL_INVALID", "duplicate or unchanged publication destination")
        changes.append({"path": path, "before": old, "after": content,
                        "before_revision": revision(old), "after_revision": revision(content)})
    history_path = local_path(root, config.history_dir + "/prospective.json")
    ignored = subprocess.run(["git", "check-ignore", "-q", "--", str(history_path)], cwd=root,
        check=False, capture_output=True, timeout=1)
    if ignored.returncode == 0:
        raise LifecycleError("HISTORY_NOT_PORTABLE", "inverse history must live in a versioned unignored worktree directory")
    # Preview is isolated. No canonical write occurs before all checks succeed.
    with tempfile.TemporaryDirectory(prefix="agent-brain-preview-") as directory:
        preview = Path(directory)
        for path, content in before.documents.items():
            target = preview / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        for owner in config.knowledge_roots:
            (preview / owner.path).mkdir(parents=True, exist_ok=True)
        for item in changes:
            target = preview / item["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            if item["after"] is None:
                target.unlink(missing_ok=True)
            else:
                target.write_text(item["after"], encoding="utf-8")
        after = load_knowledge(config, repository_root=preview, ignore_publication=True)
        issues = after.issues + validate_guidance_references(after)
        if issues:
            raise LifecycleError("GUIDANCE_INVALID", "; ".join(issue.message for issue in issues))
    following = {unit.id: unit for unit in after.units}
    validate_links(after.documents, root, changes)
    paths = {item["path"] for item in changes}
    affected = {identity for identity in prior.keys() | following.keys() if prior.get(identity) != following.get(identity)}
    from .lifecycle import guidance
    delivered = guidance(config, root, scope, ignore_publication=True)
    affected.update(unit["id"] for unit in delivered["units"] if unit["loading_mode"] == "whole" and unit["path"] in paths)
    # Policy meaning is deliberately protected conservatively by exact prose,
    # plus explicit metadata. Relocation may change only its source path.
    for identity, unit in prior.items():
        successor = following.get(identity)
        if unit.kind == "policy" and (successor is None or successor.kind != "policy"
                or successor.status != unit.status or successor.applies != unit.applies
                or successor.requires != unit.requires
                or strip_metadata_comments(successor.content) != strip_metadata_comments(unit.content)):
            raise LifecycleError("POLICY_PROTECTED", "automatic publication preserves existing policy meaning, scope, references and exceptions")
    if any(unit.kind == "policy" and (identity not in prior or prior[identity].kind != "policy") for identity, unit in following.items()):
        raise LifecycleError("POLICY_PROTECTED", "automatic evidence promotion cannot introduce new instruction authority")
    from .lifecycle import scope_record
    claims = {}
    for value in proposal["claims"]:
        claim = _object(value, "claim")
        _keys(claim, "claim", {"id", "type", "action", "scope", "evidence"})
        identity = claim["id"]
        if identity in claims or identity not in affected:
            raise LifecycleError("EVIDENCE_INVALID", "claim identity is duplicate or unrelated to exact changed guidance")
        claims[identity] = claim
        current = following.get(identity) or prior.get(identity)
        claim_scope = scope_record(claim["scope"])
        current_scope = {field: list(current.applies.get(field, ())) for field in scope}
        if claim_scope != current_scope:
            raise LifecycleError("EVIDENCE_SCOPE_INVALID", "evidence applicability differs from guidance scope")
        if not any(set(values) & set(scope[field]) for field, values in claim_scope.items()):
            # Existing scoped units can use globs, but they must be delivered.
            from .lifecycle import guidance
            scoped = guidance(config, root, scope, ignore_publication=True)
            if identity not in {unit["id"] for unit in scoped["units"]}:
                raise LifecycleError("EVIDENCE_SCOPE_INVALID", "changed guidance is outside the assigned foreground scope")
        evidence = _object(claim["evidence"], "claim evidence")
        if claim["action"] in ("add", "correct") and current.status == "established":
            notes = current.evidence
            if not isinstance(notes.get("sources"), list) or not notes["sources"]:
                raise LifecycleError("EVIDENCE_REQUIRED", "learned established guidance retains a compact colocated source reference")
            _string(notes.get("verification_note"), "colocated verification note")
            _string(notes.get("verified_at"), "colocated verification date")
            if claim["type"] in ("fact", "rule"):
                source = _object(evidence.get("source"), "source identity")
                if not any(isinstance(item, dict) and item.get("source") == source.get("path") and item.get("revision") == source.get("revision") for item in notes["sources"]):
                    raise LifecycleError("EVIDENCE_INVALID", "colocated source identity/revision differs from the proposed claim")
        for field in ("verified_at", "result"):
            _string(evidence.get(field), field)
        if claim["action"] not in ("add", "correct", "prune", "relocate"):
            raise LifecycleError("EVIDENCE_INVALID", "unsupported change action")
        if claim["action"] in ("correct", "prune"):
            if evidence.get("basis") not in ("error", "obsolete", "complete_redundancy"):
                raise LifecycleError("PRUNE_UNSUPPORTED", "correction/pruning requires error, obsolescence or complete redundancy evidence")
            _string(evidence.get("basis_note"), "retirement/correction evidence")
        if claim["type"] == "tip":
            _string(evidence.get("failure"), "observed failure")
            _string(evidence.get("workaround"), "successful workaround")
        elif claim["type"] in ("fact", "rule", "relocation"):
            source = _object(evidence.get("source"), "source identity")
            _keys(source, "source identity", {"path", "revision", "note"})
            source_path = _relative_path(source["path"], "source path")
            _string(source["note"], "verification note")
            allowed = {part["path"] for part in payload["review"]["sources"]}
            if source_path not in allowed or revision(text_bytes(local_path(root, source_path))) != source["revision"]:
                raise LifecycleError("SOURCE_STALE", "claim must retain an actually reviewed exact source identity/revision")
            if claim["type"] == "rule":
                required = evidence.get("checks")
                if not isinstance(required, list) or not required or any(name not in config.checks["required"] for name in required):
                    raise LifecycleError("EVIDENCE_REQUIRED", "broader rules require configured appropriate verification checks")
        else:
            raise LifecycleError("EVIDENCE_INVALID", "unknown proportional evidence classification")
    if set(claims) != affected:
        raise LifecycleError("EVIDENCE_REQUIRED", "every affected stable unit must have evidence")
    return {"changes": changes, "affected_ids": sorted(affected), "rationale": proposal["rationale"], "evidence": proposal["claims"]}


def changed_operation(operation, store, state, handle, config, config_path, binding, payload):
    from .history import exclusive
    try:
        with exclusive(store):
            return _changed_operation(operation, store, state, handle, config, config_path, binding, payload)
    except LifecycleError as exc:
        if operation != "prepare" and exc.code == "CHECK_FAILED":
            from .lifecycle import validate_invocation
            latest = store.read()
            def failed(record):
                _, session, _, obligation = validate_invocation(record, handle, "learn", config, store.root, config_path)
                obligation.update(status="pending", stage_outcome="incomplete", retry_needed=True, reason=str(exc))
                session["status"] = "incomplete"
            store.change(latest["revision"], failed)
        raise


def _changed_operation(operation, store, state, handle, config, config_path, binding, payload):
    from . import history, publication
    from .checks import checked_review
    from .lifecycle import (guidance, inputs, file_revision, validate_invocation,
                            event_result)
    from .state import digest
    invocation, session, agent, obligation = binding
    if agent["parent"]:
        raise LifecycleError("PUBLICATION_SCOPE_INVALID", "aggregate publication belongs to the root foreground obligation")
    if operation == "prepare":
        if history.pending(store.root, config, store):
            raise LifecycleError("PUBLICATION_PENDING", "reconcile the prior publication at an eligible event first", exit_code=1)
        validated = validate_proposal(payload, config, store.root, obligation["scope"], session["input_revision"])
        checks, _ = checked_review({key: value for key, value in payload.items() if key != "proposal"} | {"outcome": "no_change"},
            config, store.root, obligation["scope"], guidance(config, store.root, obligation["scope"], store=store))
        if not all(check["exit_code"] == 0 and not check["timed_out"] for check in checks):
            raise LifecycleError("CHECK_FAILED", "configured prepare checks failed", exit_code=1, retry_eligible=True)
        latest = guidance(config, store.root, session["scope"], store=store)
        if inputs(config, store.root, file_revision(config_path), session["scope"], latest) != session["input_revision"]:
            raise LifecycleError("INPUTS_STALE", "relevant inputs changed while preparing", exit_code=1)
        path, journal = publication.prepare_journal(validated, payload, config, config_path, store.root, invocation, session, obligation, checks)
        def save(record):
            inv, bound, executing, item = validate_invocation(record, handle, "learn", config, store.root, config_path)
            item["publication"] = publication.summary(path, journal)
            item["prepared"] = digest(payload)
            item["check_receipts"] = [{"id": uid(), **check,
                "input_revision": bound["input_revision"], "config_revision": file_revision(config_path),
                "owner_generation": inv["owner_generation"], "attempt_id": inv["attempt_id"],
                "checked_at": time.time()} for check in checks]
        store.change(state["revision"], save)
    else:
        path = obligation["publication"]["history_path"]
        journal = history.read(store.root, path)
        if (journal["owner_generation"] != invocation["owner_generation"] or journal["attempt_id"] != invocation["attempt_id"]
                or digest(journal["payload"]) != obligation.get("prepared")):
            raise LifecycleError("PUBLICATION_STALE", "publication is not bound to the current exact prepared attempt", exit_code=1)
        def validate_owner():
            current = store.read()
            validate_invocation(current, handle, "learn", config, store.root, config_path)
            publication.validate_inputs(journal, config, config_path, store.root)
        validate_owner()
        if operation == "publish":
            if journal["status"] != "prepared":
                raise LifecycleError("PUBLICATION_PENDING", "this set was already published; verify completion or recover")
            publication.write_set(path, journal, config, store.root, validate_owner)
        elif operation == "complete":
            if journal["status"] != "published":
                raise LifecycleError("PUBLICATION_NOT_PUBLISHED", "publish the exact prepared set before completion")
        else:
            raise LifecycleError("OPERATION_UNAVAILABLE", "changed proposals use prepare, publish and complete")
        checks = publication.post_checks(journal, config, store.root)
        publication.barrier(config, store.root, "after_checks")
        validate_owner()
        state = store.read()
        publication.finish(store, state, config, config_path, path, journal, checks, complete=operation == "complete")
    current = store.read()
    current_session = next(value for value in current["sessions"].values() if value["id"] == session["id"])
    current_agent = next(value for value in current_session["agents"].values() if value["id"] == agent["id"])
    result = event_result(current, current_session, current_agent, None, "none")
    result.update(stage="learn", operation=operation, publication=publication.summary(path, journal),
        check_receipts=current_session["obligations"][obligation["id"]]["check_receipts"])
    result["stage_outcome"] = "changed" if operation == "complete" else "incomplete"
    return result, 0, store
