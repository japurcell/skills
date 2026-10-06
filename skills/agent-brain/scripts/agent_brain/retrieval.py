"""Resolve applicable guidance and its required-reference closure."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable
from collections import Counter, deque
from dataclasses import dataclass

from .knowledge import KnowledgeBase
from .metadata import MetadataIssue, strip_metadata_comments
from .records import (
    AgentBrainConfig,
    DeliveryArtifact,
    GuidanceLoadingMode,
    GuidanceUnit,
    RecallResult,
    RecalledUnit,
    RetrievalScope,
)


NOTICE = "Informational output only; this does not confirm agent delivery or application."
SCOPE_FIELDS = ("paths", "concepts", "actions", "dependencies", "providers", "runtimes")


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    recall: RecallResult
    exit_code: int


def retrieve(
    config: AgentBrainConfig,
    knowledge: KnowledgeBase,
    scope: RetrievalScope,
    *, target_ids: tuple[str, ...] | None = None,
) -> RetrievalResult:
    issues = list(knowledge.issues)
    counts = Counter(unit.id for unit in knowledge.units)
    for unit_id, count in counts.items():
        if count > 1:
            duplicate = next(unit for unit in knowledge.units if unit.id == unit_id)
            issues.append(MetadataIssue("ABM002", duplicate.path, 1, 1,
                                        f"duplicate guidance unit id {unit_id}"))
    by_id = {unit.id: unit for unit in knowledge.units if counts[unit.id] == 1}

    selected: list[tuple[GuidanceUnit, GuidanceLoadingMode]] = []
    selected_ids: set[str] = set()
    pending = deque[tuple[GuidanceUnit, GuidanceLoadingMode]]()

    def select(
        unit_id: str,
        mode: GuidanceLoadingMode,
        *,
        reason_path: str = "startup",
        mandatory: bool = False,
    ) -> None:
        unit = by_id.get(unit_id)
        if unit is None:
            issues.append(MetadataIssue("ABM003", reason_path, 1, 1,
                                        f"required guidance unit {unit_id} is unresolved"))
            return
        if unit.status == "candidate" and mandatory:
            issues.append(MetadataIssue("ABM003", reason_path, 1, 1,
                                        f"candidate {unit_id} cannot satisfy mandatory established guidance"))
            if not scope.investigate:
                return
        elif unit.status == "candidate" and not scope.investigate:
            return
        if unit_id in selected_ids:
            if mode == "whole":
                for index, (existing, existing_mode) in enumerate(selected):
                    if existing.id == unit_id and existing_mode != "whole":
                        selected[index] = (existing, "whole")
                        pending.append((existing, "whole"))
            return
        selected_ids.add(unit_id)
        selected.append((unit, mode))
        pending.append((unit, mode))

    for startup_read in config.startup:
        select(startup_read.id, startup_read.loading_mode, mandatory=True)

    if target_ids is not None:
        for identity in target_ids:
            select(identity, "unit", reason_path="assigned dream batch")
    has_task_scope = bool(scope.query) or any(scope.selectors.get(field) for field in SCOPE_FIELDS)
    uncertain_fields: set[str] = set()
    if not has_task_scope and not scope.all_guidance:
        routed = [unit for unit in by_id.values()
                  if unit.kind == "policy" and unit.status == "established"
                  and all(not values for values in unit.applies.values())]
        scope_status = "task_unknown"
    elif not has_task_scope and scope.all_guidance:
        routed = list(by_id.values())
        scope_status = "library"
    else:
        uncertain_fields: set[str] = set()
        for field in SCOPE_FIELDS:
            requested = scope.selectors.get(field, ())
            if not requested:
                continue
            constraints = [value for unit in by_id.values() for value in unit.applies.get(field, ())]
            if field == "paths":
                unknown = [path for path in requested
                           if not any(_glob_match(pattern, path) for pattern in constraints)]
            else:
                known = {value.casefold() for value in constraints}
                unknown = [value for value in requested if value.casefold() not in known]
            if unknown:
                uncertain_fields.add(field)
                issues.append(MetadataIssue(
                    "ABM010", "retrieval scope", 1, 1,
                    f"{field} selector(s) {', '.join(unknown)} are not represented by indexed metadata; scope broadened",
                ))

        query_unknown = bool(scope.query) and not any(_text_match(unit, scope.query) for unit in by_id.values())
        if query_unknown:
            issues.append(MetadataIssue(
                "ABM010", "retrieval scope", 1, 1,
                f"query {scope.query!r} matched no indexed text; scope broadened",
            ))
        routed = [unit for unit in by_id.values()
                  if _matches_scope(unit, scope, uncertain_fields=uncertain_fields, ignore_query=query_unknown)]
        scope_status = "broadened" if uncertain_fields or query_unknown else "scoped"
    routed.sort(key=lambda unit: (0 if unit.status == "established" and unit.kind == "policy" else
                                  1 if unit.status == "established" else 2,
                                  unit.path, unit.heading or "", unit.id))
    for unit in routed:
        if target_ids is not None:
            continue
        if unit.status == "candidate" and not scope.investigate:
            continue
        select(unit.id, "unit", reason_path=unit.path)

    processed_references: set[str] = set()
    processed_whole: set[str] = set()
    while pending:
        unit, loading_mode = pending.popleft()
        if loading_mode == "whole":
            if unit.id not in processed_whole:
                processed_whole.add(unit.id)
                for contained_id in knowledge.contained_ids.get(unit.path, ()):
                    if contained_id == unit.id:
                        continue
                    select(contained_id, "unit", reason_path=unit.path)
        if unit.id in processed_references:
            continue
        processed_references.add(unit.id)
        for required in unit.requires:
            target = by_id.get(required.id)
            if target is None:
                issues.append(MetadataIssue("ABM003", unit.path, 1, 1,
                                            f"required reference {required.id} is unresolved"))
                continue
            select(required.id, required.loading_mode, reason_path=unit.path,
                   mandatory=unit.status == "established")

    revisions: dict[str, tuple[str, str]] = {}
    visiting: set[str] = set()

    def unit_revisions(unit_id: str) -> tuple[str, str]:
        if unit_id in revisions:
            return revisions[unit_id]
        unit = by_id[unit_id]
        content_revision = _sha256(strip_metadata_comments(unit.content).encode("utf-8"))
        if unit_id in visiting:
            issues.append(MetadataIssue("ABM003", unit.path, 1, 1,
                                        f"required-reference cycle includes {unit_id}"))
            return content_revision, _sha256(f"cycle:{unit_id}".encode("utf-8"))
        visiting.add(unit_id)
        dependencies: list[dict[str, str]] = []
        for required in unit.requires:
            target = by_id.get(required.id)
            if target is not None:
                _, target_input = unit_revisions(target.id)
                if required.loading_mode == "whole" and target.path in knowledge.documents:
                    target_input = _whole_artifact_input(
                        knowledge.documents[target.path],
                        knowledge.contained_ids.get(target.path, (target.id,)),
                        whole_unit_revisions,
                    )
                dependencies.append({"id": target.id, "loading_mode": required.loading_mode,
                                     "input_revision": target_input})
        visiting.discard(unit_id)
        payload = {
            "id": unit.id,
            "path": unit.path,
            "selector": unit.selector,
            "heading": unit.heading,
            "kind": unit.kind,
            "status": unit.status,
            "applies": {name: list(values) for name, values in sorted(unit.applies.items())},
            "requires": [{"id": item.id, "loading_mode": item.loading_mode} for item in unit.requires],
            "evidence": unit.evidence,
            "content_revision": content_revision,
            "dependency_revisions": dependencies,
        }
        input_revision = _sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True,
                                            separators=(",", ":")).encode("utf-8"))
        revisions[unit_id] = (content_revision, input_revision)
        return revisions[unit_id]

    def whole_unit_revisions(unit_id: str) -> tuple[str, str]:
        if unit_id not in by_id:
            return "", _sha256(f"unresolved:{unit_id}".encode("utf-8"))
        return unit_revisions(unit_id)

    recalled_units: list[RecalledUnit] = []
    for unit, loading_mode in selected:
        content_revision, input_revision = unit_revisions(unit.id)
        evidence = unit.evidence if scope.show_evidence else _evidence_summary(unit.evidence)
        recalled_units.append(
            RecalledUnit(
                id=unit.id,
                path=unit.path,
                kind=unit.kind,
                status=unit.status,
                loading_mode=loading_mode,
                source=unit.source,
                applies=unit.applies,
                content_revision=content_revision,
                input_revision=input_revision,
                requires=unit.requires,
                evidence=evidence,
            )
        )

    artifacts = _delivery_artifacts(selected, knowledge, whole_unit_revisions)
    startup_ids = {item.id for item in config.startup}
    def affected(issue):
        if issue.code != "ABM007" or issue.path not in knowledge.unavailable:
            return True
        units = knowledge.unavailable[issue.path]
        if not units:
            return True
        return scope.all_guidance or any(unit.id in startup_ids or (
            _matches_scope(unit, scope, uncertain_fields=uncertain_fields) if has_task_scope
            else unit.kind == "policy" and all(not values for values in unit.applies.values())) for unit in units)
    issues = [issue for issue in issues if affected(issue)]
    gaps = tuple(_gap(issue) for issue in _deduplicate_issues(issues))
    has_blocking_gap = any(gap["code"] != "ABM010" for gap in gaps)
    recall = RecallResult(
        1,
        "error" if has_blocking_gap else "ok",
        "recall",
        True,
        NOTICE,
        scope_status,
        not gaps,
        gaps,
        tuple(recalled_units),
        artifacts,
    )
    return RetrievalResult(recall, 1 if has_blocking_gap else 0)


def _matches_scope(
    unit: GuidanceUnit,
    scope: RetrievalScope,
    *,
    uncertain_fields: set[str] | None = None,
    ignore_query: bool = False,
) -> bool:
    for field in SCOPE_FIELDS:
        if uncertain_fields and field in uncertain_fields:
            continue
        requested = scope.selectors.get(field, ())
        constrained = unit.applies.get(field, ())
        if not requested or not constrained:
            continue
        if field == "paths":
            if not any(_glob_match(pattern, path) for pattern in constrained for path in requested):
                return False
        else:
            known = {value.casefold() for value in requested}
            if not any(value.casefold() in known for value in constrained):
                return False
    if scope.query and not ignore_query and not _text_match(unit, scope.query):
        if unit.kind == "policy" and unit.status == "established":
            return True
        # Structured routes are sufficient even when the query words are absent.
        if not any(scope.selectors.get(field) and unit.applies.get(field) and
                   _dimension_matches(field, unit.applies[field], scope.selectors[field])
                   for field in SCOPE_FIELDS):
            return False
    return True


def _dimension_matches(field: str, constrained: tuple[str, ...], requested: tuple[str, ...]) -> bool:
    if field == "paths":
        return any(_glob_match(pattern, path) for pattern in constrained for path in requested)
    known = {value.casefold() for value in requested}
    return any(value.casefold() in known for value in constrained)


def _text_match(unit: GuidanceUnit, query: str) -> bool:
    terms = {term.casefold() for term in re.findall(r"[\w'-]+", query, flags=re.UNICODE) if len(term) > 1}
    if not terms:
        return True
    searchable = " ".join((unit.heading or "", " ".join(unit.applies.get("concepts", ())), unit.content)).casefold()
    return any(term in searchable for term in terms)


def _glob_match(pattern: str, path: str) -> bool:
    pattern_segments = pattern.split("/")
    path_segments = path.split("/")

    def match_segment(segment_pattern: str, segment: str) -> bool:
        expression = "^" + "".join("[^/]*" if char == "*" else
                                   "[^/]" if char == "?" else re.escape(char)
                                   for char in segment_pattern) + "$"
        return re.match(expression, segment) is not None

    def visit(pattern_index: int, path_index: int) -> bool:
        if pattern_index == len(pattern_segments):
            return path_index == len(path_segments)
        if pattern_segments[pattern_index] == "**":
            if visit(pattern_index + 1, path_index):
                return True
            return path_index < len(path_segments) and visit(pattern_index, path_index + 1)
        return (path_index < len(path_segments) and
                match_segment(pattern_segments[pattern_index], path_segments[path_index]) and
                visit(pattern_index + 1, path_index + 1))

    return visit(0, 0)


def _delivery_artifacts(
    selected: list[tuple[GuidanceUnit, GuidanceLoadingMode]],
    knowledge: KnowledgeBase,
    resolve_revision: Callable[[str], tuple[str, str]],
) -> tuple[DeliveryArtifact, ...]:
    output: list[DeliveryArtifact] = []
    path_to_indices: dict[str, list[int]] = {}
    for unit, mode in selected:
        if unit.path not in knowledge.documents:
            continue
        if mode == "whole":
            content = knowledge.documents[unit.path]
            contained = knowledge.contained_ids.get(unit.path, (unit.id,))
            composite_input = _whole_artifact_input(content, contained, resolve_revision)
        else:
            content = strip_metadata_comments(unit.content)
            contained = (unit.id,)
            composite_input = resolve_revision(unit.id)[1]
        existing = path_to_indices.setdefault(unit.path, [])
        whole_index = next((index for index in existing if output[index].loading_mode == "whole"), None)
        if whole_index is not None:
            artifact = output[whole_index]
            output[whole_index] = DeliveryArtifact(
                id=artifact.id,
                path=artifact.path,
                loading_mode="whole",
                applies=_merge_applies(artifact.applies, unit.applies),
                evidence_details_included=True,
                content=artifact.content,
                content_bytes=artifact.content_bytes,
                content_revision=artifact.content_revision,
                input_revision=_whole_artifact_input(
                    artifact.content,
                    tuple(dict.fromkeys((*artifact.contained_unit_ids, *contained))),
                    resolve_revision,
                ),
                contained_unit_ids=tuple(dict.fromkeys((*artifact.contained_unit_ids, *contained))),
            )
            continue
        if mode == "whole":
            if existing:
                first_index = existing[0]
                prior = output[first_index]
                contributing_ids = tuple(dict.fromkeys((*contained, *(i for index in existing
                                                                         for i in output[index].contained_unit_ids))))
                output[first_index] = DeliveryArtifact(
                    id=prior.id,
                    path=unit.path,
                    loading_mode="whole",
                    applies=_merge_applies(prior.applies, unit.applies),
                    evidence_details_included=True,
                    content=content,
                    content_bytes=len(content.encode("utf-8")),
                    content_revision=_sha256(content.encode("utf-8")),
                    input_revision=_whole_artifact_input(content, contributing_ids, resolve_revision),
                    contained_unit_ids=contributing_ids,
                )
                for index in existing[1:]:
                    output[index] = DeliveryArtifact(
                        id="", path="", loading_mode="unit", applies={},
                        evidence_details_included=False, content="", content_bytes=0,
                        content_revision="", input_revision="", contained_unit_ids=(),
                    )
                path_to_indices[unit.path] = [first_index]
                continue
        if mode == "unit" and any(output[index].id == unit.id for index in existing):
            continue
        content_revision, _ = resolve_revision(unit.id)
        output.append(
            DeliveryArtifact(
                id=unit.id,
                path=unit.path,
                loading_mode=mode,
                applies=unit.applies,
                evidence_details_included=mode == "whole",
                content=content,
                content_bytes=len(content.encode("utf-8")),
                content_revision=_sha256(content.encode("utf-8")) if mode == "whole" else content_revision,
                input_revision=composite_input,
                contained_unit_ids=tuple(dict.fromkeys(contained)),
            )
        )
        existing.append(len(output) - 1)
    return tuple(item for item in output if item.path)


def _merge_applies(
    left: dict[str, tuple[str, ...]], right: dict[str, tuple[str, ...]]
) -> dict[str, tuple[str, ...]]:
    return {
        field: tuple(dict.fromkeys((*left.get(field, ()), *right.get(field, ()))))
        for field in SCOPE_FIELDS
    }


def _evidence_summary(evidence: dict[str, object]) -> dict[str, object]:
    sources = evidence.get("sources", [])
    public_sources: list[dict[str, object]] = []
    if isinstance(sources, list):
        for source in sources:
            if not isinstance(source, dict):
                continue
            public_sources.append({
                key: source[key] for key in ("source", "revision", "uri") if key in source
            })
    return {"available": bool(evidence), "sources": public_sources}


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _whole_artifact_input(
    content: str,
    contained_ids: tuple[str, ...],
    resolve_revision: Callable[[str], tuple[str, str]],
) -> str:
    unit_ids = sorted(set(contained_ids))
    return _sha256(json.dumps({
        "content_revision": _sha256(content.encode("utf-8")),
        "units": [{"id": unit_id, "input_revision": resolve_revision(unit_id)[1]}
                  for unit_id in unit_ids],
    }, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _gap(issue: MetadataIssue) -> dict[str, str]:
    return {"code": issue.code, "path": issue.path, "message": issue.message}


def _deduplicate_issues(issues: list[MetadataIssue]) -> tuple[MetadataIssue, ...]:
    found: set[tuple[str, str, int, int, str]] = set()
    result: list[MetadataIssue] = []
    for issue in issues:
        key = (issue.code, issue.path, issue.line, issue.column, issue.message)
        if key not in found:
            found.add(key)
            result.append(issue)
    return tuple(result)
