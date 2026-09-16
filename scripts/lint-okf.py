#!/usr/bin/env python3

"""Validate canonical agent documents against the repository OKF profile."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PureWindowsPath
from typing import Any, Iterable
from urllib.parse import unquote, urlsplit


VENDOR_DIR = Path(__file__).resolve().parent / "vendor"
VENDOR_PACKAGE = VENDOR_DIR / "yaml"
sys.path.insert(0, str(VENDOR_DIR))

try:
    import yaml
except Exception as error:  # pragma: no cover - depends on a broken vendor tree
    YAML_ERROR = str(error)
    yaml = None
else:
    try:
        Path(yaml.__file__).resolve().relative_to(VENDOR_PACKAGE.resolve())
    except (AttributeError, TypeError, ValueError) as error:
        YAML_ERROR = f"PyYAML was not loaded from {VENDOR_PACKAGE}: {error}"
    else:
        version = getattr(yaml, "__version__", None)
        YAML_ERROR = None if version == "6.0.3" else f"expected PyYAML 6.0.3, found {version!r}"


@dataclass(frozen=True)
class Diagnostic:
    id: str
    path: str
    line: int
    column: int
    message: str

    def as_json(self) -> dict[str, object]:
        return {
            "id": self.id,
            "path": self.path,
            "line": self.line,
            "column": self.column,
            "message": self.message,
        }


if YAML_ERROR is None:
    class NoTimestampSafeLoader(yaml.SafeLoader):
        yaml_implicit_resolvers = copy.deepcopy(yaml.SafeLoader.yaml_implicit_resolvers)

    for initial, resolvers in NoTimestampSafeLoader.yaml_implicit_resolvers.items():
        NoTimestampSafeLoader.yaml_implicit_resolvers[initial] = [
            resolver for resolver in resolvers if resolver[0] != "tag:yaml.org,2002:timestamp"
        ]


COMMENT_RE = re.compile(r"<!--")
FENCE_OPEN_RE = re.compile(r"(?m)^[ \t]{0,3}(?:(`{3,})[^`\n]*|(~{3,})[^\n]*)$")

LocationPath = tuple[str | int, ...]


def diagnostic(identifier: str, path: str, line: int, column: int, message: str) -> Diagnostic:
    return Diagnostic(identifier, path, line, column, message)


def relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def find_root(start: Path) -> Path | None:
    for directory in (start, *start.parents):
        agents = directory / ".agents"
        if (agents / "instructions").is_dir() and (agents / "memory").is_dir():
            return directory
    return None


def key_locations(frontmatter: str) -> dict[LocationPath, tuple[int, int]]:
    locations: dict[LocationPath, tuple[int, int]] = {}
    if yaml is None:
        return locations
    try:
        node = yaml.compose(frontmatter, Loader=NoTimestampSafeLoader)
    except yaml.YAMLError:
        return locations
    def visit(current: Any, prefix: LocationPath) -> None:
        if isinstance(current, yaml.MappingNode):
            for key, value in current.value:
                if not isinstance(key, yaml.ScalarNode):
                    continue
                child = prefix + (str(key.value),)
                locations[child] = (key.start_mark.line + 2, key.start_mark.column + 1)
                visit(value, child)
        elif isinstance(current, yaml.SequenceNode):
            for index, item in enumerate(current.value):
                child = prefix + (index,)
                locations[child] = (item.start_mark.line + 2, item.start_mark.column + 1)
                visit(item, child)

    visit(node, ())
    return locations


def key_position(locations: dict[LocationPath, tuple[int, int]], *parts: str | int) -> tuple[int, int]:
    return locations.get(parts, (1, 1))


def expected_type(path: str) -> str:
    if path.startswith(".agents/instructions/"):
        return "Agent Instruction"
    memory_path = path.removeprefix(".agents/memory/")
    if memory_path == "INDEX.md":
        return "Knowledge Index"
    if memory_path == "LOG.md":
        return "Source Ingestion Log"
    if memory_path == "KNOWN_ISSUES.md" or memory_path.startswith("known-issues/"):
        return "Known Issue"
    if memory_path == "TESTING_STRATEGY.md" or memory_path.startswith("testing/"):
        return "Testing Guidance"
    if memory_path.startswith("adrs/"):
        return "Architecture Decision"
    if memory_path.startswith("sources/") and memory_path.endswith(".summary.md"):
        return "Source Summary"
    return "Agent Memory"


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def has_explicit_offset(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        return datetime.fromisoformat(normalized).tzinfo is not None
    except ValueError:
        return False


def add_metadata_diagnostics(
    findings: list[Diagnostic], path: str, data: dict[str, Any], locations: dict[LocationPath, tuple[int, int]]
) -> None:
    for name in ("type", "description"):
        if not is_nonempty_string(data.get(name)):
            line, column = key_position(locations, name)
            findings.append(diagnostic("OKF004", path, line, column, f"{name} must be a non-empty string"))

    for name in ("title", "resource"):
        if name in data and not is_nonempty_string(data[name]):
            line, column = key_position(locations, name)
            findings.append(diagnostic("OKF005", path, line, column, f"{name} must be a non-empty string"))

    if "tags" in data and (
        not isinstance(data["tags"], list) or not all(is_nonempty_string(item) for item in data["tags"])
    ):
        line, column = key_position(locations, "tags")
        findings.append(diagnostic("OKF005", path, line, column, "tags must be a list of non-empty strings"))

    if "status" in data:
        line, column = key_position(locations, "status")
        if isinstance(data["status"], str) and data["status"] in {"stable", "scaffold", "verified"}:
            findings.append(diagnostic("OKF105", path, line, column, "legacy status representation is not allowed"))
        elif not isinstance(data["status"], str) or data["status"] not in {"draft", "deprecated"}:
            findings.append(diagnostic("OKF005", path, line, column, "status must be draft or deprecated"))
    if "coverage" in data:
        line, column = key_position(locations, "coverage")
        findings.append(diagnostic("OKF105", path, line, column, "legacy coverage field is not allowed"))

    validate_window(findings, path, "usage_window", data.get("usage_window"), locations)
    validate_timestamp(findings, path, "stale_after", data.get("stale_after"), locations)
    validate_generated(findings, path, data.get("generated"), locations)
    validate_verified(findings, path, data.get("verified"), locations)
    validate_sources(findings, path, data.get("sources"), locations)


def validate_timestamp(
    findings: list[Diagnostic], path: str, name: str, value: Any, locations: dict[LocationPath, tuple[int, int]], prefix: LocationPath = ()
) -> None:
    if value is not None and not has_explicit_offset(value):
        line, column = key_position(locations, *prefix, name)
        findings.append(diagnostic("OKF006" if isinstance(value, str) else "OKF005", path, line, column, f"{name} must be an explicit-offset ISO 8601 datetime"))


def validate_window(
    findings: list[Diagnostic], path: str, name: str, value: Any, locations: dict[LocationPath, tuple[int, int]], prefix: LocationPath = ()
) -> None:
    if value is None:
        return
    full_path = prefix + (name,)
    if not isinstance(value, dict):
        line, column = key_position(locations, *full_path)
        findings.append(diagnostic("OKF005", path, line, column, f"{name} must contain explicit-offset from and to datetimes"))
        return
    for endpoint in ("from", "to"):
        if endpoint not in value:
            findings.append(diagnostic("OKF005", path, 1, 1, f"{name} requires {endpoint}"))
        elif not has_explicit_offset(value[endpoint]):
            line, column = key_position(locations, *full_path, endpoint)
            findings.append(diagnostic("OKF006" if isinstance(value[endpoint], str) else "OKF005", path, line, column, f"{name}.{endpoint} must be an explicit-offset ISO 8601 datetime"))


def validate_generated(
    findings: list[Diagnostic], path: str, value: Any, locations: dict[LocationPath, tuple[int, int]]) -> None:
    if value is None:
        return
    line, column = key_position(locations, "generated")
    if not isinstance(value, dict):
        findings.append(diagnostic("OKF005", path, line, column, "generated must contain non-empty by and at fields"))
        return
    if "by" not in value:
        findings.append(diagnostic("OKF005", path, 1, 1, "generated requires by"))
    elif not is_nonempty_string(value["by"]):
        line, column = key_position(locations, "generated", "by")
        findings.append(diagnostic("OKF005", path, line, column, "generated.by must be a non-empty string"))
    if "at" not in value:
        findings.append(diagnostic("OKF005", path, 1, 1, "generated requires at"))
    elif not has_explicit_offset(value["at"]):
        line, column = key_position(locations, "generated", "at")
        findings.append(diagnostic("OKF006" if isinstance(value["at"], str) else "OKF005", path, line, column, "generated.at must be an explicit-offset ISO 8601 datetime"))


def validate_verified(
    findings: list[Diagnostic], path: str, value: Any, locations: dict[LocationPath, tuple[int, int]]) -> None:
    if value is None:
        return
    line, column = key_position(locations, "verified")
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        findings.append(diagnostic("OKF005", path, line, column, "verified must be a list of mappings"))
        return
    for index, item in enumerate(value):
        if "by" not in item:
            findings.append(diagnostic("OKF005", path, 1, 1, "verified entries require by"))
        elif not is_nonempty_string(item["by"]):
            item_line, item_column = key_position(locations, "verified", index, "by")
            findings.append(diagnostic("OKF005", path, item_line, item_column, "verified.by must be a non-empty string"))
        if "at" not in item:
            findings.append(diagnostic("OKF005", path, 1, 1, "verified entries require at"))
        elif not has_explicit_offset(item["at"]):
            item_line, item_column = key_position(locations, "verified", index, "at")
            findings.append(diagnostic("OKF006" if isinstance(item["at"], str) else "OKF005", path, item_line, item_column, "verified.at must be an explicit-offset ISO 8601 datetime"))


def validate_sources(
    findings: list[Diagnostic], path: str, value: Any, locations: dict[LocationPath, tuple[int, int]]) -> None:
    if value is None:
        return
    line, column = key_position(locations, "sources")
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        findings.append(diagnostic("OKF005", path, line, column, "sources must be a list of mappings"))
        return
    for index, item in enumerate(value):
        if not is_nonempty_string(item.get("resource")):
            item_line, item_column = key_position(locations, "sources", index, "resource")
            findings.append(diagnostic("OKF005", path, item_line, item_column, "source resource must be a non-empty string"))
        for name in ("id", "title", "author"):
            if name in item and not is_nonempty_string(item[name]):
                item_line, item_column = key_position(locations, "sources", index, name)
                findings.append(diagnostic("OKF005", path, item_line, item_column, f"source {name} must be a non-empty string"))
        if "usage_count" in item and (type(item["usage_count"]) is not int or item["usage_count"] < 0):
            item_line, item_column = key_position(locations, "sources", index, "usage_count")
            findings.append(diagnostic("OKF005", path, item_line, item_column, "source usage_count must be a non-negative integer"))
        if "last_modified" in item and not has_explicit_offset(item["last_modified"]):
            item_line, item_column = key_position(locations, "sources", index, "last_modified")
            findings.append(diagnostic("OKF006" if isinstance(item["last_modified"], str) else "OKF005", path, item_line, item_column, "source last_modified must be an explicit-offset ISO 8601 datetime"))
        if "usage_window" in item:
            validate_window(findings, path, "usage_window", item["usage_window"], locations, ("sources", index))


def ignored_ranges(body: str) -> list[bool]:
    ignored = [False] * len(body)

    def mask(start: int, end: int) -> None:
        for index in range(start, end):
            ignored[index] = True

    for match in COMMENT_RE.finditer(body):
        closing = body.find("-->", match.end())
        mask(match.start(), len(body) if closing == -1 else closing + 3)
    for match in FENCE_OPEN_RE.finditer(body):
        if ignored[match.start()]:
            continue
        marker = match.group(1) or match.group(2)
        close_re = re.compile(rf"(?m)^[ \t]{{0,3}}{re.escape(marker[0])}{{{len(marker)},}}[ \t]*$")
        closing = close_re.search(body, match.end())
        if closing is not None:
            mask(match.start(), closing.end())
        else:
            mask(match.start(), len(body))

    index = 0
    while index < len(body):
        if body[index] != "`" or ignored[index]:
            index += 1
            continue
        end = index
        while end < len(body) and body[end] == "`":
            end += 1
        marker = body[index:end]
        search = end
        closing = None
        while search < len(body):
            candidate = body.find(marker, search)
            if candidate == -1:
                break
            candidate_end = candidate + len(marker)
            is_exact_run = (
                (candidate == 0 or body[candidate - 1] != "`")
                and (candidate_end == len(body) or body[candidate_end] != "`")
            )
            if is_exact_run and not any(ignored[candidate:candidate_end]):
                closing = candidate
                break
            search = candidate + 1
        if closing is None:
            index = end
            continue
        mask(index, closing + len(marker))
        index = closing + len(marker)
    return ignored


def masked_body(body: str) -> str:
    ignored = ignored_ranges(body)
    return "".join("\n" if character == "\n" else (" " if ignored[index] else character) for index, character in enumerate(body))


def unescape_markdown_destination(value: str) -> str:
    return re.sub(r"\\([\\()<>])", r"\1", value)


def is_windows_absolute(value: str) -> bool:
    return PureWindowsPath(value).is_absolute()


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


def inline_destinations(text: str) -> Iterable[tuple[str, int]]:
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


def reference_destinations(text: str) -> Iterable[tuple[str, int]]:
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


def destination_diagnostics(root: Path, document: Path, source: str, start: int, path: str) -> list[Diagnostic]:
    raw_source = source
    source = unescape_markdown_destination(source)
    if source.startswith("/") or is_windows_absolute(raw_source) or is_windows_absolute(source):
        return [diagnostic("OKF102", path, 1, 1, "local target must not be absolute")]
    parsed = urlsplit(source)
    if parsed.scheme:
        return []
    if not parsed.path:
        return []
    candidate = (document.parent / unquote(parsed.path)).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return [diagnostic("OKF102", path, 1, 1, "local target escapes repository root")]
    if not candidate.is_file():
        return [diagnostic("OKF103", path, 1, 1, "local target does not resolve to a regular file")]
    return []


def link_diagnostics(root: Path, document: Path, body: str, path: str, body_start_line: int) -> list[Diagnostic]:
    findings: list[Diagnostic] = []
    masked = masked_body(body)
    for destination, index in (*inline_destinations(masked), *reference_destinations(masked)):
        line = body_start_line + masked.count("\n", 0, index)
        column = index - masked.rfind("\n", 0, index)
        for item in destination_diagnostics(root, document, destination, index, path):
            findings.append(Diagnostic(item.id, item.path, line, column, item.message))
    return findings


def frontmatter_resource_diagnostics(root: Path, document: Path, path: str, data: dict[str, Any], locations: dict[LocationPath, tuple[int, int]]) -> list[Diagnostic]:
    findings: list[Diagnostic] = []
    resources: list[tuple[LocationPath, str]] = []
    if is_nonempty_string(data.get("resource")):
        resources.append((("resource",), data["resource"]))
    if isinstance(data.get("sources"), list):
        resources.extend((("sources", index, "resource"), item["resource"]) for index, item in enumerate(data["sources"]) if isinstance(item, dict) and is_nonempty_string(item.get("resource")))
    for resource_path, source in resources:
        line, column = key_position(locations, *resource_path)
        findings.extend(Diagnostic(item.id, item.path, line, column, item.message) for item in destination_diagnostics(root, document, source, 0, path))
    return findings


def manifest_diagnostics(root: Path, concepts: list[tuple[Path, str, dict[str, Any], dict[str, tuple[int, int]]]]) -> list[Diagnostic]:
    summaries = [item for item in concepts if expected_type(item[1]) == "Source Summary"]
    if not summaries:
        return []
    manifest_path = root / ".agents/memory/sources/source-ingest-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = manifest["entries"]
        if not isinstance(entries, list):
            raise ValueError("entries is not a list")
    except Exception as error:
        return [diagnostic("OKF900", relative(root, manifest_path), 1, 1, f"cannot load source-ingest manifest: {error}")]
    findings: list[Diagnostic] = []
    source_root = root / ".agents/sources"
    for document, path, data, _ in summaries:
        summary_path = document.relative_to(root / ".agents/memory/sources").as_posix()
        matching = [entry for entry in entries if isinstance(entry, dict) and entry.get("summary_path") == summary_path]
        source_entries = data.get("sources")
        valid = len(matching) == 1 and isinstance(source_entries, list) and len(source_entries) == 1
        if valid:
            expected = (source_root / str(matching[0].get("source_path", ""))).resolve()
            resource = source_entries[0].get("resource") if isinstance(source_entries[0], dict) else None
            actual = (document.parent / unquote(urlsplit(resource).path)).resolve() if is_nonempty_string(resource) else None
            valid = actual == expected
        if not valid:
            findings.append(diagnostic("OKF104", path, 1, 1, "source summary must bind exactly to its manifest source"))
    return findings


def lint(root: Path) -> list[Diagnostic]:
    findings: list[Diagnostic] = []
    concepts: list[tuple[Path, str, dict[str, Any], dict[str, tuple[int, int]]]] = []
    for bundle in (root / ".agents/instructions", root / ".agents/memory"):
        for document in sorted(bundle.rglob("*.md")):
            path = relative(root, document)
            if document.name in {"index.md", "log.md"}:
                findings.append(diagnostic("OKF007", path, 1, 1, "lowercase index.md and log.md paths are reserved"))
                continue
            try:
                text = document.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                findings.append(diagnostic("OKF001", path, 1, 1, "concept must be readable UTF-8"))
                continue
            lines = text.splitlines(keepends=True)
            if not lines or lines[0].rstrip("\r\n") != "---":
                findings.append(diagnostic("OKF002", path, 1, 1, "frontmatter must begin with an exact --- delimiter"))
                continue
            closing = next((index for index, line in enumerate(lines[1:], 1) if line.rstrip("\r\n") == "---"), None)
            if closing is None:
                findings.append(diagnostic("OKF002", path, 1, 1, "frontmatter must end with an exact --- delimiter"))
                continue
            frontmatter = "".join(lines[1:closing])
            try:
                data = yaml.load(frontmatter, Loader=NoTimestampSafeLoader)
            except yaml.YAMLError as error:
                mark = getattr(error, "problem_mark", None)
                line = mark.line + 2 if mark else 1
                column = mark.column + 1 if mark else 1
                findings.append(diagnostic("OKF003", path, line, column, "frontmatter is not valid YAML"))
                continue
            if not isinstance(data, dict):
                findings.append(diagnostic("OKF003", path, 1, 1, "frontmatter must be a mapping"))
                continue
            locations = key_locations(frontmatter)
            add_metadata_diagnostics(findings, path, data, locations)
            if is_nonempty_string(data.get("type")) and data["type"] != expected_type(path):
                line, column = key_position(locations, "type")
                findings.append(diagnostic("OKF101", path, line, column, f"type must be {expected_type(path)} for this path"))
            body = "".join(lines[closing + 1:])
            findings.extend(link_diagnostics(root, document, body, path, closing + 2))
            findings.extend(frontmatter_resource_diagnostics(root, document, path, data, locations))
            concepts.append((document, path, data, locations))
    findings.extend(manifest_diagnostics(root, concepts))
    return sorted(findings, key=lambda item: (item.path, item.line, item.column, item.id))


def render(findings: Iterable[Diagnostic], output_format: str) -> None:
    diagnostics = list(findings)
    if output_format == "json":
        print(json.dumps({"schema_version": 1, "diagnostics": [item.as_json() for item in diagnostics]}, separators=(",", ":")))
    else:
        for item in diagnostics:
            print(f"{item.path}:{item.line}:{item.column}: {item.id} {item.message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("human", "json"), default="human")
    arguments = parser.parse_args()
    if YAML_ERROR is not None:
        findings = [diagnostic("OKF900", ".", 1, 1, f"unable to load vendored PyYAML: {YAML_ERROR}")]
        render(findings, arguments.format)
        return 2
    root = find_root(Path.cwd().resolve())
    if root is None:
        findings = [diagnostic("OKF900", ".", 1, 1, "cannot find repository with both canonical document bundles")]
        render(findings, arguments.format)
        return 2
    try:
        findings = lint(root)
    except Exception as error:  # pragma: no cover - defensive public CLI boundary
        findings = [diagnostic("OKF900", ".", 1, 1, f"internal linter error: {error}")]
    render(findings, arguments.format)
    return 2 if any(item.id == "OKF900" for item in findings) else (1 if findings else 0)


if __name__ == "__main__":
    raise SystemExit(main())
