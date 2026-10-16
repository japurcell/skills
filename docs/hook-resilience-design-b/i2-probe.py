#!/usr/bin/env python3
"""Retained I2 POSIX public-process composition probe; no live installation.

Run with Python 3.13+ from any directory. Requires Git and native ps observation.
All writes and injected executables live in a TemporaryDirectory. This is retained
integration evidence, not an aggregate-suite registration or a Windows proof.
"""
import errno
import fcntl
import hashlib
import json
import os
import pty
from pathlib import Path
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
PYTHON = str(Path(sys.executable).resolve())
SECRET = "ghp_" + "A" * 36


def fingerprint(root):
    return {str(p.relative_to(root)): (p.stat().st_mode, p.stat().st_mtime_ns,
            hashlib.sha256(p.read_bytes()).hexdigest()) for p in root.rglob("*") if p.is_file()}


def exercise(base, installed):
    home = base / "private home"
    home.mkdir(parents=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SCAN_SECRETS_", "PYTHON", "XDG_"))}
    env.update(HOME=str(home), USERPROFILE=str(home), APPDATA=str(home / "roaming"),
        LOCALAPPDATA=str(home / "local"), XDG_DATA_HOME=str(home / "data"),
        XDG_CONFIG_HOME=str(home / "config"), XDG_CACHE_HOME=str(home / "cache"),
        GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    env.pop("CODEX_HOME", None)
    source = base / "copied source"
    shutil.copytree(ROOT / "hooks/runtime", source / "hooks/runtime", ignore=shutil.ignore_patterns("__pycache__"))
    (source / "scripts").mkdir()
    shutil.copy2(ROOT / "scripts/scan-secrets.py", source / "scripts/scan-secrets.py")
    shutil.copy2(ROOT / "scripts/scan_install_windows.py", source / "scripts/scan_install_windows.py")
    entry = source / "scripts/scan-secrets.py"
    command = [PYTHON, "-I", "-S", "-B", str(entry)]

    def run(*args, code=0, command_override=None, environment=None, **kwargs):
        result = subprocess.run([*(command_override or command), *args], cwd=base,
            env=environment or env, capture_output=True, text=True, timeout=10, **kwargs)
        assert result.returncode == code, (result.returncode, code, result.stdout, result.stderr)
        assert SECRET not in result.stdout + result.stderr
        assert "Traceback" not in result.stderr and "Exception ignored" not in result.stderr
        assert "\x1b" not in result.stdout + result.stderr
        return result

    if installed:
        destination = base / "installed runtime"
        run("install", "--source-dir", str(source), "--destination", str(destination), "--json",
            command_override=[PYTHON, "-I", "-S", "-B", str(ROOT / "scripts/install-scan-secrets.py")])
        manifest = json.loads((destination / "installation.json").read_text())
        assert len(manifest["files"]) == 13 and manifest["interpreter"] == PYTHON
        for relative, expected_hash in manifest["files"].items():
            assert hashlib.sha256((destination / relative).read_bytes()).hexdigest() == expected_hash
            assert hashlib.sha256((source / relative).read_bytes()).hexdigest() == expected_hash
        entry = destination / "scripts/scan-secrets.py"
        command = [str(destination / "scan-secrets")]
        shutil.rmtree(source)
        assert not source.exists()
    runtime = entry.parent.parent / "hooks/runtime"
    bundle_before = fingerprint(entry.parent.parent)
    repo = base / "repository with spaces"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], env=env, check=True)
    content = repo / "notes.txt"
    content.write_text("ordinary notes\n")
    common = ["--repo", str(repo), "--json", "--quiet", "--no-input", "--no-color"]

    def value(action, code=0, **kwargs):
        result = run(action, *common, code=code, **kwargs)
        parsed = json.loads(result.stdout)
        assert parsed["schema"] == "scan_secrets_" + ("check" if action == "check" else "status") + "_v1"
        return parsed

    def historical():
        result = value("status")
        assert result["historical"] is True and result["authorizes_publication"] is False
        return result

    for args in ((), ("--help",), ("--version",), ("help", "check"), ("status", "--help")):
        assert run(*args).stderr == ""
    parser = run("check", "--repo", str(repo), "--js", SECRET, "--json", code=3)
    assert json.loads(parser.stdout)["reason"] == "invalid_arguments"
    assert historical()["outcome"] == "not_scanned"
    outside = run("status", "--repo", str(home), "--json")
    assert json.loads(outside.stdout)["reason"] == "not_repository"
    assert json.loads(run("check", "--repo", str(home), "--json", code=3).stdout)["reason"] == "not_repository"
    clean = value("check")
    assert clean["outcome"] == "complete_clean" and clean["audit_outcome"] == "written"
    old = historical()
    report = next((home / "data/scan-secrets/status").glob("*.json"))
    report_before = report.read_bytes()
    content.write_text("token = " + SECRET + "\n")
    assert historical() == old and report.read_bytes() == report_before

    # Natural filesystem failure at the public storage seam, no product mocks.
    with report.with_name(report.name + ".lock").open("rb") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        finding = value("check", 1)
    assert finding["outcome"] == "complete_findings" and finding["security_outcome"] == "findings"
    assert finding["status_outcome"] == "failed" and finding["status_reason"] == "status_timeout"
    assert finding["audit_outcome"] == "written" and finding["coverage_complete"] is True
    assert historical() == old and report.read_bytes() == report_before
    fresh = value("check", 1)
    assert fresh["status_outcome"] == "written" and historical()["last_scan"]["outcome"] == "complete_findings"
    assert report.read_bytes() != report_before
    audit = home / "data/scan-secrets/audit.jsonl"
    audit.rename(audit.with_suffix(".saved"))
    audit.mkdir()
    try:
        incomplete = value("check", 2)
        assert incomplete["outcome"] == "incomplete" and incomplete["audit_outcome"] == "failed"
        assert incomplete["security_outcome"] == "findings" and incomplete["coverage_complete"] is True
        assert incomplete["counts"]["processed_findings"] > 0 and incomplete["findings"]
        assert incomplete["status_outcome"] == "written"
        last = historical()["last_scan"]
        assert last["outcome"] == "incomplete" and last["security_outcome"] == "findings"
    finally:
        audit.rmdir()
        audit.with_suffix(".saved").rename(audit)
    report.chmod(0)
    try:
        assert value("status", 2)["outcome"] == "unavailable"
    finally:
        report.chmod(0o600)

    # Actual installed/source entry still reads history with detectors absent.
    removed = {}
    for module in runtime.glob("*.py"):
        if module.name not in {"scan_cli.py", "scan_status.py", "scan_native_file.py"}:
            removed[module] = (module.read_bytes(), module.stat().st_mode & 0o777)
            module.unlink()
    expected = historical()
    wrapper = base / "readonly sentinel.py"
    wrapper.write_text("import os,sys,runpy\n" + r'''
def guard(event,args):
 if event in {"subprocess.Popen","os.system","socket.__new__","socket.connect","os.mkdir","os.rename","os.remove","os.chmod"}:
  raise RuntimeError("forbidden side effect")
 if event in {"os.listdir","os.scandir"} and str(args[0]).startswith((os.environ["I2_REPO"],os.environ["XDG_DATA_HOME"])):
  raise RuntimeError("forbidden enumeration")
 if event == "open":
  path,mode,flags=args
  if flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND) or str(path).endswith(("/index","/config","/notes.txt")):
   raise RuntimeError("forbidden open")
sys.addaudithook(guard)
if os.environ.get("I2_NEGATIVE"):
 try: os.mkdir(os.environ["I2_REPO"] + "/forbidden-new-directory")
 except RuntimeError: sys.exit(91)
 sys.exit(92)
''' + f"\nsys.argv[0]={str(entry)!r}\nrunpy.run_path({str(entry)!r},run_name='__main__')\n")
    run("status", *common, code=91, command_override=[PYTHON,"-I","-S","-B",str(wrapper)],
        environment={**env, "I2_REPO": str(repo), "I2_NEGATIVE": "1"})
    assert not (repo / "forbidden-new-directory").exists()
    data_before = fingerprint(home)
    guarded = value("status", command_override=[PYTHON,"-I","-S","-B",str(wrapper)],
        environment={**env, "I2_REPO": str(repo)})
    assert guarded == expected and fingerprint(home) == data_before
    for path, (data, mode) in removed.items():
        path.write_bytes(data)
        path.chmod(mode)
    # Preserve observed content/mode hashes; mtimes change only in this deliberate fixture.
    assert {k:(v[0],v[2]) for k,v in fingerprint(entry.parent.parent).items()} == {k:(v[0],v[2]) for k,v in bundle_before.items()}

    # Check with caller stdin deliberately kept open must finish without consuming it.
    read_fd, write_fd = os.pipe()
    try:
        os.write(write_fd, b"caller input\n")
        result = run("check", *common, code=1, stdin=read_fd)
        os.set_blocking(read_fd, False)
        assert os.read(read_fd, 100) == b"caller input\n"
    finally:
        os.close(read_fd)
        os.close(write_fd)
    # Real terminal stdin/stdout, held open with no response: JSON/no-input
    # must finish without prompting, and terminal output must remain parseable.
    master, slave = pty.openpty()
    terminal = None
    try:
        terminal = subprocess.Popen([*command, "check", *common], env={**env, "NO_COLOR": "1", "TERM": "dumb"},
            cwd=base, stdin=slave, stdout=slave, stderr=subprocess.PIPE)
        os.close(slave)
        slave = None
        deadline = time.monotonic() + 5
        blocks = []
        while True:
            assert time.monotonic() < deadline, "terminal command did not finish without input"
            if not select.select([master], [], [], 0.1)[0]:
                continue
            try:
                block = os.read(master, 65536)
            except OSError as error:
                if error.errno != errno.EIO:
                    raise
                break
            if not block:
                break
            blocks.append(block)
        _, terminal_stderr = terminal.communicate(timeout=1)
        assert terminal.returncode == 1 and terminal_stderr == b""
        terminal_output = b"".join(blocks)
        assert json.loads(terminal_output)["outcome"] == "complete_findings"
        assert SECRET.encode() not in terminal_output and b"\x1b" not in terminal_output
    finally:
        if terminal is not None:
            if terminal.poll() is None:
                terminal.kill()
            terminal.communicate(timeout=3)
        if slave is not None:
            os.close(slave)
        os.close(master)
    for args in (("--help",), ("check", *common), ("status", *common)):
        read_fd, write_fd = os.pipe()
        os.close(read_fd)
        try:
            result = subprocess.run([*command,*args], env=env, cwd=base, stdout=write_fd,
                stderr=subprocess.PIPE, timeout=5)
            assert result.returncode != 0 and b"Traceback" not in result.stderr
        finally:
            os.close(write_fd)

    # Capture's real executable process boundary: a separate Git process group
    # with a descendant that ignores graceful termination and inherits pipes.
    binary = base / "private bin"
    binary.mkdir()
    marker, ready = base / "git-process.json", base / "descendant-ready"
    child_code = ("import os,signal,time;from pathlib import Path;"
        "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
        f"Path({str(ready)!r}).touch();time.sleep(60)")
    fake_git = binary / "git"
    fake_git.write_text(f"#!{PYTHON}\nimport json,os,subprocess,time\nfrom pathlib import Path\n"
        f"child=subprocess.Popen([{PYTHON!r},'-I','-S','-B','-c',{child_code!r}])\n"
        f"while not Path({str(ready)!r}).exists(): time.sleep(.01)\n"
        f"Path({str(marker)!r}).write_text(json.dumps(dict(pid=os.getpid(),child=child.pid,group=os.getpgrp(),session=os.getsid(0))))\n"
        "time.sleep(60)\n")
    fake_git.chmod(0o755)
    process = subprocess.Popen([*command,"check",*common], env={**env,"PATH":str(binary)+os.pathsep+env["PATH"]},
        cwd=base, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    details = None
    started = time.monotonic()
    try:
        deadline = started + 4
        while not marker.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(.01)
        assert marker.exists(), "real capture did not launch Git fixture"
        details = json.loads(marker.read_text())
        assert details["group"] == details["session"] == details["pid"]
        assert process.pid != details["pid"]
        process.send_signal(signal.SIGINT)
        stdout, stderr = process.communicate(timeout=4)  # EOF requires descendant pipe closure.
        assert process.returncode == 130 and json.loads(stdout)["reason"] == "cancelled", (stdout,stderr)
        assert b"Traceback" not in stderr and SECRET.encode() not in stdout + stderr
        cancel_states = {}
        for role, pid in (("root", details["pid"]), ("descendant", details["child"])):
            observed = subprocess.run(["ps","-o","stat=","-p",str(pid)], capture_output=True, timeout=2, check=False)
            assert observed.returncode in (0,1), observed.stderr
            assert not observed.stdout.strip() or observed.stdout.lstrip().startswith(b"Z"), observed.stdout
            cancel_states[role] = observed.stdout.strip().decode() or "absent"
        last = historical()["last_scan"]
        assert last["outcome"] == "incomplete" and last["reason"] == "cancelled"
    finally:
        # Cleanup cannot make any of the assertions above pass.
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=4)
        if details:
            for pid in (details["pid"],details["child"]):
                try:
                    os.kill(pid,signal.SIGKILL)
                except ProcessLookupError:
                    pass
    assert not list(entry.parent.parent.rglob("__pycache__"))
    return {"mode": "installed" if installed else "source_copy", "history": "historical_only",
        "display_failure": finding["status_reason"], "audit_failure": incomplete["outcome"],
        "cancel_root_and_descendant": "terminated", "cancel_process_states": cancel_states, "cancel_seconds": round(time.monotonic()-started,3),
        "runtime_assets": 13 if installed else "copied canonical runtime"}


def main():
    assert os.name == "posix", "POSIX composition proof; native Windows requires its own run"
    with tempfile.TemporaryDirectory(prefix="i2 composed proof ") as directory:
        base = Path(directory).resolve()
        results = [exercise(base / name, installed) for name,installed in (("source",False),("installed",True))]
        print(json.dumps({"python": sys.version.split()[0], "results": results},sort_keys=True))


if __name__ == "__main__":
    main()
