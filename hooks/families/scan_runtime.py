"""Deterministic provider-local copies of the normal scanner dependency closure."""
from pathlib import Path
from hooks.manifest import GeneratedTarget
from hooks.providers import Provider

MODULES = ('scan_types', 'scan_reporting', 'scan_allowlist', 'scan_stream', 'scan_git', 'scan_native_file', 'scan_native_process', 'scan_audit', 'scan_engine')


def render(provider: Provider, target: GeneratedTarget) -> str:
    name = target.output_path.stem
    if target.family != "scan_runtime" or target.provider != provider.name or name not in MODULES:
        raise ValueError("Unsupported scanner runtime target")
    source = (Path(__file__).resolve().parents[1] / "runtime" / (name + ".py")).read_text()
    return ("#!/usr/bin/env python3\n"
            "# Generated from hooks/families/scan_runtime.py by scripts/generate-hooks.py. Do not edit.\n"
            + source)
