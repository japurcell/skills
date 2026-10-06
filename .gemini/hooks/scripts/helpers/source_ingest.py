#!/usr/bin/env python3
# Generated from hooks/families/auto_ingest.py by scripts/generate-hooks.py. Do not edit.
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote


MANIFEST_FILE_NAME = "source-ingest-manifest.json"
SUMMARY_SUFFIX = ".summary.md"
DRAFT_SUMMARY_TYPE = "Source Summary"
DRAFT_SUMMARY_STATUS = "draft"
PENDING_INGEST_DIRECTIVE = "Pending ingest blocks normal work."
PENDING_INGEST_SKILL_PROMPT = "Activate or load the `ingest-source` skill, then run `/ingest-source`."
PENDING_INGEST_SKILL_MISSING = "The `ingest-source` skill is unavailable."


@dataclass(frozen=True)
class SourceRecord:
    source_path: str
    content_hash: str
    size: int
    summary_path: str
    summary_exists: bool
    summary_hash: str
    summary_is_scaffold: bool



def source_root_for_payload(payload: dict[str, object]) -> Path:
    override = os.environ.get("AGENTS_SOURCE_SCAN_DIR")
    if override:
        return Path(override)
    cwd = str(payload.get("cwd") or "")
    if cwd:
        from helpers.common import convert_windows_path_to_posix
        cwd = convert_windows_path_to_posix(cwd)
    return Path(cwd) / ".agents/sources" if cwd else Path.cwd() / ".agents/sources"


def summary_root_for_payload(payload: dict[str, object]) -> Path:
    override = os.environ.get("AGENTS_SOURCE_SUMMARY_DIR")
    if override:
        return Path(override)
    cwd = str(payload.get("cwd") or "")
    if cwd:
        from helpers.common import convert_windows_path_to_posix
        cwd = convert_windows_path_to_posix(cwd)
    return Path(cwd) / ".agents/memory/sources" if cwd else Path.cwd() / ".agents/memory/sources"


def manifest_path_for_summary_root(summary_dir: Path) -> Path:
    return summary_dir / MANIFEST_FILE_NAME


def manifest_path_for_payload(payload: dict[str, object], summary_root: Path) -> Path:
    override = os.environ.get("AGENTS_SOURCE_MANIFEST_PATH")
    if override:
        return Path(override)
    return manifest_path_for_summary_root(summary_root)


def repo_root_for_payload(payload: dict[str, object]) -> Path:
    cwd = str(payload.get("cwd") or "")
    if cwd:
        from helpers.common import convert_windows_path_to_posix
        cwd = convert_windows_path_to_posix(cwd)
    return Path(cwd) if cwd else Path.cwd()


def ingest_skill_path(repo_root: Path) -> Path:
    override = os.environ.get("AGENTS_SKILLS_DIR") or os.environ.get("GEMINI_SKILLS_DIR")
    if override:
        return Path(override) / "ingest-source" / "SKILL.md"
    return repo_root / ".agents" / "skills" / "ingest-source" / "SKILL.md"


def ingest_skill_available(repo_root: Path) -> bool:
    skill_path = ingest_skill_path(repo_root)
    return skill_path.is_file() and os.access(skill_path, os.R_OK)


def summary_name_for_source(relpath: str) -> str:
    encoded = "__".join(part.replace(".", "-") for part in Path(relpath).parts)
    return f"{encoded}{SUMMARY_SUFFIX}"


def summary_path_for_source(summary_dir: Path, relpath: str) -> Path:
    return summary_dir / summary_name_for_source(relpath)


def default_manifest() -> dict[str, Any]:
    return {"version": 1, "entries": []}


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _read_file_hash(path: Path) -> str:
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
    except OSError:
        return ""
    return hasher.hexdigest()


def _parse_frontmatter_scalar(raw_value: str) -> str | None:
    value = raw_value.strip()
    in_single_quote = False
    in_double_quote = False
    escaped = False
    for index, character in enumerate(value):
        if escaped:
            escaped = False
        elif character == "\\" and in_double_quote:
            escaped = True
        elif character == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
        elif character == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif character == "#" and not in_single_quote and not in_double_quote:
            if index == 0 or value[index - 1].isspace():
                value = value[:index].rstrip()
                break

    if not value:
        return None
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return None
        return parsed if isinstance(parsed, str) else None
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            return None
        return value[1:-1].replace("''", "'")
    return value


def _is_scaffold_summary(text: str) -> bool:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return False

    frontmatter: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return (
                frontmatter.get("type") == DRAFT_SUMMARY_TYPE
                and frontmatter.get("status") == DRAFT_SUMMARY_STATUS
            )
        if line[:1].isspace() or ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        if (key := key.rstrip()) in {"type", "status"}:
            value = _parse_frontmatter_scalar(raw_value)
            if value is not None:
                frontmatter[key] = value
    return False


def _summary_details(path: Path) -> tuple[bool, str, bool]:
    if not path.exists() or not path.is_file() or path.is_symlink():
        return False, "", False

    content = path.read_bytes()
    text = content.decode("utf-8", errors="replace")
    return True, _sha256_bytes(content), _is_scaffold_summary(text)


def _is_hidden_relative(relpath: Path) -> bool:
    return any(part.startswith(".") for part in relpath.parts)


def blocking_entries(report_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [entry for entry in report_entries if _entry_state(entry) in {"needs_summary", "stale"}]


def _pending_entry_label(entry: dict[str, Any]) -> str:
    summary_name = _entry_summary_path(entry, "")
    return f"- `.agents/sources/{entry['source_path']}` → `.agents/memory/sources/{summary_name}` ({_entry_reason(entry)})"


def _recovery_checklist() -> list[str]:
    return [
        "## Recovery checklist",
        "- Restore `.agents/skills/ingest-source/SKILL.md`.",
        "- Re-run the turn after the skill is available.",
    ]


def _build_orphan_context(orphan_entries: list[dict[str, Any]]) -> list[str]:
    if not orphan_entries:
        return []

    lines = [
        "Do not invoke `ingest-source` for deleted sources; clean up orphan summaries manually.",
        "",
        "## Orphan summaries requiring cleanup",
    ]
    for entry in orphan_entries:
        summary_name = _entry_summary_path(entry, "")
        lines.append(f"- `.agents/sources/{entry['source_path']}`")
        lines.append(f"  - stale reason: {_entry_reason(entry)}")
        lines.append(f"  - orphan summary: `.agents/memory/sources/{summary_name}`")
        related_source = str(entry.get("related_source") or "")
        if related_source:
            lines.append(f"  - replacement source path: `.agents/sources/{related_source}`")
    return lines


def build_block_reason(report_entries: list[dict[str, Any]], skill_available: bool) -> str:
    blocking = blocking_entries(report_entries)
    if not blocking:
        return ""

    pending = "; ".join(f"`{entry['source_path']}` ({_entry_reason(entry)})" for entry in blocking)
    if skill_available:
        return f"{PENDING_INGEST_DIRECTIVE} Load `/ingest-source` for {pending}."

    return f"{PENDING_INGEST_DIRECTIVE} {PENDING_INGEST_SKILL_MISSING} Pending: {pending}."


def scan_sources(source_root: Path, summary_root: Path) -> list[SourceRecord]:
    if not source_root.exists():
        return []

    records: list[SourceRecord] = []
    for source_path in sorted(source_root.rglob("*")):
        if not source_path.is_file() or source_path.is_symlink():
            continue

        relpath = source_path.relative_to(source_root)
        if _is_hidden_relative(relpath):
            continue

        source_relpath = relpath.as_posix()
        summary_path = summary_path_for_source(summary_root, source_relpath)
        summary_exists, summary_hash, summary_is_scaffold = _summary_details(summary_path)
        records.append(
            SourceRecord(
                source_path=source_relpath,
                content_hash=_read_file_hash(source_path),
                size=source_path.stat().st_size,
                summary_path=summary_path.name,
                summary_exists=summary_exists,
                summary_hash=summary_hash,
                summary_is_scaffold=summary_is_scaffold,
            )
        )

    return records


def load_manifest(path: Path, *, expected: bool = False) -> dict[str, Any]:
    if not path.exists():
        if expected or path.with_suffix(".expected").exists():
            raise ValueError("Expected source-ingest manifest is unavailable; restore it before proceeding.")
        return default_manifest()

    try:
        payload = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_manifest_object,
            parse_constant=_manifest_constant, parse_float=_manifest_float)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Source-ingest manifest is damaged; preserve and restore it before proceeding.") from exc
    if not isinstance(payload, dict) or type(payload.get("version")) is not int or payload.get("version") != 1 or not isinstance(payload.get("entries"), list):
        raise ValueError("Source-ingest manifest schema is invalid.")
    seen = set()
    for entry in payload["entries"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("source_path"), str) or not entry["source_path"]:
            raise ValueError("Source-ingest manifest entry is invalid.")
        if entry["source_path"] in seen or _entry_state(entry) not in {"active", "needs_summary", "stale", "orphan"}:
            raise ValueError("Source-ingest manifest identity or state is invalid.")
        seen.add(entry["source_path"])
        source = entry["source_path"]
        if "\\" in source or "\0" in source or source.startswith("/") or any(part in ("", ".", "..") for part in source.split("/")) or (len(source) > 1 and source[1] == ":"):
            raise ValueError("Source-ingest manifest source path is invalid.")
        for field in ("content_hash", "summary_hash", "summary_path", "reason", "related_source", "orphan_summary_path", "state"):
            if field in entry and not isinstance(entry[field], str):
                raise ValueError("Source-ingest manifest field type is invalid.")
        if "size" in entry and (type(entry["size"]) is not int or entry["size"] < 0):
            raise ValueError("Source-ingest manifest size is invalid.")
        # Legacy summary paths are intentionally treated as local basenames
        # by _entry_summary_path, including old absolute/traversal spellings.
        # They remain typed strings and never grant access to that location.
    return payload


def _manifest_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Source-ingest manifest has duplicate JSON keys.")
        result[key] = value
    return result


def _manifest_constant(value: str) -> None:
    raise ValueError("Source-ingest manifest contains non-finite JSON.")


def _manifest_float(value: str) -> float:
    import math
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Source-ingest manifest contains non-finite JSON.")
    return result


def _normalized_entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        return []
    return [entry for entry in entries if isinstance(entry, dict)]


def _entry_by_source(entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(entry.get("source_path") or ""): entry
        for entry in entries
        if str(entry.get("source_path") or "")
    }


def _entry_state(entry: dict[str, Any]) -> str:
    return str(entry.get("state") or "active")


def _entry_hash(entry: dict[str, Any]) -> str:
    return str(entry.get("content_hash") or "")


def _entry_summary_hash(entry: dict[str, Any]) -> str:
    return str(entry.get("summary_hash") or "")


def _entry_summary_path(entry: dict[str, Any], fallback: str) -> str:
    value = str(entry.get("summary_path") or "")
    return value or fallback


def _entry_reason(entry: dict[str, Any], fallback: str = "") -> str:
    value = str(entry.get("reason") or "")
    return value or fallback


def _entry_for_record(
    record: SourceRecord,
    *,
    state: str,
    reason: str,
    related_source: str = "",
    orphan_summary_path: str = "",
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "source_path": record.source_path,
        "summary_path": record.summary_path,
        "content_hash": record.content_hash,
        "summary_hash": record.summary_hash,
        "size": record.size,
        "state": state,
        "reason": reason,
    }
    if related_source:
        entry["related_source"] = related_source
    if orphan_summary_path:
        entry["orphan_summary_path"] = orphan_summary_path
    return entry


def _set_entry_state(
    entry: dict[str, Any],
    *,
    state: str,
    reason: str,
    related_source: str = "",
    orphan_summary_path: str = "",
) -> dict[str, Any]:
    updated = dict(entry)
    updated["state"] = state
    updated["reason"] = reason
    if related_source:
        updated["related_source"] = related_source
    else:
        updated.pop("related_source", None)
    if orphan_summary_path:
        updated["orphan_summary_path"] = orphan_summary_path
    else:
        updated.pop("orphan_summary_path", None)
    return updated


def _orphan_entry(previous: dict[str, Any], *, reason: str, related_source: str = "") -> dict[str, Any]:
    entry = dict(previous)
    entry["state"] = "orphan"
    entry["reason"] = reason
    if related_source:
        entry["related_source"] = related_source
    return entry


def _find_rename_candidate(
    record: SourceRecord,
    previous_entries: list[dict[str, Any]],
    claimed_sources: set[str],
    current_paths: set[str],
) -> dict[str, Any] | None:
    for entry in previous_entries:
        source_path = str(entry.get("source_path") or "")
        if not source_path or source_path in claimed_sources or source_path in current_paths:
            continue
        if _entry_state(entry) == "orphan":
            continue
        if _entry_hash(entry) == record.content_hash:
            return entry
    return None


def _summary_is_resolved(record: SourceRecord, previous: dict[str, Any]) -> bool:
    if not record.summary_exists or record.summary_is_scaffold:
        return False
    return record.summary_hash != _entry_summary_hash(previous)


def _ensure_summary_scaffold(summary_dir: Path, record: SourceRecord, reason: str) -> SourceRecord:
    summary_path = summary_dir / record.summary_path
    if not summary_path.exists():
        try:
            scaffold_summary(summary_dir, record.source_path, reason)
        except OSError:
            pass

    summary_exists, summary_hash, summary_is_scaffold = _summary_details(summary_path)
    return SourceRecord(
        source_path=record.source_path,
        content_hash=record.content_hash,
        size=record.size,
        summary_path=record.summary_path,
        summary_exists=summary_exists,
        summary_hash=summary_hash,
        summary_is_scaffold=summary_is_scaffold,
    )


def reconcile_manifest(
    manifest: dict[str, Any],
    current_records: list[SourceRecord],
    summary_dir: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    previous_entries = sorted(
        _normalized_entries(manifest),
        key=lambda entry: str(entry.get("source_path") or ""),
    )
    previous_by_source = _entry_by_source(previous_entries)

    claimed_sources: set[str] = set()
    next_entries: dict[str, dict[str, Any]] = {}
    current_paths = {record.source_path for record in current_records}

    for record in current_records:
        previous = previous_by_source.get(record.source_path)
        if previous and _entry_state(previous) != "orphan":
            if record.content_hash != _entry_hash(previous):
                if _summary_is_resolved(record, previous):
                    next_entries[record.source_path] = _entry_for_record(
                        record,
                        state="active",
                        reason="",
                    )
                else:
                    next_entries[record.source_path] = _entry_for_record(
                        record,
                        state="stale",
                        reason="content modified",
                    )
                continue

            previous_state = _entry_state(previous)
            if previous_state in {"needs_summary", "stale"}:
                if _summary_is_resolved(record, previous):
                    next_entries[record.source_path] = _entry_for_record(
                        record,
                        state="active",
                        reason="",
                    )
                else:
                    next_entries[record.source_path] = _set_entry_state(
                        previous,
                        state=previous_state,
                        reason=_entry_reason(previous, "new file"),
                    )
                continue

            next_entries[record.source_path] = _entry_for_record(
                record,
                state="active",
                reason="",
            )
            continue

        rename_candidate = _find_rename_candidate(record, previous_entries, claimed_sources, current_paths)
        if rename_candidate:
            claimed_sources.add(str(rename_candidate.get("source_path") or ""))
            record = _ensure_summary_scaffold(summary_dir, record, "renamed/moved")
            next_entries[str(rename_candidate.get("source_path") or "")] = _orphan_entry(
                rename_candidate,
                reason="renamed/moved",
                related_source=record.source_path,
            )
            next_entries[record.source_path] = _entry_for_record(
                record,
                state="needs_summary" if record.summary_is_scaffold else "active",
                reason="renamed/moved" if record.summary_is_scaffold else "",
                related_source=str(rename_candidate.get("source_path") or ""),
                orphan_summary_path=_entry_summary_path(rename_candidate, ""),
            )
            continue

        if record.summary_exists and not record.summary_is_scaffold:
            next_entries[record.source_path] = _entry_for_record(
                record,
                state="active",
                reason="",
            )
            continue

        record = _ensure_summary_scaffold(summary_dir, record, "new file")
        next_entries[record.source_path] = _entry_for_record(
            record,
            state="needs_summary",
            reason="new file",
        )

    current_paths = {record.source_path for record in current_records}
    for previous in previous_entries:
        source_path = str(previous.get("source_path") or "")
        if not source_path or source_path in next_entries:
            continue

        summary_name = Path(_entry_summary_path(previous, "")).name
        summary_path = summary_dir / summary_name
        summary_exists, summary_hash, _summary_is_scaffold = _summary_details(summary_path)
        if not summary_exists:
            continue

        if source_path in current_paths:
            continue

        reason = _entry_reason(previous, "deleted")
        if _entry_state(previous) != "orphan":
            reason = "deleted"

        entry = dict(previous)
        entry["summary_hash"] = summary_hash
        entry["state"] = "orphan"
        entry["reason"] = reason
        if reason == "deleted":
            entry.pop("related_source", None)
            entry.pop("orphan_summary_path", None)
        next_entries[source_path] = entry

    ordered_entries = [next_entries[key] for key in sorted(next_entries)]
    next_manifest = {
        "version": 1,
        "entries": ordered_entries,
    }
    report_entries = [entry for entry in ordered_entries if _entry_state(entry) != "active"]
    return report_entries, next_manifest


def scaffold_summary(summary_dir: Path, source_relpath: str, reason: str) -> Path:
    summary_path = summary_path_for_source(summary_dir, source_relpath)
    try:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        if summary_path.exists():
            return summary_path

        summary_relpath = summary_path.name
        content = "\n".join(
            [
                "---",
                f"type: {DRAFT_SUMMARY_TYPE}",
                "description: " + json.dumps(
                    f"Pending ingestion of raw source `.agents/sources/{source_relpath}`.",
                    ensure_ascii=False,
                ),
                "sources:",
                "  - resource: " + json.dumps(
                    "../../sources/" + quote(source_relpath, safe="/"),
                    ensure_ascii=False,
                ),
                f"status: {DRAFT_SUMMARY_STATUS}",
                "---",
                "",
                f"# Summary scaffold for `{Path(source_relpath).name}`",
                "",
                "## Core Details",
                f"- **Source File**: `.agents/sources/{source_relpath}`",
                f"- **Summary File**: `.agents/memory/sources/{summary_relpath}`",
                f"- **Stale Reason**: {reason}",
                "",
                "## Executive Summary",
                "- Pending verification.",
                "",
                "## Key Findings",
                "- Pending verification.",
                "",
                "## Integration Checklist",
                "- [ ] Read the raw source.",
                "- [ ] Update the executive summary with verified facts.",
                "- [ ] Update the key findings with verified facts.",
                "- [ ] Weave durable facts into `.agents/memory/*` or `.agents/instructions/*`.",
                "- [ ] Append an integrate record to `.agents/memory/LOG.md` after successful ingestion.",
                "",
            ]
        )
        summary_path.write_text(content, encoding="utf-8")
    except OSError:
        pass
    return summary_path


def save_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    try:
        temp_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temp_path.replace(path)
        path.with_suffix(".expected").write_text("source-ingest-manifest-v1\n", encoding="utf-8")
    finally:
        try:
            if temp_path.exists():
                temp_path.unlink()
        except OSError:
            pass


class ManifestLock:
    def __init__(self, manifest_path: Path, timeout_seconds: float = 10.0):
        self.lock_path = manifest_path.with_suffix(manifest_path.suffix + ".lock")
        self.timeout_seconds = timeout_seconds
        self.lock_fd = None

    def __enter__(self) -> ManifestLock:
        try:
            import fcntl
        except ImportError:
            fcntl = None

        try:
            self.lock_path.parent.mkdir(parents=True, exist_ok=True)
            self.lock_fd = os.open(str(self.lock_path), os.O_CREAT | os.O_RDWR, 0o600)
        except OSError as exc:
            raise ValueError("Source-ingest manifest lock is unavailable.") from exc

        if fcntl is None:
            import msvcrt
            if os.fstat(self.lock_fd).st_size == 0:
                os.write(self.lock_fd, b"\0")

        import time
        deadline = time.monotonic() + self.timeout_seconds
        while True:
            try:
                if fcntl is not None:
                    fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                else:
                    os.lseek(self.lock_fd, 0, os.SEEK_SET)
                    msvcrt.locking(self.lock_fd, msvcrt.LK_NBLCK, 1)
                return self
            except OSError as exc:
                import errno
                if exc.errno not in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                    os.close(self.lock_fd)
                    self.lock_fd = None
                    break
                if time.monotonic() >= deadline:
                    try:
                        os.close(self.lock_fd)
                    except OSError:
                        pass
                    self.lock_fd = None
                    break
                time.sleep(0.05)
        raise ValueError("Source-ingest manifest lock could not be acquired.")

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.lock_fd is not None:
            try:
                import fcntl
                fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
            except ImportError:
                try:
                    import msvcrt
                    os.lseek(self.lock_fd, 0, os.SEEK_SET)
                    msvcrt.locking(self.lock_fd, msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass
            except OSError:
                pass
            try:
                os.close(self.lock_fd)
            except OSError:
                pass
            self.lock_fd = None


def build_context(report_entries: list[dict[str, Any]], manifest_file: Path, skill_available: bool = True) -> str:
    if not report_entries:
        return ""

    blocking = blocking_entries(report_entries)
    orphan_entries = [entry for entry in report_entries if _entry_state(entry) == "orphan"]

    if not blocking and not orphan_entries:
        return ""

    lines: list[str] = []

    if blocking:
        lines.append(PENDING_INGEST_DIRECTIVE)
        if skill_available:
            lines.append(PENDING_INGEST_SKILL_PROMPT)
        else:
            lines.append(PENDING_INGEST_SKILL_MISSING)
            lines.append("")
            lines.extend(_recovery_checklist())
        lines.append("")
        lines.append("## Pending entries")
        for entry in blocking:
            lines.append(_pending_entry_label(entry))
        lines.append("")

    lines.extend(_build_orphan_context(orphan_entries))
    return "\n".join(lines).rstrip() + "\n"


def context_snapshot(repo_root: Path, *, reconcile: bool = False) -> dict[str, Any]:
    """Canonical standalone bridge protocol. Environment overrides are legacy-only."""
    sources = repo_root / ".agents/sources"
    summaries = repo_root / ".agents/memory/sources"
    manifest_file = summaries / MANIFEST_FILE_NAME
    skill = repo_root / ".agents/skills/ingest-source/SKILL.md"
    for path in (sources, summaries, manifest_file, skill):
        ordinary_repository_path(repo_root, path)
    for directory in (sources, summaries):
        if directory.exists():
            for path in directory.rglob("*"):
                ordinary_repository_path(repo_root, path)
    for path in (manifest_file.with_suffix(".expected"), manifest_file.with_suffix(manifest_file.suffix + ".lock")):
        ordinary_repository_path(repo_root, path)
    load_manifest(manifest_file, expected=True)
    if reconcile:
        with ManifestLock(manifest_file):
            manifest = load_manifest(manifest_file, expected=True)
            records = scan_sources(sources, summaries)
            prior = _entry_by_source(manifest["entries"])
            changed_sources = sorted({record.source_path for record in records if record.source_path not in prior or record.content_hash != _entry_hash(prior[record.source_path])}
                | {name for name, entry in prior.items() if name not in {record.source_path for record in records} and _entry_state(entry) != "orphan"})
            _, manifest = reconcile_manifest(manifest, records, summaries)
            save_manifest(manifest_file, manifest)
    manifest = load_manifest(manifest_file, expected=True)
    records = scan_sources(sources, summaries)
    previous = _entry_by_source(manifest["entries"])
    if not reconcile:
        changed_sources = sorted({record.source_path for record in records if record.source_path not in previous or record.content_hash != _entry_hash(previous[record.source_path])}
            | {name for name, entry in previous.items() if name not in {record.source_path for record in records} and _entry_state(entry) != "orphan"})
    entries = []
    files = {manifest_file.relative_to(repo_root).as_posix(): _read_file_hash(manifest_file)}
    for record in records:
        path = sources / record.source_path
        summary = summaries / record.summary_path
        for target in (path, summary):
            if target.is_symlink() or not target.resolve().is_relative_to(repo_root.resolve()):
                raise ValueError("Source or summary access escapes the repository.")
        prior = previous.get(record.source_path)
        state = _entry_state(prior) if prior else "needs_summary"
        if prior and record.content_hash != _entry_hash(prior):
            state = "stale"
        if not record.summary_exists or record.summary_is_scaffold:
            state = "needs_summary" if state != "stale" else state
        entry = {"source_path": record.source_path, "source_revision": record.content_hash,
            "summary_path": summary.relative_to(repo_root).as_posix(),
            "summary_revision": record.summary_hash if record.summary_exists else None,
            "state": state, "summary_resolved": record.summary_exists and not record.summary_is_scaffold}
        entries.append(entry)
        files[path.relative_to(repo_root).as_posix()] = record.content_hash
        if record.summary_exists:
            files[entry["summary_path"]] = record.summary_hash
    orphans = []
    current = {record.source_path for record in records}
    for entry in manifest["entries"]:
        if entry["source_path"] in current:
            continue
        summary = summaries / Path(_entry_summary_path(entry, summary_name_for_source(entry["source_path"]))).name
        if summary.is_symlink() or not summary.resolve().is_relative_to(repo_root.resolve()):
            raise ValueError("Orphan summary access escapes the repository.")
        _, summary_hash, _ = _summary_details(summary)
        orphans.append({"source_path": entry["source_path"], "summary_path": summary.relative_to(repo_root).as_posix(),
            "summary_revision": summary_hash if summary.is_file() else None, "state": "orphan"})
        if summary.is_file():
            files[summary.relative_to(repo_root).as_posix()] = summary_hash
    available = skill.is_file() and os.access(skill, os.R_OK)
    if available:
        files[skill.relative_to(repo_root).as_posix()] = _read_file_hash(skill)
    return {"schema_version": 1, "entries": entries, "blocking": [entry for entry in entries if entry["state"] != "active"],
        "orphans": orphans, "changes": changed_sources, "files": files, "skill_path": skill.relative_to(repo_root).as_posix(),
        "skill_available": available}


def ordinary_repository_path(root: Path, path: Path) -> None:
    """Reject every linked component before a scanner can read or write it."""
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Source-ingest paths must remain ordinary repository-local inputs.")
    current = root
    for part in path.relative_to(root).parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Linked source-ingest path components are unsupported.")


def bridge_main() -> int:
    import argparse
    import sys
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--reconcile", action="store_true")
    parser.add_argument("--settle", type=Path)
    parser.add_argument("--json", action="store_true", required=True)
    args = parser.parse_args()
    try:
        if args.settle is not None:
            settle_sources(args.repository_root.resolve(), json.loads(args.settle.read_text(encoding="utf-8")))
        result = context_snapshot(args.repository_root.resolve(), reconcile=args.reconcile)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError, UnicodeError) as exc:
        print(json.dumps({"schema_version": 1, "error": str(exc)}))
        print(str(exc), file=sys.stderr)
        return 1


def settle_sources(root: Path, evidence: dict[str, Any]) -> None:
    """Mechanical settlement of foreground-checked current artifacts only.

    This operation grants no semantic authority. Agent-brain separately checks
    pre-pass bases, attributable knowledge, actual checks and registered owners.
    """
    before = context_snapshot(root)
    if before["files"] != evidence["checked_files"]:
        raise ValueError("Source inputs differ from checked settlement files.")
    manifest_file = root / ".agents/memory/sources" / MANIFEST_FILE_NAME
    with ManifestLock(manifest_file):
        current = context_snapshot(root)
        if current != before:
            raise ValueError("Source inputs changed before manifest settlement.")
        records = {entry["source_path"]: entry for entry in current["entries"]}
        manifest = load_manifest(manifest_file, expected=True)
        for entry in evidence["entries"]:
            actual = records.get(entry["source_path"])
            if (not actual or not actual["summary_resolved"] or actual["source_revision"] != entry["source_revision"]
                    or actual["summary_revision"] != entry["summary_revision"]):
                raise ValueError("Source settlement evidence is not current.")
            target = next(item for item in manifest["entries"] if item["source_path"] == entry["source_path"])
            target.update(state="active", reason="", content_hash=actual["source_revision"], summary_hash=actual["summary_revision"])
        save_manifest(manifest_file, manifest)


def join_agent_brain(repo_root: Path, payload: dict[str, Any]) -> dict[str, Any] | None:
    """Join a registered common-protocol obligation; never synthesize authority."""
    import subprocess
    import sys
    config_path = repo_root / ".agents/context/config.json"
    if not config_path.is_file():
        return None
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        integration = config.get("source_ingestion", {})
        if not integration.get("enabled", False):
            return None
        path = integration["bridge_path"]
        target = repo_root / path
        if not isinstance(path, str) or Path(path).is_absolute() or ".." in Path(path).parts or target.is_symlink() or not target.resolve().is_relative_to(repo_root.resolve()):
            raise ValueError("Configured bridge path is not repository-local.")
        if _read_file_hash(target) != integration["bridge_revision"]:
            raise ValueError("Configured bridge bytes differ from their trusted revision.")
        event = payload.get("agent_brain_event")
        if not isinstance(event, dict):
            # Native providers never inject the fixture-only private event.
            # The pinned bridge validates the activated native registration;
            # this gate neither synthesizes authority nor reconciles sources.
            result = subprocess.run([sys.executable, str(target), "--json", "--native-gate"], cwd=repo_root,
                input=json.dumps(payload).encode("utf-8"), capture_output=True, timeout=3.5, check=False)
            response = json.loads(result.stdout.decode("utf-8"))
            if result.returncode or type(response.get("completed")) is not bool or not isinstance(response.get("reason"), str):
                raise ValueError("Validated native join is unavailable.")
            return response
        result = subprocess.run([sys.executable, str(target), "--json"], cwd=repo_root,
            input=json.dumps(event).encode("utf-8"), capture_output=True, timeout=60, check=False)
        response = json.loads(result.stdout.decode("utf-8"))
        completed = result.returncode == 0 and response.get("work_session_status") == "completed"
        reason = "Source-ingest gate joined the current agent-brain learn obligation."
        if result.returncode or response.get("operation_status") != "ok":
            reason += " Current registration or source inputs are unavailable; restore foreground context."
        elif not completed:
            reason += " Complete the canonical foreground learn procedure before concluding."
            if response.get("invocation_file"):
                reason += " Invocation file: " + response["invocation_file"]
        return {"completed": completed, "reason": reason}
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError):
        return {"completed": False, "reason": "Source-ingest gate is incomplete; restore the configured agent-brain bridge and foreground registration."}


if __name__ == "__main__":
    raise SystemExit(bridge_main())
