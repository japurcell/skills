#!/usr/bin/env python3
"""Prepare and run one fresh Codex W1 controlled actor session."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BASE = "7fc651a7702735f0b13d1f50695a8ef0ddc96477"
CALLERS = {"delegate-to-subagents", "execplan-implement"}
ARMS = {"baseline", "short", "challenger", "challenger2"}
def prepare(arm: str, caller: str, project: Path, rendered_root: Path) -> None:
    if project.exists():
        raise RuntimeError(f"refusing to overwrite actor project: {project}")
    project.mkdir(parents=True)
    skill_root = project / ".agents" / "skills"
    caller_dir = skill_root / caller
    router_dir = skill_root / "subagent-model-router"
    caller_dir.mkdir(parents=True)
    router_dir.mkdir(parents=True)
    rendered = rendered_root / arm / caller
    shutil.copyfile(rendered / "caller-SKILL.md", caller_dir / "SKILL.md")
    shutil.copyfile(rendered / "router-SKILL.md", router_dir / "SKILL.md")
    source_router = REPO / "skills/default/subagent-model-router"
    shutil.copytree(source_router / "reference", router_dir / "reference")
    shutil.copytree(source_router / "scripts", router_dir / "scripts")
    private = project / ".w1"
    (private / "router").mkdir(parents=True)
    shutil.copytree(source_router / "scripts", private / "router" / "scripts")
    shutil.copytree(source_router / "reference", private / "router" / "reference")
    cases = json.loads((HERE / "fixtures/cases.json").read_text())
    actor_cases = {"cases": [{"id": item["id"], "route": item["route"],
                              "host": item["host"]["public"]} for item in cases["cases"]]}
    (private / "cases.json").write_text(json.dumps(actor_cases, indent=2) + "\n")
    bin_dir = project / "bin"
    bin_dir.mkdir()
    boundary = HERE / "host_boundary.py"
    boundary.chmod(0o755)
    for command in ("case38", "route38", "host38", "dispatch38", "reuse38"):
        (bin_dir / command).symlink_to(boundary)
    project.joinpath(".gitignore").write_text(".w1/events.jsonl\n")


def prompt(caller: str) -> str:
    return f"""You are an independent caller executing a controlled routing evaluation.

Read `.agents/skills/{caller}/SKILL.md` and `.agents/skills/subagent-model-router/SKILL.md` fully. Treat those files as your operating instructions. The host controls printed by `host38` are authoritative synthetic inputs. Do not edit the skills, route files, or case inputs.

Process each benign synthetic assignment listed by `case38 list`. The user objective for each is to return the sum of 19 and 23. Use the supplied task and host facts, apply the caller/router instructions, and report completion or blocker for every assignment. Do not edit the skills, route files, or case inputs.

The host API commands are available on PATH: `case38 list` prints assignments; `route38 CASE_ID` invokes the bundled router; `host38 CASE_ID` prints host facts; `dispatch38 CASE_ID --model MODEL [--effort LEVEL]` records a synthetic dispatch and completion or rejection; `reuse38 CASE_ID --worker WORKER_ID` records a synthetic reuse action. These commands produce an observable JSONL trace. Save a concise case-by-case report to `actor-report.txt`; actual decisions will be graded from command events, not that report."""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=sorted(ARMS), required=True)
    parser.add_argument("--caller", choices=sorted(CALLERS), required=True)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--run-suffix", default="")
    parser.add_argument("--scratch-root", type=Path, required=True)
    args = parser.parse_args()
    key = f"{args.arm}-{args.caller}"
    suffix = f"-{args.run_suffix}" if args.run_suffix else ""
    scratch = args.scratch_root.resolve()
    rendered_root = scratch / "rendered"
    if not rendered_root.exists():
        subprocess.run(["python3", str(HERE / "render_variants.py"), str(rendered_root)], check=True)
    project = scratch / "projects" / f"{key}{suffix}"
    output = scratch / "evidence" / f"{key}{suffix}"
    output.mkdir(parents=True, exist_ok=True)
    prepare(args.arm, args.caller, project, rendered_root)
    if args.prepare_only:
        print(project)
        return
    env = os.environ.copy()
    env["W1_PROJECT"] = str(project)
    env["W1_OUTCOMES"] = str(HERE / "fixtures/host-outcomes.json")
    env["PATH"] = str(project / "bin") + os.pathsep + env.get("PATH", "")
    (output / "codex-version.txt").write_text(subprocess.check_output(["rtk", "codex", "--version"], text=True))
    cmd = ["rtk", "proxy", "codex", "exec", "--ephemeral", "--json", "--skip-git-repo-check",
           "--approve-for-me", "--cd", str(project),
           "--output-last-message", str(project / "actor-response.txt"), prompt(args.caller)]
    (output / "command.json").write_text(json.dumps({"argv": cmd[:-1], "project": str(project),
                                                     "arm": args.arm, "caller": args.caller}, indent=2) + "\n")
    codex_home = Path(env.get("CODEX_HOME", str(Path.home() / ".codex")))
    subprocess.run(["python3", str(HERE / "host_config.py"), str(output / "command.json"),
                    str(output / "host-model.json"), "--config", str(codex_home / "config.toml")], check=True)
    proc = subprocess.run(cmd, env=env, text=True, capture_output=True, timeout=600)
    (output / "codex-events.jsonl").write_text(proc.stdout)
    subprocess.run(["python3", str(HERE / "extract_tool_order.py"),
                    str(output / "codex-events.jsonl"), str(output / "tool-order.jsonl")], check=True)
    subprocess.run(["python3", str(HERE / "case_records.py"),
                    str(project / ".w1" / "events.jsonl"), str(output / "case-records.jsonl")], check=True)
    (output / "stderr.txt").write_text(proc.stderr)
    (output / "exit-code.txt").write_text(str(proc.returncode) + "\n")
    if proc.returncode:
        raise SystemExit(proc.returncode)
    print(json.dumps({"project": str(project), "evidence": str(output), "exit_code": proc.returncode}))


if __name__ == "__main__":
    main()
