from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MANIFEST_FILE_NAME = "source-ingest-manifest.json"
SUMMARY_SUFFIX = ".summary.md"
SCAFFOLD_STATUS_MARKER = "status: scaffold"


@dataclass(frozen=True)
class SourceRecord:
    source_path: str
    content_hash: str
    size: int
    summary_path: str
    summary_exists: bool
    summary_hash: str
    summary_is_scaffold: bool


def summary_name_for_source(relpath: str) -> str:
    encoded = "__".join(part.replace(".", "-") for part in Path(relpath).parts)
    return f"{encoded}{SUMMARY_SUFFIX}"


def summary_path_for_source(summary_dir: Path, relpath: str) -> Path:
    return summary_dir / summary_name_for_source(relpath)


def manifest_path_for_summary_root(summary_dir: Path) -> Path:
    return summary_dir / MANIFEST_FILE_NAME


def default_manifest() -> dict[str, Any]:
    return {"version": 1, "entries": []}


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _read_file_hash(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _is_scaffold_summary(text: str) -> bool:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return False
    frontmatter_lines = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        frontmatter_lines.append(line)
    frontmatter_text = "\n".join(frontmatter_lines)
    return SCAFFOLD_STATUS_MARKER in frontmatter_text


def _summary_details(path: Path) -> tuple[bool, str, bool]:
    if not path.exists() or not path.is_file() or path.is_symlink():
        return False, "", False

    content = path.read_bytes()
    text = content.decode("utf-8", errors="replace")
    return True, _sha256_bytes(content), _is_scaffold_summary(text)


def _is_hidden_relative(relpath: Path) -> bool:
    return any(part.startswith(".") for part in relpath.parts)


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


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    if not manifest_path.exists():
        return default_manifest()

    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default_manifest()

    if not isinstance(payload, dict):
        return default_manifest()

    entries = payload.get("entries")
    if not isinstance(entries, list):
        payload["entries"] = []
    if payload.get("version") != 1:
        payload["version"] = 1
    return payload


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
        scaffold_summary(summary_dir, record.source_path, reason)

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
                    next_entries[record.source_path] = _entry_for_record(
                        record,
                        state=previous_state,
                        reason=_entry_reason(previous, "new file"),
                        related_source=str(previous.get("related_source") or ""),
                        orphan_summary_path=str(previous.get("orphan_summary_path") or ""),
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
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    if summary_path.exists():
        return summary_path

    summary_relpath = summary_path.name
    content = "\n".join(
        [
            "---",
            "status: scaffold",
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
    return summary_path


def save_manifest(manifest_path: Path, manifest: dict[str, Any]) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = manifest_path.with_name(f"{manifest_path.name}.{os.getpid()}.tmp")
    temp_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(manifest_path)


def build_context(report_entries: list[dict[str, Any]], manifest_path: Path) -> str:
    if not report_entries:
        return ""

    lines = [
        "Auto-ingest source updates detected.",
        "",
        f"Manifest: `{manifest_path.as_posix()}`",
    ]

    actionable_entries = [entry for entry in report_entries if _entry_state(entry) in {"needs_summary", "stale"}]
    orphan_entries = [entry for entry in report_entries if _entry_state(entry) == "orphan"]

    if actionable_entries:
        lines.extend(
            [
                "Activate `ingest-source` for new, modified, and renamed sources below.",
                "",
            ]
        )
        lines.append("## Sources requiring `ingest-source`")
        for entry in actionable_entries:
            summary_name = _entry_summary_path(entry, "")
            lines.append(f"- `.agents/sources/{entry['source_path']}`")
            lines.append(f"  - stale reason: {_entry_reason(entry)}")
            lines.append(f"  - summary: `.agents/memory/sources/{summary_name}`")
            related_source = str(entry.get("related_source") or "")
            orphan_summary_path = str(entry.get("orphan_summary_path") or "")
            if related_source:
                lines.append(f"  - previous source path: `.agents/sources/{related_source}`")
            if orphan_summary_path:
                lines.append(f"  - orphan summary to clean up later: `.agents/memory/sources/{orphan_summary_path}`")
        lines.append("")

    if orphan_entries:
        lines.extend(
            [
                "Do not invoke `ingest-source` for deleted sources; clean up orphan summaries manually.",
                "",
            ]
        )
        lines.append("## Orphan summaries requiring cleanup")
        for entry in orphan_entries:
            summary_name = _entry_summary_path(entry, "")
            lines.append(f"- `.agents/sources/{entry['source_path']}`")
            lines.append(f"  - stale reason: {_entry_reason(entry)}")
            lines.append(f"  - orphan summary: `.agents/memory/sources/{summary_name}`")
            related_source = str(entry.get("related_source") or "")
            if related_source:
                lines.append(f"  - replacement source path: `.agents/sources/{related_source}`")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
