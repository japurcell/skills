#!/usr/bin/env python3
"""Render reproducible W1 caller/router skill variants from the frozen baseline."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

BASE = "7fc651a7702735f0b13d1f50695a8ef0ddc96477"
ROOT = Path(__file__).resolve().parents[3]
CALLERS = {
    "delegate-to-subagents": "skills/default/delegate-to-subagents/SKILL.md",
    "execplan-implement": "skills/default/execplan-implement/SKILL.md",
}
ROUTER = "skills/default/subagent-model-router/SKILL.md"
GATES = Path(__file__).with_name("fixtures") / "gates.json"
STANDALONE = "Return the CLI's JSON result unchanged."


def load_gates() -> dict:
    return json.loads(GATES.read_text())


def git(path: str) -> str:
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT, text=True)


def word_count(text: str) -> int:
    return len(text.split())


def extra_reuse_text(caller: str, name: str) -> str:
    lines = caller.splitlines()
    if name == "delegate-to-subagents":
        return "\n".join(line for line in lines if line.startswith("- Follow the [pre-dispatch gate]"))
    return "\n".join(line for line in lines if (
        line.startswith("- Start with one implementer") or
        line.startswith("Start with one implementer") or
        line.startswith("Apply the [pre-dispatch gate](#pre-dispatch-gate) to each new assignment.")
    ))


def selected_section(text: str, heading: str, end: str) -> str:
    start_at = text.index(heading) + len(heading)
    return text[start_at:text.index(end, start_at)].strip()


def replace_section(text: str, start: str, end: str, content: str) -> str:
    a = text.index(start)
    b = text.index(end, a)
    return text[:a] + content.rstrip() + "\n\n" + text[b:]


def render(source: str, caller: bool, gate: str, addendum: str, shared: str) -> str:
    if caller:
        original_start = ("### Pre-dispatch gate\n" if source == CALLERS["delegate-to-subagents"]
                          else "## Pre-dispatch gate\n")
        end = "## Runtime enforcement\n"
        body = gate
        if addendum:
            body += "\n\n" + addendum
        text = git(source)
        text = replace_section(text, original_start, end, original_start.rstrip() + "\n\n" + body)
        if source == CALLERS["delegate-to-subagents"]:
            text = text.replace("- Follow the [pre-dispatch gate](#pre-dispatch-gate). Reuse requires the same model with no original effort override for `host_default`, or the exact model/effort pair for `explicit`.", "- Follow the [pre-dispatch gate](#pre-dispatch-gate).")
        else:
            text = text.replace("Start with one implementer and assign each implementer one task at a time. Reuse an idle implementer when its model and effort satisfy the pre-dispatch gate and its prior context helps with the task.", "Start with one implementer and assign each implementer one task at a time. Let the gate determine whether an idle implementer can take the next assignment.")
            text = text.replace("Apply the [pre-dispatch gate](#pre-dispatch-gate) to each new assignment. Reuse requires the same model with no original effort override for `host_default`, or the exact model/effort pair for `explicit`. Otherwise dispatch a fresh agent.", "Apply the [pre-dispatch gate](#pre-dispatch-gate) to each new assignment. If reuse is ineligible, dispatch a fresh agent.")
        return text
    text = git(source)
    text = text.replace("## Return the result\n", STANDALONE + "\n\n## Return the result\n", 1)
    start = "## Return the result\n"
    end = "Load [maintenance.md]"
    replacement = "## Dispatch controls\n\n" + shared + "\n\n"
    return replace_section(text, start, end, replacement)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    gates = load_gates()
    rows = []
    arms = [("baseline", None), ("short", gates["short"]), ("challenger", gates["challenger"]),
            ("challenger2", gates["challenger2"])]
    for arm, gate_spec in arms:
        shared = gate_spec["shared_rules"] if gate_spec else None
        for name, source in CALLERS.items():
            if gate_spec:
                gate = gate_spec["caller_gate"]
                addendum = gate_spec["caller_addenda"].get(name, "")
                caller = render(source, True, gate, addendum, shared)
                router = render(ROUTER, False, gate, addendum, shared)
            else:
                caller = git(source)
                router = git(ROUTER)
            caller_heading = ("### Pre-dispatch gate\n" if name == "delegate-to-subagents"
                              else "## Pre-dispatch gate\n")
            router_heading = "## Return the result\n" if arm == "baseline" else "## Dispatch controls\n"
            selected_caller = selected_section(caller, caller_heading, "## Runtime enforcement\n")
            selected_caller += " " + extra_reuse_text(caller, name)
            selected_shared = selected_section(router, router_heading, "Load [maintenance.md]")
            selected_shared = selected_shared.replace(STANDALONE, "").strip()
            directory = args.out / arm / name
            directory.mkdir(parents=True, exist_ok=True)
            (directory / "caller-SKILL.md").write_text(caller)
            (directory / "router-SKILL.md").write_text(router)
            rows.append({"arm": arm, "caller": name,
                         "count_basis": "rendered gate body + selected outside-gate reuse text + rendered router dispatch body; headings excluded",
                         "retained_standalone_words_excluded_from_gate_count": word_count(STANDALONE),
                         "caller_gate_words": word_count(selected_caller),
                         "shared_router_words": word_count(selected_shared),
                         "selected_total": word_count(selected_caller) + word_count(selected_shared),
                         "caller_sha256": hashlib.sha256((directory / "caller-SKILL.md").read_bytes()).hexdigest(),
                         "router_sha256": hashlib.sha256((directory / "router-SKILL.md").read_bytes()).hexdigest()})
    (args.out / "counts.json").write_text(json.dumps(rows, indent=2) + "\n")


if __name__ == "__main__":
    main()
