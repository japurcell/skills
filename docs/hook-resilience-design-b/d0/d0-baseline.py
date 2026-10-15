#!/usr/bin/env python3
"""Retain incident-shaped source-provider denials without changing live hooks."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import runpy
import subprocess
import sys
import tempfile

SIZES = [3611602, 3131324, 2495842, 3340075, 3319151, 4128480]


def run(args, cwd, env, data=None, expected=0):
    p = subprocess.run(args, cwd=cwd, env=env, input=data, capture_output=True, timeout=30)
    if expected is not None:
        assert p.returncode == expected, p.stderr
    return p


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    sys.path.insert(0, str(source / "scripts"))
    from hook_test_support import hook_entrypoint, raw_tool_envelope
    observations = []
    workloads = []
    with tempfile.TemporaryDirectory(prefix="d0-baseline-") as temp:
        root = Path(temp).resolve()
        home = root / "home"
        home.mkdir()
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k not in {"SKIP_SECRETS_SCAN", "SECRETS_ALLOWLIST", "PYTHONPATH"}}
        env.update(HOME=str(home), USERPROFILE=str(home), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0", SCAN_MODE="block", SCAN_SCOPE="diff", OBSERVABILITY_TESTING="1")
        for workload in ("merge", "six-binaries"):
            repo = root / workload
            if workload == "merge":
                run(["git", "clone", "--shared", "--no-checkout", "-q", str(source), str(repo)], root, env)
                run(["git", "-c", "core.hooksPath=/dev/null", "checkout", "-q", "e5c2be2095ba30626559adae7fb2c49ba691734e"], repo, env)
                merge = run(["git", "-c", "user.name=D0", "-c", "user.email=d0@example.invalid", "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", "merge", "--no-commit", "--no-ff", "5f3948c92e5037fb066321e9c9e5b03419410671"], repo, env, expected=None)
                assert merge.returncode == 1
            else:
                repo.mkdir()
                run(["git", "init", "-q", str(repo)], root, env)
                for number, size in enumerate(SIZES):
                    (repo / f"image-{number}.png").write_bytes(b"\x89PNG\x00" + b"\0" * (size - 5))
                (repo / "repair.txt").write_text("safe pending input\n")
            before_status = run(["git", "status", "--porcelain=v1", "-z"], repo, env).stdout
            scanner = runpy.run_path(str(source / ".codex/hooks/scan-secrets.py"))
            candidates = scanner["collect_files"](repo, "diff", workload == "merge")
            total = 0
            for kind, name in candidates:
                if kind in {"staged", "unmerged-base", "unmerged-ours", "unmerged-theirs"}:
                    stage = {"staged": 0, "unmerged-base": 1, "unmerged-ours": 2, "unmerged-theirs": 3}[kind]
                    total += len(run(["git", "show", f":{stage}:{name}"], repo, env).stdout)
                elif (repo / name).is_file():
                    total += (repo / name).stat().st_size
            workloads.append(dict(name=workload, pending_snapshots=len(candidates), logical_candidate_bytes=total))
            def fingerprint():
                value = hashlib.sha256((repo / ".git/index").read_bytes() if (repo / ".git/index").exists() else b"")
                for path in sorted(repo.rglob("*")):
                    if ".git" not in path.relative_to(repo).parts and path.is_file():
                        value.update(os.fsencode(path.relative_to(repo)))
                        value.update(path.read_bytes())
                return value.hexdigest()
            before = fingerprint()
            for provider in ("codex", "copilot", "gemini"):
                installed = root / (workload + "-" + provider) / hook_entrypoint(Path(), provider, "scan-secrets.py")
                shutil.copytree((source / hook_entrypoint(Path(), provider, "scan-secrets.py")).parent, installed.parent)
                logs = root / (workload + "-" + provider + "-logs")
                logs.mkdir()
                child_env = {**env, "SECRETS_LOG_DIR": str(logs), "AUDIT_LOG": str(logs / "audit.log"), "AUDIT_LOCK": str(logs / "audit.lock"), "OBSERVABILITY_LOG_PATH": str(logs / "observability.jsonl"), "TMPDIR": str(root)}
                for action in ("read", "repair", "completion", "completion-repeat"):
                    tool = {"codex": "exec_command", "copilot": "bash", "gemini": "run_shell_command"}[provider]
                    cmd = "rtk read repair.txt" if action == "read" else "python3 -c \"from pathlib import Path; Path('repair.txt').write_text('repair')\""
                    arguments = {"cmd": cmd, "login": False} if provider == "codex" else {"command": cmd}
                    payload = raw_tool_envelope(provider, tool, arguments)
                    payload["cwd"] = str(repo)
                    if action.startswith("completion"):
                        payload["hook_event_name"] = {"codex": "Stop", "copilot": "sessionEnd", "gemini": "SessionEnd"}[provider]
                        payload["stop_hook_active"] = action.endswith("repeat")
                    proc = run([sys.executable, "-I", "-S", "-B", str(installed)], repo, child_env, json.dumps(payload).encode())
                    response = json.loads(proc.stdout)
                    record = json.loads((logs / "scan.log").read_text().splitlines()[-1])
                    assert record["status"] == "incomplete", record
                    assert record["enforcement"] == "deny", record
                    assert "scan incomplete" in json.dumps(response)
                    assert fingerprint() == before
                    assert run(["git", "status", "--porcelain=v1", "-z"], repo, env).stdout == before_status
                    observations.append(dict(workload=workload, provider=provider, action=action, exit=proc.returncode, response=response, diagnostic=record["diagnostic"], build=record["build"], pending_unchanged=True))
    args.output.write_text(json.dumps(dict(source_revision=run(["git", "rev-parse", "HEAD"], source, os.environ).stdout.decode().strip(), image_bytes=sum(SIZES), image_sizes=SIZES, workloads=workloads, observations=observations), indent=2) + "\n")
    print(f"{len(observations)} native JSON source denials retained; pending state unchanged")


if __name__ == "__main__":
    main()
