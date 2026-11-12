#!/usr/bin/env python3
"""Allocate private provider runs and record bounded provider CLI turns."""

import argparse
import hashlib
import json
import os
import signal
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import uuid


PROVIDERS = {"codex", "copilot"}
MAX_TIMEOUT = 1800


class Terminated(Exception):
    pass


def terminate_handler(signum, frame):
    raise Terminated()


def within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def digest(path: Path) -> str:
    value = hashlib.sha256()
    for item in sorted(path.rglob("*")):
        if item.is_file() and not item.is_symlink():
            value.update(item.relative_to(path).as_posix().encode())
            value.update(item.read_bytes())
    return value.hexdigest()


def call(args, *, cwd=None, env=None, timeout=15):
    process = subprocess.Popen(args, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, encoding="utf-8", errors="replace", shell=False,
                               start_new_session=True)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
        return subprocess.CompletedProcess(args, 124, stdout, stderr)
    except (KeyboardInterrupt, Terminated):
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise
    return subprocess.CompletedProcess(args, process.returncode, stdout, stderr)


def atomic_text(path: Path, value: str) -> None:
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def emit_json(value) -> bool:
    try:
        print(json.dumps(value, ensure_ascii=False), flush=True)
        return True
    except BrokenPipeError:
        try:
            sys.stdout.close()
        except BrokenPipeError:
            pass
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
        return False


def preflight(executable: str, provider: str) -> dict:
    if provider not in PROVIDERS:
        raise ValueError(f"unsupported provider: {provider}")
    version = call([executable, "--version"])
    if provider == "codex":
        helps = [call([executable, "exec", "--help"]), call([executable, "exec", "resume", "--help"])]
        required_by_help = (("--add-dir", "--cd", "--model", "--sandbox", "--json", "--output-last-message"),
                            ("--model", "--json", "--output-last-message"))
    else:
        helps = [call([executable, "--help"])]
        required_by_help = (("--add-dir", "--model", "--session-id", "--resume", "--reasoning-effort",
                             "--log-dir", "--output-format", "--prompt", "--allow-tool"),)
    if version.returncode or any(result.returncode for result in helps):
        raise ValueError(f"{provider} preflight failed: --version={version.returncode}, --help exits={[item.returncode for item in helps]}")
    missing = [option for help_result, required in zip(helps, required_by_help)
               for option in required if option not in help_result.stdout]
    if missing:
        raise ValueError(f"{provider} help is missing required persistent-run options: {', '.join(missing)}")
    help_text = "\n--- resume help ---\n".join(result.stdout for result in helps)
    return {"provider": provider, "executable": shutil.which(executable) or executable,
            "version": version.stdout.strip(), "help_sha256": hashlib.sha256(help_text.encode()).hexdigest(),
            "help_excerpt": help_text[:2000]}


def init_run(root: Path, skill: Path, config: Path, fixture_repo: Path) -> dict:
    root = root.expanduser().absolute()
    if root.exists():
        raise ValueError(f"run root already exists: {root}")
    skill, config, fixture_repo = skill.resolve(strict=True), config.resolve(strict=True), fixture_repo.resolve(strict=True)
    root.mkdir(parents=True, mode=0o700)
    root.chmod(0o700)
    try:
        shutil.copytree(skill, root / "skill", symlinks=False)
        shutil.copy2(config, root / "config.json")
        for item in (root / "skill").rglob("*"):
            item.chmod(0o555 if item.is_dir() else 0o444)
        (root / "skill").chmod(0o555)
        (root / "config.json").chmod(0o444)
        for name in ("messages", "evidence", "tmp"):
            (root / name).mkdir(mode=0o700)
        repo = root / "repo"
        shutil.copytree(fixture_repo, repo, symlinks=False)
        remote = call(["git", "remote"], cwd=repo)
        top = call(["git", "rev-parse", "--show-toplevel"], cwd=repo)
        head = call(["git", "rev-parse", "--verify", "HEAD"], cwd=repo)
        if (remote.returncode or remote.stdout.strip() or top.stdout.strip() != str(repo.resolve())
                or head.returncode or not head.stdout.strip()):
            raise ValueError("fixture repository must have an initial commit, correct top-level, and no remotes")
        manifest = {"format": 1, "run_id": str(uuid.uuid4()), "created_at": time.time(),
                    "root": str(root.resolve()), "skill_snapshot": str((root / "skill").resolve()),
                    "skill_sha256": digest(root / "skill"), "config_sha256": hashlib.sha256((root / "config.json").read_bytes()).hexdigest(),
                    "repo": str(repo.resolve()), "repo_initial_head": head.stdout.strip(), "provider": None,
                    "preflight": None, "session_id": None, "settings": {}, "turns": [], "smoke_receipt": None}
        atomic_text(root / "manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        return manifest
    except Exception as exc:
        if root.exists():
            (root / "preparation-error.json").write_text(json.dumps({"error": str(exc)}) + "\n", encoding="utf-8")
        raise


def adopt_run(root: Path, config: Path) -> dict:
    """Attach runner metadata to an already prepared, instrumented commit fixture."""
    root = root.expanduser().resolve(strict=True)
    root.chmod(0o700)
    if (root / "manifest.json").exists():
        raise ValueError("refusing to replace an existing run manifest")
    for required in ("repo", "skill", "events.jsonl", "fixture.json", "message.txt"):
        if not (root / required).exists():
            raise ValueError(f"prepared fixture is missing required path: {required}")
    repo = root / "repo"
    remote = call(["git", "remote"], cwd=repo)
    top = call(["git", "rev-parse", "--show-toplevel"], cwd=repo)
    head = call(["git", "rev-parse", "--verify", "HEAD"], cwd=repo)
    fixture = json.loads((root / "fixture.json").read_text(encoding="utf-8"))
    if (remote.returncode or remote.stdout.strip() or top.stdout.strip() != str(repo.resolve())
            or head.returncode or fixture.get("initial_head") != head.stdout.strip()):
        raise ValueError("prepared fixture repository must match its initial HEAD and have no remotes")
    config = config.resolve(strict=True)
    config_target = root / "config.json"
    new_paths = [root / name for name in ("messages", "evidence", "tmp")]
    existing = [target.name for target in [*new_paths, config_target] if target.exists()]
    if existing:
        raise ValueError(f"refusing to overwrite existing prepared paths: {', '.join(existing)}")
    for target in new_paths:
        target.mkdir(mode=0o700)
    shutil.copy2(config, config_target)
    config_target.chmod(0o444)
    for item in (root / "skill").rglob("*"):
        item.chmod(0o555 if item.is_dir() else 0o444)
    (root / "skill").chmod(0o555)
    manifest = {"format": 1, "run_id": str(uuid.uuid4()), "created_at": time.time(),
                "root": str(root), "skill_snapshot": str((root / "skill").resolve()),
                "skill_sha256": digest(root / "skill"),
                "config_sha256": hashlib.sha256(config_target.read_bytes()).hexdigest(),
                "repo": str(repo.resolve()), "repo_initial_head": head.stdout.strip(),
                "repo_initial_status": call(["git", "status", "--porcelain"], cwd=repo).stdout.splitlines(),
                "provider": None, "preflight": None, "session_id": None, "settings": {},
                "turns": [], "smoke_receipt": None, "adopted_fixture": True}
    atomic_text(root / "manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return manifest


def load_manifest(path: Path) -> tuple[dict, Path]:
    path = path.resolve(strict=True)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    root = path.parent.resolve()
    if root.stat().st_mode & 0o777 != 0o700:
        raise ValueError("run root must remain private (mode 0700)")
    if manifest.get("root") != str(root) or not (root / "repo").is_dir():
        raise ValueError("manifest root/repository mismatch")
    if manifest.get("repo") != str((root / "repo").resolve()):
        raise ValueError("manifest repository path mismatch")
    if digest(root / "skill") != manifest.get("skill_sha256"):
        raise ValueError("skill snapshot changed after run preparation")
    if hashlib.sha256((root / "config.json").read_bytes()).hexdigest() != manifest.get("config_sha256"):
        raise ValueError("run configuration changed after preparation")
    for name in ("repo", "messages", "evidence", "tmp"):
        if not within(root / name, root) or not (root / name).is_dir():
            raise ValueError(f"run {name} path escaped or is missing")
    remotes = call(["git", "remote"], cwd=root / "repo")
    top = call(["git", "rev-parse", "--show-toplevel"], cwd=root / "repo")
    if remotes.returncode or remotes.stdout.strip() or top.stdout.strip() != str((root / "repo").resolve()):
        raise ValueError("fixture repository remotes or top-level changed")
    head = call(["git", "rev-parse", "--verify", "HEAD"], cwd=root / "repo")
    if head.returncode or (manifest.get("turns", [])[-1:]
                           and manifest["turns"][-1]["phase"] != "commit"
                           and head.stdout.strip() != manifest.get("repo_initial_head")):
        raise ValueError("fixture repository initial state changed before commit turn")
    return manifest, root


def main(argv=None) -> int:
    contract = "macOS and Linux only. Input: arguments and message files; JSON results on stdout, diagnostics on stderr. Exit: 0 success, 2 input error, 124 timeout, 130 interrupt, 143 termination, or provider status."
    parser = argparse.ArgumentParser(description=__doc__, epilog=contract, allow_abbrev=False)
    sub = parser.add_subparsers(dest="action", required=True)
    create = sub.add_parser("init", epilog=contract, allow_abbrev=False, help="create a private run root and immutable skill/config snapshot")
    create.add_argument("--run-root", type=Path, required=True)
    create.add_argument("--skill", type=Path, required=True)
    create.add_argument("--config", type=Path, required=True)
    create.add_argument("--repo", type=Path, required=True, help="fixture repository with initial commit and no remote")
    adopt = sub.add_parser("adopt", epilog=contract, allow_abbrev=False, help="add isolated provider-run metadata to a fresh prepared commit fixture")
    adopt.add_argument("--run-root", type=Path, required=True)
    adopt.add_argument("--config", type=Path, required=True)
    check = sub.add_parser("preflight", epilog=contract, allow_abbrev=False, help="read provider version and help without starting a model")
    check.add_argument("--provider", choices=sorted(PROVIDERS), required=True)
    check.add_argument("--executable", required=True)
    invoke = sub.add_parser("turn", epilog=contract, allow_abbrev=False, help="run one bounded CLI turn in the persistent run session")
    invoke.add_argument("--manifest", type=Path, required=True)
    invoke.add_argument("--provider", choices=sorted(PROVIDERS), required=True)
    invoke.add_argument("--executable", required=True)
    invoke.add_argument("--phase", choices=("smoke", "contribution", "commit"), required=True)
    invoke.add_argument("--message-file", type=Path, required=True)
    invoke.add_argument("--timeout", type=int, default=600)
    invoke.add_argument("--setting", action="append", default=[], metavar="KEY=VALUE")
    args = parser.parse_args(argv)
    if sys.platform not in ("darwin", "linux"):
        print("eval-runner: supported platforms are macOS and Linux; use a supported host", file=sys.stderr)
        return 2
    signal.signal(signal.SIGTERM, terminate_handler)
    lock_path = None
    lock_fd = None
    try:
        if args.action == "init":
            result = init_run(args.run_root, args.skill, args.config, args.repo)
            emit_json({"run_id": result["run_id"], "manifest": str(args.run_root / "manifest.json")})
            return 0
        if args.action == "adopt":
            result = adopt_run(args.run_root, args.config)
            emit_json({"run_id": result["run_id"], "manifest": str(args.run_root / "manifest.json")})
            return 0
        if args.action == "preflight":
            if not emit_json(preflight(args.executable, args.provider)):
                return 0
            return 0
        if args.timeout < 1 or args.timeout > MAX_TIMEOUT:
            raise ValueError(f"timeout must be 1..{MAX_TIMEOUT} seconds")
        candidate_lock = args.manifest.resolve().parent / ".runner.lock"
        lock_fd = os.open(candidate_lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        lock_path = candidate_lock
        manifest, root = load_manifest(args.manifest)
        message = args.message_file.resolve(strict=True)
        if not within(message, root / "messages"):
            raise ValueError("message file must resolve inside this run's messages directory")
        settings = dict(item.split("=", 1) for item in args.setting)
        if set(settings) - {"model", "reasoning_effort", "sandbox"} or not settings.get("model"):
            raise ValueError("settings require model and may include reasoning_effort or sandbox only")
        if len(settings) != len(args.setting):
            raise ValueError("duplicate settings are not allowed")
        if settings.get("reasoning_effort") not in (None, "none", "minimal", "low", "medium", "high", "xhigh", "max"):
            raise ValueError("reasoning_effort must be none, minimal, low, medium, high, xhigh, or max")
        if settings.get("sandbox", "workspace-write") not in ("read-only", "workspace-write"):
            raise ValueError("sandbox must be read-only or workspace-write")
        if args.phase == "smoke":
            if manifest["smoke_receipt"]:
                raise ValueError("smoke receipt already exists")
            pf = preflight(args.executable, args.provider)
            manifest.update(provider=args.provider, preflight=pf, settings=settings)
            if args.provider == "copilot":
                manifest["session_id"] = str(uuid.uuid4())
        else:
            if not manifest.get("smoke_receipt"):
                raise ValueError("complete the smoke phase before contribution or commit turns")
            if manifest["provider"] != args.provider or manifest["settings"] != settings:
                raise ValueError("provider or settings changed within run")
            pf = preflight(args.executable, args.provider)
            if pf != manifest["preflight"]:
                raise ValueError("provider executable or version changed after smoke")
        if args.phase == "commit" and not any(
                turn["phase"] == "contribution" and turn["exit_code"] == 0 and not turn["timed_out"]
                for turn in manifest["turns"]):
            raise ValueError("commit turn requires a successful contribution turn in the same session")
        prompt = message.read_text(encoding="utf-8")
        if not prompt.strip():
            raise ValueError("message file is empty")
        model = settings["model"]
        executable = manifest["preflight"]["executable"]
        if args.provider == "codex":
            turn_number = len(manifest["turns"]) + 1
            output_file = str(root / "evidence" / f"{turn_number:02d}-{args.phase}-response.txt")
            if args.phase == "smoke":
                command = ["exec", "--json", "--cd", str((root / "repo").resolve()), "--add-dir", str(root),
                           "--model", model, "--sandbox", settings.get("sandbox", "workspace-write"),
                           "--output-last-message", output_file]
                if settings.get("reasoning_effort"):
                    command += ["-c", f'model_reasoning_effort="{settings["reasoning_effort"]}"']
                command += ["-"]
            else:
                command = ["exec", "resume", manifest["session_id"], "--json", "--model", model,
                           "--output-last-message", output_file]
                if settings.get("reasoning_effort"):
                    command += ["-c", f'model_reasoning_effort="{settings["reasoning_effort"]}"']
                command += ["-"]
        else:
            log_dir = root / "evidence" / "provider-logs"
            log_dir.mkdir(exist_ok=True)
            command = ["--add-dir", str(root), "--log-dir", str(log_dir), "--model", model, "--output-format", "json",
                       "--session-id", manifest["session_id"]] if args.phase == "smoke" else [
                       "--add-dir", str(root), "--log-dir", str(log_dir), "--model", model, "--output-format", "json",
                       f'--resume={manifest["session_id"]}']
            if any(char in str(root) for char in "()\n\r"):
                raise ValueError("Copilot run root cannot contain parentheses or newlines; choose another root")
            write_root = "".join({"[": "[[]", "*": "[*]", "?": "[?]"}.get(char, char) for char in str(root))
            grants = [f"write({write_root}/repo/**)", f"write({write_root}/message.txt)",
                      f"write({write_root}/outputs/**)", f"write({write_root}/messages/**)", "shell(git add:*)", "shell(git commit:*)",
                      f"shell(python3 {root}/skill/scripts/validate_message.py:*)"]
            command += [f"--allow-tool={grant}" for grant in grants]
            if settings.get("reasoning_effort"):
                command += ["--reasoning-effort", settings["reasoning_effort"]]
            command += ["--prompt", prompt]
        env = os.environ.copy()
        env["TMPDIR"] = str(root / "tmp")
        env["TMP"] = str(root / "tmp")
        env["TEMP"] = str(root / "tmp")
        env["EVAL_RUN_ROOT"] = str(root)
        env["EVAL_MESSAGE_FILE"] = str(message)
        started_at = time.time()
        interrupted = False
        try:
            process = subprocess.Popen([executable, *command], cwd=root / "repo", env=env,
                                       stdin=subprocess.PIPE if args.provider == "codex" else subprocess.DEVNULL,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                       start_new_session=True)
            try:
                stdout, stderr = process.communicate(input=prompt if args.provider == "codex" else None, timeout=args.timeout)
                result = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                stdout, stderr = process.communicate()
                result = subprocess.CompletedProcess(command, 124, stdout, stderr)
                timed_out = True
            except (KeyboardInterrupt, Terminated) as exc:
                os.killpg(process.pid, signal.SIGKILL)
                stdout, stderr = process.communicate()
                result = subprocess.CompletedProcess(command, 143 if isinstance(exc, Terminated) else 130, stdout, stderr)
                timed_out = False
                interrupted = True
            else:
                timed_out = False
        except subprocess.TimeoutExpired as exc:
            result = subprocess.CompletedProcess(command, 124, exc.stdout or "", exc.stderr or "")
            timed_out = True
        if args.provider == "codex" and args.phase == "smoke" and result.returncode == 0:
            try:
                thread = next(json.loads(line)["thread_id"] for line in result.stdout.splitlines()
                              if json.loads(line).get("type") == "thread.started")
                manifest["session_id"] = thread
            except (KeyError, StopIteration, json.JSONDecodeError):
                result = subprocess.CompletedProcess(command, 2, result.stdout, result.stderr + "\nmissing Codex thread.started session receipt")
        if args.provider == "codex" and args.phase != "smoke" and not manifest.get("session_id"):
            raise ValueError("Codex smoke did not establish a persistent session")
        record = {"phase": args.phase, "cwd": str((root / "repo").resolve()), "command": [executable, *command],
                  "session_id": manifest.get("session_id"), "started_at": started_at,
                  "finished_at": time.time(), "duration_seconds": time.time() - started_at,
                  "exit_code": result.returncode,
                  "timed_out": timed_out, "stdout": result.stdout, "stderr": result.stderr,
                  "message_file": str(message), "provider": args.provider, "settings": settings}
        turn_number = len(manifest["turns"]) + 1
        evidence_file = root / "evidence" / f"{turn_number:02d}-{args.phase}.json"
        atomic_text(evidence_file, json.dumps(record, indent=2, ensure_ascii=False) + "\n")
        manifest["turns"].append(record)
        if args.phase == "smoke" and result.returncode == 0 and not timed_out:
            manifest["smoke_receipt"] = {"provider": args.provider, "version": manifest["preflight"]["version"],
                                         "settings": settings, "session_id": manifest["session_id"],
                                         "evidence": str(evidence_file)}
        atomic_text(args.manifest.resolve(), json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        emit_json({"exit_code": result.returncode, "timed_out": timed_out,
                   "interrupted": interrupted,
                          "evidence": str(evidence_file),
                   "smoke_ready": bool(manifest["smoke_receipt"]) })
        return result.returncode if interrupted else 124 if timed_out else result.returncode
    except (OSError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        print(f"eval-runner: {exc}", file=sys.stderr)
        return 2
    except (KeyboardInterrupt, Terminated) as exc:
        print("eval-runner: interrupted", file=sys.stderr)
        return 143 if isinstance(exc, Terminated) else 130
    finally:
        if lock_fd is not None:
            os.close(lock_fd)
        if lock_path is not None:
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
