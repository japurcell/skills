#!/usr/bin/env python3
"""Run the ablation experiment. The agent calls this; the user watches.

Executes the same probe task N times with the AI layer intact and N times with it
stripped, in throwaway git worktrees, and collects the resulting diffs for grading.

Two properties make this safe to run unattended:

  * Your working tree is never modified. Every run happens in a detached worktree
    created from HEAD in a temp directory and deleted afterwards. Nothing is moved
    aside, so there is no restore step that can fail and leave you stripped.
  * Worktrees live OUTSIDE the repo. An agent started inside the repo would walk
    up and find the very CLAUDE.md this script just removed.

Why N runs per arm rather than one: agent runs are nondeterministic. A single
control-vs-stripped pair is a point estimate, and two runs of the SAME arm can
differ more than the two arms differ. Only a rule that behaves consistently across
runs is evidence of anything.

Usage:
  python run_ablation.py <repo> --task-file task.md
  python run_ablation.py <repo> --task-file task.md --runs 3 --scope all
  python run_ablation.py <repo> --task-file task.md --dry-run
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import threading
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from map_layer import ALWAYS, ONDEMAND, iter_matches  # noqa: E402

CONTROL, STRIPPED = "control", "stripped"
CANCELLED = threading.Event()
WORKTREE_LOCK = threading.Lock()


class ShutdownUnconfirmed(RuntimeError):
    """Runner ownership cannot yet be released safely."""


def group_exists(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # Some sandboxed hosts deny signal probes even after the group has gone.
        # A read-only process table can establish absence without sending signals.
        result = subprocess.run(["ps", "-axo", "pgid="], capture_output=True,
                                text=True, check=True, timeout=2)
        return pgid in {int(value) for value in result.stdout.split()}


def stop_group(process: subprocess.Popen) -> None:
    """Stop and verify the session group, even if its original leader exited."""
    for sig, grace in ((signal.SIGTERM, 0.5), (signal.SIGKILL, 2)):
        process.poll()
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            process.wait()
            return
        except PermissionError:
            if group_exists(process.pid):
                raise
            process.wait()
            return
        deadline = time.monotonic() + grace
        while time.monotonic() < deadline:
            process.poll()
            if not group_exists(process.pid):
                process.wait()
                return
            time.sleep(0.02)
    raise ShutdownUnconfirmed(f"process group {process.pid} still exists; worktree retained")


def run_agent(cmd, use_shell, wt, prompt, timeout, stdout_path, stderr_path):
    # Files avoid waiting for pipe EOF from descendants after the leader exits.
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        process = subprocess.Popen(
            cmd, cwd=str(wt), stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
            text=True, encoding="utf-8", errors="replace", shell=use_shell,
            start_new_session=True)
        try:
            deadline = time.monotonic() + timeout
            pending_input = prompt
            while True:
                if CANCELLED.is_set():
                    raise RuntimeError("cancelled")
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(cmd, timeout)
                try:
                    process.communicate(input=pending_input, timeout=min(0.1, remaining))
                    break
                except subprocess.TimeoutExpired:
                    pending_input = None
        finally:
            try:
                stop_group(process)
            except (OSError, subprocess.SubprocessError, ValueError) as error:
                raise ShutdownUnconfirmed(
                    f"cannot verify process group {process.pid}: {error}; worktree retained") from error
        return process.returncode


def stream_metadata(rec, stdout_path, stderr_path):
    """Decode previews only; raw artifacts remain the authoritative evidence."""
    stdout = stdout_path.read_bytes()
    stderr = stderr_path.read_bytes()
    rec.update(stdout_path=str(stdout_path), stderr_path=str(stderr_path),
               stdout_bytes=len(stdout), stderr_bytes=len(stderr))
    text = stdout.decode("utf-8", errors="replace")
    error_text = stderr.decode("utf-8", errors="replace")
    rec["agent_error"] = rec.get("exit_code", 1) != 0
    try:
        payload = json.loads(text)
    except (ValueError, RecursionError):
        payload = None
    if isinstance(payload, dict):
        if isinstance(payload.get("is_error"), bool):
            rec["agent_error"] |= payload["is_error"]
        if isinstance(payload.get("result"), str):
            text = payload["result"]
        for source, target, kind in (("total_cost_usd", "cost_usd", (int, float)),
                                     ("num_turns", "num_turns", (int,))):
            value = payload.get(source)
            if type(value) in kind and (not isinstance(value, float) or math.isfinite(value)):
                rec[target] = value
        usage = payload.get("usage")
        if isinstance(usage, dict) and type(usage.get("output_tokens")) is int:
            rec["output_tokens"] = usage["output_tokens"]
    rec.update(result_text=text[:4000], result_text_truncated=len(text) > 4000,
               stderr_tail=error_text[-600:], stderr_tail_truncated=len(error_text) > 600)


# ---------------------------------------------------------------- git plumbing

def git(args: list[str], cwd: Path, check: bool = True) -> str:
    p = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout


def repo_root(start: Path) -> Path:
    out = git(["rev-parse", "--show-toplevel"], start).strip()
    return Path(out).resolve()


def head_sha(root: Path) -> str:
    return git(["rev-parse", "HEAD"], root).strip()


def is_dirty(root: Path) -> bool:
    return bool(git(["status", "--porcelain"], root).strip())


# ---------------------------------------------------------------- the layer

def layer_targets(root: Path, scope: str) -> list[dict]:
    """The artifacts the stripped arm removes. Enforcement is never touched:
    hooks and permissions run as code and spend no attention budget, so removing
    them would change mechanics rather than the variable under test."""
    kinds = {ALWAYS} if scope == "always" else {ALWAYS, ONDEMAND}
    return [i for i in iter_matches(root) if i["kind"] in kinds]


SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".rb",
                   ".java", ".kt", ".cs", ".php", ".swift", ".toml", ".json"}
SKIP = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__",
        ".next", "target", ".ablation"}


def build_dependencies(root: Path, targets: list[dict]) -> list[str]:
    """Does the repo's own source read its AI layer? A CLI that imports its skill
    markdown at build time breaks the moment those files go missing, and the user
    reads a compile error as an agent regression."""
    names = {Path(t["path"]).name for t in targets}
    names |= {t["path"] for t in targets}
    hits = []
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix not in SOURCE_SUFFIXES:
            continue
        if any(part in SKIP for part in p.parts):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for n in names:
            if n in text:
                hits.append(f"{p.relative_to(root).as_posix()} references {n}")
                break
    return hits


# ---------------------------------------------------------------- one run

def build_command(model: str | None, runner: str | None) -> tuple[list[str] | str, bool]:
    """Returns (command, use_shell). The prompt always arrives on stdin, never in
    argv: Windows caps a command line at 32,767 chars and a real probe task plus
    its context blows through that as a misleading 'file not found'."""
    if runner:
        return runner, True
    exe = shutil.which("claude")
    if not exe:
        raise RuntimeError(
            "`claude` is not on PATH. Install Claude Code, or pass --runner with the "
            "headless command for your agent (it must read the prompt on stdin).")
    cmd = [exe, "-p", "--output-format", "json", "--permission-mode", "acceptEdits"]
    if model:
        cmd += ["--model", model]
    return cmd, False


def run_one(root: Path, sha: str, arm: str, index: int, prompt: str,
            targets: list[dict], model: str | None, runner: str | None,
            timeout: int, keep: bool, out: Path) -> dict:
    """One worktree, one agent session, one diff. Fresh worktree per run so runs
    never compound on each other."""
    tmp = Path(tempfile.mkdtemp(prefix=f"ablate-{arm}-{index}-"))
    wt = tmp / "repo"
    rec: dict = {"arm": arm, "index": index, "removed": [], "ok": False}
    started = time.time()
    stdout_path = out / f"{arm}-{index}.stdout"
    stderr_path = out / f"{arm}-{index}.stderr"
    shutdown_confirmed = True
    created = False
    try:
        stdout_path.write_bytes(b"")
        stderr_path.write_bytes(b"")
        if CANCELLED.is_set():
            rec["note"] = "cancelled before launch"
            return rec
        with WORKTREE_LOCK:
            git(["worktree", "add", "--detach", "--quiet", str(wt), sha], root)
            created = True

        if arm == STRIPPED:
            for t in targets:
                f = wt / t["path"]
                if f.exists():
                    if not f.resolve().is_relative_to(wt.resolve()):
                        raise RuntimeError(f"instruction target escapes worktree: {t['path']}")
                    f.unlink()
                    rec["removed"].append(t["path"])
            # Drop directories left empty, so nothing looks half-present.
            for t in sorted({str(Path(t["path"]).parent) for t in targets}, reverse=True):
                d = wt / t
                try:
                    if d.is_dir() and not any(d.iterdir()):
                        d.rmdir()
                except OSError:
                    pass

        # Measure only agent work, including any commits it makes, against setup.
        git(["add", "-A"], wt)
        baseline = git(["write-tree"], wt).strip()

        cmd, use_shell = build_command(model, runner)
        rec["exit_code"] = run_agent(cmd, use_shell, wt, prompt, timeout,
                                     stdout_path, stderr_path)
        stream_metadata(rec, stdout_path, stderr_path)

        git(["add", "-A"], wt)
        rec["diff"] = git(["diff", "--cached", baseline], wt)
        rec["files_changed"] = [
            l for l in git(["diff", "--cached", "--name-only", baseline], wt).splitlines() if l]
        rec["ok"] = not rec.get("agent_error") and bool(rec["diff"].strip())
        if not rec["diff"].strip():
            rec["note"] = "agent produced no file changes"
    except ShutdownUnconfirmed as exc:
        shutdown_confirmed = False
        rec["note"] = str(exc)
    except subprocess.TimeoutExpired:
        rec["note"] = f"timed out after {timeout}s"
    except Exception as exc:  # a broken run must not sink the other five
        rec["note"] = f"{type(exc).__name__}: {exc}"
    finally:
        try:
            stream_metadata(rec, stdout_path, stderr_path)
        except OSError as error:
            rec["ok"] = False
            rec["note"] = f"{rec.get('note', '')}; stream metadata failed: {error}".lstrip("; ")
        rec["shutdown_confirmed"] = shutdown_confirmed
        rec["duration_s"] = round(time.time() - started, 1)
        if (keep and created) or not shutdown_confirmed:
            rec["worktree_kept"] = str(wt)
            rec["cleanup_status"] = "retained"
        else:
            try:
                with WORKTREE_LOCK:
                    if wt.exists():
                        git(["worktree", "remove", "--force", str(wt)], root)
                    shutil.rmtree(tmp)
                rec["cleanup_status"] = "removed" if created else "not_created"
            except (OSError, RuntimeError) as error:
                rec["ok"] = False
                rec["cleanup_status"] = "failed"
                rec["worktree_kept"] = str(wt)
                rec["note"] = f"{rec.get('note', '')}; cleanup failed: {error}".lstrip("; ")
    return rec


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Run the control and stripped arms of an AI-layer ablation.",
        allow_abbrev=False,
        epilog="Execution requires POSIX process groups (macOS/Linux or WSL). "
               "Runners must keep descendants in their process group. On timeout or cancellation, "
               "the group is stopped before worktree cleanup; unconfirmed shutdown retains the worktree. "
               "Exit codes: 0 completed comparison, 1 unusable experiment, 2 usage/platform error, "
               "130 interrupt, 143 termination. Results are written under --out; progress goes to stdout.")
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--task-file", required=True,
                    help="file holding the probe-task prompt, reused verbatim by every run")
    ap.add_argument("--runs", type=int, default=2, help="runs PER ARM (default 2)")
    ap.add_argument("--scope", choices=["always", "all"], default="always")
    ap.add_argument("--model", default=None)
    ap.add_argument("--jobs", type=int, default=2, help="concurrent runs (default 2)")
    ap.add_argument("--timeout", type=int, default=1800, help="seconds per run")
    ap.add_argument("--runner", default=None,
                    help="shell command for a non-Claude agent; must read the prompt on stdin")
    ap.add_argument("--out", default=None)
    ap.add_argument("--keep-worktrees", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, run nothing")
    args = ap.parse_args()
    if args.runs < 1 or args.jobs < 1 or args.timeout < 1:
        ap.error("--runs, --jobs, and --timeout must be positive")

    try:
        root = repo_root(Path(args.repo).resolve())
    except Exception:
        print(f"Not a git repository: {Path(args.repo).resolve()}", file=sys.stderr)
        print("Ablation needs git: the experiment runs in worktrees.", file=sys.stderr)
        return 2

    try:
        prompt = Path(args.task_file).read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError) as error:
        ap.error(f"cannot read task file {args.task_file}: {error}")
    if not prompt:
        print("The task file is empty. The probe task decides whether this experiment "
              "can detect anything; it cannot be blank.", file=sys.stderr)
        return 2

    targets = layer_targets(root, args.scope)
    if not targets:
        print(f"No {args.scope}-scope AI layer artifacts under {root}.")
        print("Nothing to ablate, so there is nothing to test.")
        return 1

    sha = head_sha(root)
    print(f"repo    {root}")
    print(f"base    {sha[:12]}" + ("   (WORKING TREE IS DIRTY: worktrees are built from "
                                   "HEAD, so uncommitted edits are NOT under test)"
                                   if is_dirty(root) else ""))
    print(f"scope   {args.scope} ({len(targets)} files stripped in the stripped arm)")
    for t in targets[:12]:
        print(f"          - {t['path']}")
    if len(targets) > 12:
        print(f"          ... and {len(targets) - 12} more")

    deps = build_dependencies(root, targets)
    if deps:
        print("\nBUILD DEPENDENCY WARNING - this repo's own source reads its AI layer:")
        for d in deps[:5]:
            print(f"          {d}")
        print("        The stripped arm may fail to build. That is a broken experiment,")
        print("        not an agent regression. Consider --scope always.")

    total = args.runs * 2
    print(f"\nplan    {args.runs} control + {args.runs} stripped = {total} agent runs, "
          f"{args.jobs} at a time")
    print(f"        model {args.model or '(session default)'}, timeout {args.timeout}s each")
    print("        your working tree is never touched; every run is a throwaway worktree")
    if args.dry_run:
        print("\n--dry-run: nothing executed.")
        return 0

    if os.name != "posix":
        print("Agent execution requires POSIX process groups (macOS/Linux or WSL). "
              "Mapping and --dry-run remain available.", file=sys.stderr)
        return 2

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = (Path(args.out) if args.out else root / ".ablation" / stamp).resolve()
    out.mkdir(parents=True, exist_ok=True)

    jobs = [(arm, i) for arm in (CONTROL, STRIPPED) for i in range(1, args.runs + 1)]
    print(f"\nrunning {total} sessions, writing to {out}\n")
    records: list[dict] = []
    cancelled_signal = 0

    def cancel(signum, frame):
        nonlocal cancelled_signal
        cancelled_signal = signum
        CANCELLED.set()

    handlers = {sig: signal.signal(sig, cancel) for sig in (signal.SIGINT, signal.SIGTERM)}
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
            futures = {
                pool.submit(run_one, root, sha, arm, i, prompt, targets,
                            args.model, args.runner, args.timeout, args.keep_worktrees, out): (arm, i)
                for arm, i in jobs
            }
            for fut in concurrent.futures.as_completed(futures):
                arm, i = futures[fut]
                rec = fut.result()
                records.append(rec)
                mark = "ok " if rec["ok"] else "!! "
                print(f"  {mark} {arm}/{i}  {rec['duration_s']}s  "
                      f"{len(rec.get('files_changed') or [])} files  {rec.get('note', '')}")
    finally:
        for sig, handler in handlers.items():
            signal.signal(sig, handler)

    records.sort(key=lambda r: (r["arm"], r["index"]))
    for rec in records:
        if rec.get("diff"):
            (out / f"{rec['arm']}-{rec['index']}.diff").write_text(rec["diff"], encoding="utf-8")

    summary = {
        "repo": str(root), "base_sha": sha, "scope": args.scope,
        "runs_per_arm": args.runs, "model": args.model,
        "prompt": prompt, "stripped_files": [t["path"] for t in targets],
        "build_dependency_warnings": deps,
        "runs": [{k: v for k, v in r.items() if k != "diff"} for r in records],
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out / "task.md").write_text(prompt, encoding="utf-8")

    good = [r for r in records if r["ok"]]
    costs = [r.get("cost_usd") for r in records if isinstance(r.get("cost_usd"), (int, float))]
    print(f"\n{len(good)}/{total} runs produced changes")
    if costs:
        print(f"cost    ${sum(costs):.2f} across {len(costs)} runs")
    print(f"results {out}")

    if cancelled_signal:
        return 128 + cancelled_signal

    by_arm = {a: [r for r in good if r["arm"] == a] for a in (CONTROL, STRIPPED)}
    if not by_arm[CONTROL] or not by_arm[STRIPPED]:
        print("\nAt least one arm produced nothing usable. Do not grade this: an empty "
              "arm is a broken experiment, not a finding. Check stderr_tail in "
              "summary.json, then re-run.")
        return 1
    if len(good) < total:
        print("\nSome runs failed. Grade only the arms that completed, and say so in "
              "the report: unequal run counts weaken every comparison drawn from them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
