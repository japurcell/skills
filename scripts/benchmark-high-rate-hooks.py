#!/usr/bin/env python3
"""Measure retained hook entrypoints with synthetic macOS provider events.

The runner creates a disposable home and Git repositories. It never installs
hooks or invokes a provider CLI. Results are JSON so repeated runs can be
compared without relying on rounded terminal output.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import os
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Case:
    name: str
    script: Path | None
    payload: bytes
    repo: str
    environment: dict[str, str]


def run_git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def make_repo(path: Path, kind: str) -> None:
    path.mkdir()
    run_git(path, "init", "-q")
    (path / "safe.txt").write_text("safe baseline\n", encoding="utf-8")
    run_git(path, "add", "safe.txt")
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.name=Benchmark", "-c", "user.email=benchmark@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "baseline"],
        check=True,
        capture_output=True,
    )
    if kind == "finding":
        # Syntactically match the scanner's AWS key pattern using fake data.
        (path / ".env").write_text("aws=AKIA1234567890ABCDEF\n", encoding="utf-8")
    elif kind == "large":
        (path / "large.txt").write_text("safe words only\n" * 32768, encoding="utf-8")


def encoded(value: object) -> bytes:
    return (json.dumps(value, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def cases() -> list[Case]:
    result: list[Case] = []
    invalid = b'{"incomplete":\n'
    for provider in ("copilot", "gemini", "codex"):
        base = ROOT / (".codex/hooks" if provider == "codex" else f".{provider}/hooks/scripts")
        if provider == "copilot":
            clean = {"hook_event_name": "preToolUse", "toolName": "bash", "toolArgs": "echo safe"}
            finding = {**clean, "toolArgs": "git push --force origin main"}
            large = {**clean, "toolArgs": "echo " + "a" * 24000}
        elif provider == "gemini":
            clean = {"hook_event_name": "BeforeTool", "tool_name": "run_shell_command", "tool_input": {"command": "echo safe"}}
            finding = {**clean, "tool_input": {"command": "git push --force origin main"}}
            large = {**clean, "tool_input": {"command": "echo " + "a" * 24000}}
        else:
            clean = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "echo safe"}}
            finding = {**clean, "tool_input": {"command": "git push --force origin main"}}
            large = {**clean, "tool_input": {"command": "echo " + "a" * 24000}}
        for name, payload in (("clean", encoded(clean)), ("finding", encoded(finding)), ("large", encoded(large)), ("failure", invalid)):
            result.append(Case(f"{provider}.guard.{name}", base / "tool-guard.py", payload, "clean", {"GUARD_MODE": "block"}))
            result.append(Case(f"{provider}.scan.{name}", base / "scan-secrets.py", payload, "finding" if name == "finding" else "large" if name == "large" else "clean", {"SCAN_MODE": "block", "SCAN_SCOPE": "diff"}))

    for provider in ("copilot", "gemini"):
        base = ROOT / f".{provider}/hooks/scripts"
        event_name = "preToolUse" if provider == "copilot" else "BeforeTool"
        payload = encoded({"hook_event_name": event_name, "session_id": "bench-session", "tool_name": "run_shell_command", "tool_input": {"command": "echo safe"}})
        large_payload = encoded({"hook_event_name": event_name, "session_id": "bench-session", "tool_name": "run_shell_command", "tool_input": {"command": "echo " + "a" * 24000}})
        for name, data in (("clean", payload), ("large", large_payload), ("failure", invalid)):
            result.append(Case(f"{provider}.rtk.{name}", base / f"rtk-hook-{provider}.py", data, "clean", {}))
        telemetry_cases = [
            ("tool", event_name, payload),
            ("tool-large", event_name, large_payload),
            ("failure", event_name, invalid),
        ]
        if provider == "copilot":
            telemetry_cases.extend([
                ("tool-success", "postToolUse", encoded({"hook_event_name": "postToolUse", "session_id": "bench-session", "toolName": "bash", "toolResult": "safe result"})),
                ("tool-error", "postToolUseFailure", encoded({"hook_event_name": "postToolUseFailure", "session_id": "bench-session", "toolName": "bash", "error": "synthetic failure"})),
            ])
        else:
            telemetry_cases.extend([
                ("selection", "BeforeToolSelection", encoded({"hook_event_name": "BeforeToolSelection", "session_id": "bench-session"})),
                ("before-model", "BeforeModel", encoded({"hook_event_name": "BeforeModel", "session_id": "bench-session"})),
                ("model", "AfterModel", encoded({"hook_event_name": "AfterModel", "session_id": "bench-session", "llm_response": {"content": "chunk"}})),
                ("model-large", "AfterModel", encoded({"hook_event_name": "AfterModel", "session_id": "bench-session", "llm_response": {"content": "a" * 24000}})),
                ("tool-success", "AfterTool", encoded({"hook_event_name": "AfterTool", "session_id": "bench-session", "tool_name": "run_shell_command", "tool_response": {"output": "safe result"}})),
            ])
        for name, event, data in telemetry_cases:
            result.append(Case(f"{provider}.telemetry.{name}", base / "send-event.py", data, "clean", {"OBSERVABILITY_CAPTURE_EVENT": "true", "OBSERVABILITY_SOURCE_EVENT_NAME": event}))

    result.append(Case("control.clean", None, encoded({"tool_name": "Bash", "tool_input": {"command": "echo safe"}}), "clean", {}))
    result.append(Case("control.large", None, encoded({"tool_name": "Bash", "tool_input": {"command": "a" * 24000}}), "clean", {}))
    return result


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * fraction) - 1)]


def summary(values: list[float]) -> dict[str, float]:
    median = statistics.median(values)
    return {
        "median_ms": round(median, 3),
        "p95_ms": round(percentile(values, 0.95), 3),
        "min_ms": round(min(values), 3),
        "max_ms": round(max(values), 3),
        "mad_ms": round(statistics.median(abs(value - median) for value in values), 3),
    }


def verify_outcome(case: Case, exit_code: int, output: dict) -> None:
    if case.name.endswith(".failure") and ".telemetry." in case.name:
        if exit_code != 1 or not output.get("invalid_stdout"):
            raise RuntimeError(f"{case.name} did not fail on invalid JSON as expected")
        return
    if exit_code != 0 or output.get("invalid_stdout"):
        raise RuntimeError(f"{case.name} returned exit {exit_code} or invalid JSON")
    rendered = json.dumps(output).lower()
    if ".guard.finding" in case.name and "deny" not in rendered:
        raise RuntimeError(f"{case.name} did not deny the synthetic dangerous command")
    if ".scan.finding" in case.name and "deny" not in rendered:
        raise RuntimeError(f"{case.name} did not deny the synthetic scanner finding")
    if case.name.endswith(".failure") and ".scan." in case.name and "incomplete" not in rendered:
        raise RuntimeError(f"{case.name} did not report an incomplete scan")


def invoke(case: Case, repo: Path, home: Path, timeout: float = 15.0) -> tuple[float, int, dict]:
    env = os.environ.copy()
    env.update({
        "HOME": str(home),
        "XDG_CONFIG_HOME": str(home / ".config"),
        "XDG_CACHE_HOME": str(home / ".cache"),
        "XDG_DATA_HOME": str(home / ".local/share"),
        "AUDIT_LOG": str(home / "audit.log"),
        "AUDIT_LOCK": str(home / "audit.lock"),
        "TOOL_GUARD_LOG_DIR": str(home / "guard" if case.name.startswith("gemini") else home / "guard.log"),
        "SECRETS_LOG_DIR": str(home / "secrets"),
        "COPILOT_OBSERVABILITY_LOG_PATH": str(home / "copilot-observability.ndjson"),
        "GEMINI_OBSERVABILITY_LOG_PATH": str(home / "gemini-observability.ndjson"),
    })
    env.update(case.environment)
    command = [sys.executable, str(case.script)] if case.script else [sys.executable, "-c", "import json,sys; json.load(sys.stdin); print('{}')"]
    start = time.perf_counter_ns()
    completed = subprocess.run(command, input=case.payload, cwd=repo, env=env, capture_output=True, timeout=timeout)
    elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
    try:
        output = json.loads(completed.stdout)
    except (ValueError, UnicodeDecodeError):
        output = {"invalid_stdout": True}
    return elapsed_ms, completed.returncode, output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=25, help="number of warm calls per scenario")
    parser.add_argument("--warmups", type=int, default=3, help="warm calls to discard before samples")
    parser.add_argument("--concurrency", type=int, default=4, help="simultaneous calls in a separate batch")
    parser.add_argument("--output", type=Path, help="write machine-readable JSON to this path")
    args = parser.parse_args()
    if args.samples < 5 or args.warmups < 0 or args.concurrency < 2:
        parser.error("samples must be at least 5, warmups nonnegative, and concurrency at least 2")
    if platform.system() != "Darwin":
        parser.error("this milestone benchmark is macOS only")
    rtk_path = shutil.which("rtk")
    if not rtk_path:
        parser.error("rtk 0.50.0 or newer is required for the RTK forwarder scenarios")
    rtk_version = subprocess.run([rtk_path, "--version"], capture_output=True, text=True, check=True).stdout.strip()
    try:
        version_parts = tuple(int(part) for part in rtk_version.split()[1].split(".")[:3])
    except (IndexError, ValueError) as exc:
        parser.error(f"cannot parse RTK version: {rtk_version!r} ({exc})")
    if version_parts < (0, 50, 0):
        parser.error(f"rtk 0.50.0 or newer is required, found {rtk_version}")

    with tempfile.TemporaryDirectory(prefix="high-rate-hooks-") as temporary:
        temporary_root = Path(temporary)
        repos = {kind: temporary_root / f"repo-{kind}" for kind in ("clean", "finding", "large")}
        for kind, path in repos.items():
            make_repo(path, kind)
        results: list[dict] = []
        for case in cases():
            home = temporary_root / "homes" / case.name
            home.mkdir(parents=True)
            timings: list[float] = []
            outcomes: list[dict] = []
            for index in range(1 + args.warmups + args.samples):
                elapsed, exit_code, output = invoke(case, repos[case.repo], home)
                verify_outcome(case, exit_code, output)
                if index == 0:
                    cold_ms = elapsed
                elif index > args.warmups:
                    timings.append(elapsed)
                    outcomes.append(output)
            results.append({"case": case.name, "input_bytes": len(case.payload), "cold_ms": round(cold_ms, 3), "warm": summary(timings), "sample_count": len(timings), "first_output": outcomes[0], "exit_code": exit_code})

        concurrency_results: list[dict] = []
        selected = {"copilot.guard.clean", "gemini.guard.clean", "codex.guard.clean", "copilot.scan.clean", "gemini.scan.clean", "codex.scan.clean", "copilot.rtk.clean", "gemini.rtk.clean", "copilot.telemetry.tool", "gemini.telemetry.model"}
        for case in cases():
            if case.name not in selected:
                continue
            home = temporary_root / "homes" / case.name
            batch_start = time.perf_counter_ns()
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
                calls = list(pool.map(lambda _: invoke(case, repos[case.repo], home), range(args.concurrency)))
            batch_ms = (time.perf_counter_ns() - batch_start) / 1_000_000
            for _, exit_code, output in calls:
                verify_outcome(case, exit_code, output)
            concurrency_results.append({"case": case.name, "workers": args.concurrency, "batch_ms": round(batch_ms, 3), "individual": summary([elapsed for elapsed, _, _ in calls])})

        result = {
            "environment": {"platform": platform.platform(), "python": sys.version.split()[0], "rtk": rtk_version, "git": subprocess.run(["git", "--version"], capture_output=True, text=True, check=True).stdout.strip()},
            "method": {"samples": args.samples, "warmups": args.warmups, "concurrency": args.concurrency, "cold_definition": "first process for each case with a fresh disposable log home; OS file cache is not cleared", "warm_definition": "sequential subprocess calls after discarded warmups using the same log home"},
            "results": results,
            "concurrency": concurrency_results,
        }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
