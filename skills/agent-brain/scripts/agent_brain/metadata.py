"""Parse and validate agent-brain JSON comments in Markdown guidance."""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from typing import Any

from .records import GuidanceUnit, RequiredReference


SELECTOR_FIELDS = ("paths", "concepts", "actions", "dependencies", "providers", "runtimes")
ANNOTATION_RE = re.compile(r"<!--\s*agent-brain\b([\s\S]*?)-->")
OPEN_ANNOTATION_RE = re.compile(r"<!--\s*agent-brain\b")
FENCE_RE = re.compile(r"^[ \t]{0,3}(?P<marker>`{3,}|~{3,})(?P<info>[^\n]*)$")


@dataclass(frozen=True, slots=True)
class MetadataIssue:
    code: str
    path: str
    line: int
    column: int
    message: str


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _hide(text: list[str], start: int, end: int) -> None:
    for index in range(start, end):
        if text[index] not in "\r\n":
            text[index] = " "


def _mask_markdown_code(source: str) -> str:
    """Hide fenced and exact-run inline code while preserving source offsets."""
    masked = list(source)
    lines = source.splitlines(keepends=True)
    offsets: list[int] = []
    position = 0
    for line in lines:
        offsets.append(position)
        position += len(line)

    fence_marker: str | None = None
    fence_length = 0
    for offset, line in zip(offsets, lines):
        text = line.rstrip("\r\n")
        if fence_marker is None:
            match = FENCE_RE.fullmatch(text)
            if not match:
                continue
            marker = match.group("marker")
            info = match.group("info")
            if marker[0] == "`" and "`" in info:
                continue
            fence_marker = marker[0]
            fence_length = len(marker)
            _hide(masked, offset, offset + len(line))
            continue
        close = re.fullmatch(rf"[ \t]{{0,3}}{re.escape(fence_marker)}{{{fence_length},}}[ \t]*", text)
        _hide(masked, offset, offset + len(line))
        if close:
            fence_marker = None
            fence_length = 0

    # CommonMark treats four-space- or tab-indented lines as literal code.
    # Fenced lines already contain only spaces here, so masking them again is safe.
    for offset, line in zip(offsets, lines):
        if line.startswith("    ") or line.startswith("\t"):
            _hide(masked, offset, offset + len(line))

    visible = "".join(masked)
    cursor = 0
    while cursor < len(visible):
        if visible.startswith("<!--", cursor):
            comment_end = visible.find("-->", cursor + 4)
            if comment_end < 0:
                break
            cursor = comment_end + 3
            continue
        if visible[cursor] != "`":
            cursor += 1
            continue
        end = cursor + 1
        while end < len(visible) and visible[end] == "`":
            end += 1
        delimiter = visible[cursor:end]
        close = end
        while close < len(visible):
            close = visible.find(delimiter, close)
            if close < 0:
                break
            before = close > 0 and visible[close - 1] == "`"
            after = close + len(delimiter) < len(visible) and visible[close + len(delimiter)] == "`"
            if not before and not after:
                break
            close += len(delimiter)
        if close >= 0:
            _hide(masked, cursor, close + len(delimiter))
            visible = "".join(masked)
            cursor = close + len(delimiter)
        else:
            cursor = end
    return "".join(masked)


def _line_column(source: str, offset: int) -> tuple[int, int]:
    line = source.count("\n", 0, offset) + 1
    previous_newline = source.rfind("\n", 0, offset)
    return line, offset - previous_newline


def _canonical_uuid(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a UUID string")
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"{field} must be a UUID") from exc
    if str(parsed) != value.lower():
        raise ValueError(f"{field} must use canonical UUID formatting")
    return value.lower()


def _parse_fields(value: dict[str, Any], *, is_defaults: bool) -> dict[str, Any]:
    allowed = {"kind", "status", "applies", "requires", "evidence"}
    if not is_defaults:
        allowed.add("id")
    unknown = value.keys() - allowed
    if unknown:
        raise ValueError(f"annotation has unknown field {sorted(unknown)[0]!r}")
    if is_defaults and "id" in value:
        raise ValueError("defaults must not contain a unit id")
    result: dict[str, Any] = {}
    if "id" in value:
        result["id"] = _canonical_uuid(value["id"], "id")
    if "kind" in value:
        if value["kind"] not in ("policy", "fact"):
            raise ValueError("kind must be policy or fact")
        result["kind"] = value["kind"]
    if "status" in value:
        if value["status"] not in ("established", "candidate"):
            raise ValueError("status must be established or candidate")
        result["status"] = value["status"]
    if "applies" in value:
        applies = value["applies"]
        if not isinstance(applies, dict) or applies.keys() - set(SELECTOR_FIELDS):
            raise ValueError("applies must contain only supported selector lists")
        normalized: dict[str, tuple[str, ...]] = {}
        for field, raw in applies.items():
            if not isinstance(raw, list) or any(not isinstance(item, str) or not item.strip() for item in raw):
                raise ValueError(f"applies.{field} must be an array of non-empty strings")
            normalized[field] = tuple(raw)
        result["applies"] = normalized
    if "requires" in value:
        raw_requires = value["requires"]
        if not isinstance(raw_requires, list):
            raise ValueError("requires must be an array")
        requires: list[RequiredReference] = []
        seen_ids: set[str] = set()
        for index, raw_reference in enumerate(raw_requires):
            if not isinstance(raw_reference, dict) or raw_reference.keys() != {"id", "loading_mode"}:
                raise ValueError(f"requires[{index}] must contain id and loading_mode")
            reference_id = _canonical_uuid(raw_reference.get("id"), f"requires[{index}].id")
            loading_mode = raw_reference.get("loading_mode")
            if loading_mode not in ("unit", "whole"):
                raise ValueError(f"requires[{index}].loading_mode must be unit or whole")
            if reference_id in seen_ids:
                raise ValueError(f"requires contains duplicate reference {reference_id}")
            seen_ids.add(reference_id)
            requires.append(RequiredReference(reference_id, loading_mode))
        result["requires"] = tuple(requires)
    if "evidence" in value:
        evidence = value["evidence"]
        if not isinstance(evidence, dict):
            raise ValueError("evidence must be a JSON object")
        result["evidence"] = evidence
    return result


def _parse_entry(value: object, path: str, *, line: int, column: int) -> tuple[str, dict[str, Any] | None, MetadataIssue | None]:
    if not isinstance(value, dict):
        return "invalid", None, MetadataIssue("ABM001", path, line, column, "annotation must contain a JSON object")
    if type(value.get("schema_version")) is not int or value.get("schema_version") != 1:
        return "invalid", None, MetadataIssue("ABM001", path, line, column, "schema_version must be 1")
    try:
        if "defaults" in value:
            if value.keys() != {"schema_version", "defaults"}:
                raise ValueError("a defaults comment may contain only schema_version and defaults")
            raw_defaults = value["defaults"]
            if not isinstance(raw_defaults, dict):
                raise ValueError("defaults must be a JSON object")
            return "defaults", _parse_fields(raw_defaults, is_defaults=True), None
        if "id" not in value:
            raise ValueError("unit annotation must contain id")
        fields = _parse_fields({key: field for key, field in value.items() if key != "schema_version"},
                               is_defaults=False)
        return "unit", fields, None
    except ValueError as exc:
        return "invalid", None, MetadataIssue("ABM001", path, line, column, str(exc))


def _frontmatter_body_start(source: str) -> int:
    lines = source.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return 0
    offset = len(lines[0])
    for line in lines[1:]:
        if line.rstrip("\r\n") == "---":
            return offset + len(line)
        offset += len(line)
    return 0


def _comment_matches(source: str, masked: str) -> list[re.Match[str]]:
    return list(ANNOTATION_RE.finditer(masked))


def _heading_records(masked: str, source: str, body_start: int) -> list[tuple[int, int, int, str]]:
    heading_view = list(masked)
    for comment in re.finditer(r"<!--[\s\S]*?-->", masked):
        _hide(heading_view, comment.start(), comment.end())
    _hide(heading_view, 0, body_start)
    view = "".join(heading_view)
    result: list[tuple[int, int, int, str]] = []
    pattern = re.compile(r"(?m)^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
    for match in pattern.finditer(view):
        line_end = source.find("\n", match.end())
        if line_end < 0:
            line_end = len(source)
        else:
            line_end += 1
        title = re.sub(r"[ \t]+#+[ \t]*$", "", match.group(2)).strip()
        result.append((match.start(), line_end, len(match.group(1)), title))
    return result


def strip_metadata_comments(source: str) -> str:
    """Remove active namespaced metadata comments from unit-sized delivery."""
    masked = _mask_markdown_code(source)
    output = list(source)
    for match in ANNOTATION_RE.finditer(masked):
        _hide(output, match.start(), match.end())
    return "".join(output)


def extract_section_content(path: str, source: str, title: str) -> tuple[str | None, MetadataIssue | None]:
    """Resolve one externally mapped heading without changing its source file."""
    masked = _mask_markdown_code(source)
    headings = _heading_records(masked, source, _frontmatter_body_start(source))
    matches = [index for index, record in enumerate(headings) if record[3] == title]
    if len(matches) != 1:
        detail = "not found" if not matches else "ambiguous"
        return None, MetadataIssue("ABM005", path, 1, 1,
                                   f"mapped section heading {title!r} is {detail}")
    heading_index = matches[0]
    start, _, level, _ = headings[heading_index]
    end = next((candidate[0] for candidate in headings[heading_index + 1:]
                if candidate[2] <= level), len(source))
    return strip_metadata_comments(source[start:end]), None


def parse_document_metadata(path: str, source: str) -> tuple[tuple[GuidanceUnit, ...], tuple[MetadataIssue, ...]]:
    """Return active document/section annotations and findings for one Markdown file."""
    masked = _mask_markdown_code(source)
    body_start = _frontmatter_body_start(source)
    issues: list[MetadataIssue] = []
    entries: list[tuple[re.Match[str], str, dict[str, Any] | None]] = []
    for match in _comment_matches(source, masked):
        if match.start() < body_start:
            continue
        line, column = _line_column(source, match.start())
        raw = ANNOTATION_RE.fullmatch(source[match.start():match.end()])
        assert raw is not None
        try:
            value = json.loads(raw.group(1).strip(), object_pairs_hook=_unique_object)
        except (json.JSONDecodeError, ValueError) as exc:
            issues.append(MetadataIssue("ABM001", path, line, column, f"invalid agent-brain JSON: {exc}"))
            entries.append((match, "invalid", None))
            continue
        entry_kind, fields, issue = _parse_entry(value, path, line=line, column=column)
        if issue is not None:
            issues.append(issue)
        entries.append((match, entry_kind, fields))

    matched_starts = {match.start() for match, _, _ in entries}
    for unmatched in OPEN_ANNOTATION_RE.finditer(masked):
        if unmatched.start() < body_start or unmatched.start() in matched_starts:
            continue
        line, column = _line_column(source, unmatched.start())
        issues.append(MetadataIssue("ABM001", path, line, column, "unterminated agent-brain comment"))

    defaults_entries = [(match, fields) for match, kind, fields in entries
                        if kind == "defaults" and fields is not None]
    defaults: dict[str, Any] = {}
    if len(defaults_entries) > 1:
        match, _ = defaults_entries[1]
        line, column = _line_column(source, match.start())
        issues.append(MetadataIssue("ABM005", path, line, column, "only one defaults comment is allowed per document"))
    if defaults_entries:
        match, defaults = defaults_entries[0]
        comment_masked = list(masked)
        for annotation, _, _ in entries:
            _hide(comment_masked, annotation.start(), annotation.end())
        prefix = "".join(comment_masked[body_start:match.start()])
        earlier_units = any(kind == "unit" and annotation.start() < match.start()
                            for annotation, kind, _ in entries)
        if prefix.strip() or earlier_units:
            line, column = _line_column(source, match.start())
            issues.append(MetadataIssue("ABM005", path, line, column,
                                        "defaults must appear after frontmatter and before guidance content"))

    headings = _heading_records(masked, source, body_start)
    valid_units: list[tuple[re.Match[str], dict[str, Any], tuple[int, int, int, str] | None]] = []
    document_count = 0
    for match, entry_kind, fields in entries:
        if entry_kind != "unit" or fields is None:
            continue
        line, column = _line_column(source, match.start())
        heading = next((record for record in reversed(headings)
                        if record[1] <= match.start() and not masked[record[1]:match.start()].strip()), None)
        if heading is None:
            heading_view = list(masked)
            for comment in re.finditer(r"<!--[\s\S]*?-->", masked):
                _hide(heading_view, comment.start(), comment.end())
            _hide(heading_view, 0, body_start)
            if "".join(heading_view[body_start:match.start()]).strip():
                issues.append(MetadataIssue("ABM005", path, line, column,
                                            "unit comment must follow frontmatter or immediately follow a heading"))
                continue
            document_count += 1
            if document_count > 1:
                issues.append(MetadataIssue("ABM005", path, line, column,
                                            "only one document unit is allowed per artifact"))
                continue

        merged = dict(defaults)
        merged.update(fields)
        if "applies" in defaults and "applies" in fields:
            inherited_applies = dict(defaults["applies"])
            inherited_applies.update(fields["applies"])
            merged["applies"] = inherited_applies
        if "kind" not in merged or "status" not in merged:
            issues.append(MetadataIssue("ABM001", path, line, column,
                                        "unit must define kind and status directly or through defaults"))
            continue
        applies = {name: tuple(merged.get("applies", {}).get(name, ())) for name in SELECTOR_FIELDS}
        valid_units.append((match, {
            "id": fields["id"],
            "kind": merged["kind"],
            "status": merged["status"],
            "applies": applies,
            "requires": tuple(merged.get("requires", ())),
            "evidence": merged.get("evidence", {}),
        }, heading))

    heading_indexes = {record[0]: index for index, record in enumerate(headings)}
    units: list[GuidanceUnit] = []
    for match, fields, heading in valid_units:
        if heading is None:
            content = strip_metadata_comments(source)
            selector = "document"
            title = None
        else:
            start, _, level, title = heading
            heading_index = heading_indexes[start]
            end = next((candidate[0] for candidate in headings[heading_index + 1:]
                        if candidate[2] <= level), len(source))
            excluded: list[tuple[int, int]] = []
            for _, _, other_heading in valid_units:
                if other_heading is None:
                    continue
                other_start, _, other_level, _ = other_heading
                if other_level <= level or not (start < other_start < end):
                    continue
                other_index = heading_indexes[other_start]
                other_end = next((candidate[0] for candidate in headings[other_index + 1:]
                                  if candidate[2] <= other_level), len(source))
                excluded.append((other_start, min(other_end, end)))
            merged_excluded: list[tuple[int, int]] = []
            for range_start, range_end in sorted(excluded):
                if merged_excluded and range_start <= merged_excluded[-1][1]:
                    previous_start, previous_end = merged_excluded[-1]
                    merged_excluded[-1] = (previous_start, max(previous_end, range_end))
                else:
                    merged_excluded.append((range_start, range_end))
            pieces: list[str] = []
            cursor = start
            for range_start, range_end in merged_excluded:
                pieces.append(source[cursor:range_start])
                cursor = range_end
            pieces.append(source[cursor:end])
            content = strip_metadata_comments("".join(pieces))
            selector = "section"
        units.append(GuidanceUnit(
            id=fields["id"], path=path, selector=selector, heading=title,
            kind=fields["kind"], status=fields["status"], applies=fields["applies"],
            requires=fields["requires"], evidence=fields["evidence"],
            content=content, source="annotation",
        ))
    return tuple(units), tuple(issues)
