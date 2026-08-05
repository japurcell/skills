#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType

from helpers.audit import audit_log_event
from helpers.common import emit_json, first_present, read_json_input, sanitize_log_field, stringify_value


SCRIPT_NAME = Path(__file__).name


def log_event(message: str) -> None:
    try:
        audit_log_event(SCRIPT_NAME, message)
    except Exception:
        pass


def _repo_root(payload: dict[str, object]) -> Path:
    env_override = os.environ.get("COPILOT_AUTO_INGEST_REPO_ROOT")
    if env_override:
        return Path(env_override)

    cwd = stringify_value(first_present(payload, "cwd", "workingDirectory", "working_directory"))
    if cwd:
        return Path(cwd)

    return Path.cwd()


def _helper_path(repo_root: Path) -> Path:
    override = os.environ.get("COPILOT_AUTO_INGEST_HELPER_PATH")
    if override:
        return Path(override)
    return repo_root / ".github" / "hooks" / "scripts" / "helpers" / "auto_ingest.py"


def _load_helper(helper_path: Path) -> ModuleType | None:
    if not helper_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("copilot_repo_auto_ingest_helper", helper_path)
    if spec is None or spec.loader is None:
        return None

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _build_transformed_prompt(context: str, transformed_prompt: str) -> str:
    return f"{context.rstrip()}\n\n{transformed_prompt}"


def main() -> int:
    try:
        payload = read_json_input()
        if not isinstance(payload, dict):
            emit_json({})
            return 0

        transformed_prompt = stringify_value(first_present(payload, "transformedPrompt"))
        if not transformed_prompt:
            emit_json({})
            return 0

        repo_root = _repo_root(payload)
        helper = _load_helper(_helper_path(repo_root))
        if helper is None:
            emit_json({})
            return 0

        sources_dir = helper.source_root(repo_root)
        summaries_dir = helper.summary_root(repo_root)
        manifest_file = helper.manifest_path(summaries_dir)

        current_sources = helper.scan_sources(sources_dir, summaries_dir)
        previous_manifest = helper.load_manifest(manifest_file)
        report_entries, next_manifest = helper.reconcile_manifest(previous_manifest, current_sources, summaries_dir)
        helper.save_manifest(manifest_file, next_manifest)

        message = helper.build_context(report_entries, manifest_file)
        if not message.strip():
            emit_json({})
            return 0

        session_id = sanitize_log_field(stringify_value(first_present(payload, "sessionId", "session_id")))
        log_event(
            f"Message: injected auto-ingest context into transformed prompt, "
            f"Session: {session_id}, Findings: {len(report_entries)}"
        )

        emit_json({"modifiedTransformedPrompt": _build_transformed_prompt(message, transformed_prompt)})
        return 0
    except ValueError as exc:
        log_event(f"Error: {sanitize_log_field(str(exc))}")
        emit_json({})
    except Exception as exc:  # noqa: BLE001 - fail open on prompt rewrite errors
        log_event(f"Error: Unexpected exception: {sanitize_log_field(str(exc))}")
        emit_json({})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
