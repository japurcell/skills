#!/usr/bin/env python3
"""Disposable registered-tool I4 proof. Imports test adapters, no product modules."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

GIT = "/Library/Developer/CommandLineTools/usr/bin/git"
OLD = "0bf18e9764b9a2e00763e089af2c41a7710f6141"
MERGE = ("e5c2be2095ba30626559adae7fb2c49ba691734e", "5f3948c92e5037fb066321e9c9e5b03419410671")
SIZES = (3611602, 3131324, 2495842, 3340075, 3319151, 4128480)
BUILD = "82e125f8e74728baf01a0e1d792d4ec131f9a309d90b861b16287482dde9b029"
CONFIGS = {"codex": ".codex/hooks.json", "copilot": ".copilot/hooks/hooks.json", "gemini": ".gemini/settings.json"}
EVENTS = {"codex": ("PreToolUse", "Stop"), "copilot": ("preToolUse", "agentStop"), "gemini": ("BeforeTool", "AfterAgent")}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def fake():
    return b"gh" + b"p_" + b"A" * 36


def fingerprint(source):
    paths = set()
    for name in ("hooks", ".codex/hooks", ".copilot/hooks", ".gemini/hooks"):
        paths.update(p for p in (source / name).rglob("*") if p.is_file() and "__pycache__" not in p.parts and "logs" not in p.parts)
    paths.update(p for p in (source / "scripts").iterdir() if p.suffix in {".py", ".sh", ".ps1"})
    paths.update(source / name for name in (".codex/global-hooks.json", ".gemini/global-settings.json"))
    return {str(p.relative_to(source)): {"sha256": sha(p.read_bytes()), "mode": oct(p.stat().st_mode & 0o777)} for p in sorted(paths)}


class Lab:
    def __init__(self, root, source):
        self.root, self.source = root.resolve(), source.resolve()
        self.home, self.repo = self.root / "home", self.root / "repo"
        self.home.mkdir(); self.repo.mkdir()
        self.logs = self.root / "logs"; self.logs.mkdir()
        temporary = self.root / "temporary"; temporary.mkdir()
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "PYTHON", "SCAN_", "TOOL_GUARD", "GUARD_", "OBSERVABILITY", "COPILOT_", "GEMINI_"))}
        self.env.update(HOME=str(self.home), USERPROFILE=str(self.home), CODEX_HOME=str(self.home / ".codex"),
            XDG_CONFIG_HOME=str(self.root / "config"), XDG_DATA_HOME=str(self.root / "data"), XDG_CACHE_HOME=str(self.root / "cache"),
            APPDATA=str(self.root / "appdata"), LOCALAPPDATA=str(self.root / "local"), TMPDIR=str(temporary),
            PATH=str(Path(sys.executable).parent) + ":/Library/Developer/CommandLineTools/usr/bin:" + os.environ["PATH"],
            GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0", GIT_NO_LAZY_FETCH="1",
            OBSERVABILITY_DISABLE="1", OBSERVABILITY_LOG_PATH=str(self.logs / "observability.jsonl"),
            AUDIT_LOG=str(self.logs / "audit.jsonl"), TOOL_GUARD_LOG_DIR=str(self.logs / "guardian"), GUARD_MODE="block")
        self.calls = []
        self.dispatches = []
        self.git("init", "-qb", "main", str(self.repo), cwd=self.root)
        for key, value in (("user.name", "I4 fixture"), ("user.email", "i4@example.invalid"),
                           ("commit.gpgsign", "false"), ("gc.auto", "0"), ("maintenance.auto", "false")):
            self.git("config", key, value)

    def run(self, command, *, data=None, cwd=None, expected=0, env=None, timeout=180):
        started = time.monotonic()
        result = subprocess.run(command, input=data, capture_output=True, cwd=cwd or self.repo, env=env or self.env, timeout=timeout)
        assert fake() not in result.stdout + result.stderr, "synthetic credential leaked"
        receipt = {"argv": command, "exit": result.returncode, "seconds": time.monotonic() - started,
                   "stdout_bytes": len(result.stdout), "stdout_sha256": sha(result.stdout),
                   "stderr_bytes": len(result.stderr), "stderr_sha256": sha(result.stderr)}
        self.calls.append(receipt)
        if expected is not None:
            assert result.returncode == expected, (receipt, result.stdout[:2000], result.stderr[:2000])
        return result

    def git(self, *args, **kw):
        return self.run([GIT, "-c", "user.name=I4 fixture", "-c", "user.email=i4@example.invalid", "-c", "commit.gpgsign=false", *args], **kw)

    def cli(self, *args, expected=0):
        result = self.run([sys.executable, "-I", "-S", "-B", str(self.cli_path), *args, "--repo", str(self.repo), "--json", "--no-input"], expected=expected)
        value = json.loads(result.stdout)
        if value.get("schema") == "scan_secrets_check_v1":
            assert value["build"] == BUILD
        return value

    def setup(self):
        old = self.root / "old-source"; old.mkdir()
        archive = self.run([GIT, "-C", str(self.source), "archive", OLD, ".codex", ".copilot", ".gemini"], cwd=self.root).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
            bundle.extractall(old, filter="data")
        for name in (".codex/hooks", ".copilot/hooks", ".gemini/hooks"):
            shutil.copytree(old / name, self.home / name)
        provenance = json.loads((self.source / "scripts/fixtures/provider-hooks-pre-status/provenance.json").read_bytes())
        for provider, name in CONFIGS.items():
            raw = (self.source / f"scripts/fixtures/provider-hooks-pre-status/{provider}.json").read_bytes()
            assert sha(raw) == provenance[provider]["sha256"]
            config = json.loads(raw)
            config["i4UserSetting"] = {"nested": {"keep": True}}
            (self.home / name).parent.mkdir(parents=True, exist_ok=True)
            (self.home / name).write_text(json.dumps(config))
        release = self.source / "scripts/fixtures/scan-secrets-releases/t6.tar.gz"
        assert sha(release.read_bytes()) == "04d1d01ca62b0d6ac0e1a6cf7c8b72c8315c867e515a11b62ba4dba1d3191258"
        with tarfile.open(release) as bundle:
            bundle.extractall(old, filter="data")
        legacy = self.run([sys.executable, "-I", "-S", "-B", str(old / "scripts/install-scan-secrets.py"), "install", "--source-dir", str(old), "--json"], cwd=self.root)
        old_assets = {str(p.relative_to(self.home)): {"sha256": sha(p.read_bytes()), "mode": oct(p.stat().st_mode & 0o777)}
            for name in (".codex/hooks", ".copilot/hooks", ".gemini/hooks") for p in sorted((self.home / name).rglob("*.py"))}
        shutil.rmtree(old)
        current = self.root / "current-source"; current.mkdir()
        for name in ("hooks", ".codex", ".copilot", ".gemini", ".github"):
            shutil.copytree(self.source / name, current / name, ignore=shutil.ignore_patterns("__pycache__", "logs"))
        (current / "scripts").mkdir()
        for path in (self.source / "scripts").iterdir():
            if path.suffix in {".py", ".sh", ".ps1"}:
                shutil.copy2(path, current / "scripts" / path.name)
        for name in ("skills/default/fixture", "skills/forest-service", "references", "agents"):
            (current / name).mkdir(parents=True)
        (current / "skills/default/fixture/SKILL.md").write_text("---\nname: fixture\n---\nFixture.\n")
        (current / "agents/fixture.md").write_text("---\nname: fixture\ndescription: Test fixture.\n---\nFixture.\n")
        self.run(["bash", str(current / "scripts/install.sh")], cwd=self.root)
        self.config = {provider: json.loads((self.home / name).read_bytes()) for provider, name in CONFIGS.items()}
        for config in self.config.values():
            assert config["i4UserSetting"] == {"nested": {"keep": True}}
        for provider, config in self.config.items():
            feature = []
            for event, groups in config["hooks"].items():
                for group in groups:
                    for handler in ([group] if provider == "copilot" else group["hooks"]):
                        launch = handler.get("bash" if provider == "copilot" else "command", "")
                        if "scan-secrets.py" in launch or "scan-status.py" in launch:
                            feature.append((event, "scan-status.py" if "scan-status.py" in launch else "scan-secrets.py"))
            assert feature == [(EVENTS[provider][1], "scan-status.py")], (provider, feature)
        shutil.rmtree(current)
        assert not old.exists() and not current.exists()
        self.cli_path = self.home / ".local/lib/scan-secrets/scripts/scan-secrets.py"
        return {"scope": "composed authentic provider-pre-status assets/config plus genuine T6 neutral archive", "provider_provenance": provenance,
                "provider_archive_sha256": sha(archive), "old_provider_assets": old_assets, "legacy_neutral_receipt": json.loads(legacy.stdout),
                "t6_archive_sha256": sha(release.read_bytes()), "old_source_removed": True, "current_source_removed": True,
                "neutral_installation": json.loads((self.cli_path.parent.parent / "installation.json").read_bytes()),
                "registration_sha256": {p: sha((self.home / name).read_bytes()) for p, name in CONFIGS.items()}}

    def handlers(self, provider, event, tool=None):
        for group in self.config[provider]["hooks"].get(event, []):
            matcher = group.get("matcher")
            normalized = "Bash" if provider == "codex" and tool == "exec_command" else tool
            if matcher and tool is not None and matcher != "*" and not re.fullmatch(matcher, normalized):
                continue
            yield from ([group] if provider == "copilot" else group["hooks"])

    def event(self, provider, event, payload, tool=None):
        finals = []
        for handler in self.handlers(provider, event, tool):
            command = handler["bash" if provider == "copilot" else "command"]
            command = command.replace("$HOME", str(self.home)).replace("~", str(self.home))
            env = {**self.env, **handler.get("env", {})}
            # Codex/Copilot interpret TOOL_GUARD_LOG_DIR as the log filename;
            # Gemini appends guard.log. Distinct provider roots avoid collision.
            env["TOOL_GUARD_LOG_DIR"] = str(self.logs / (provider + "-guardian"))
            env["AUDIT_LOG"] = str(self.logs / (provider + "-audit.log"))
            arguments = shlex.split(command)
            name = Path(arguments[-1]).name
            result = self.run(arguments, data=json.dumps(payload).encode(), env=env, timeout=12)
            rows = [json.loads(row) for row in result.stdout.splitlines()]
            # A successful RTK/observability no-op may be silent. Security and
            # feature-status handlers must supply their documented JSON result.
            silent = not rows and (name == "send-event.py" or name.startswith("rtk-hook"))
            assert rows or silent, (provider, event, command)
            final = rows[-1] if rows else {}
            self.dispatches.append({"provider": provider, "event": event, "tool": tool,
                "matcher_tool": "Bash" if provider == "codex" and tool == "exec_command" else tool,
                "entrypoint": name, "silent_allowed_noop": silent,
                "output": rows, "seconds": self.calls[-1]["seconds"]})
            finals.append(final)
            decision = native_decision(final)
            if decision in {"deny", "block", "ask"} or final.get("continue") is False:
                return False, payload, finals
            updated = final.get("updatedInput", final.get("hookSpecificOutput", {}).get("updatedInput"))
            if updated is not None:
                payload["toolArgs" if provider == "copilot" else "tool_input"] = updated
        return True, payload, finals

    def shell(self, provider, command, *, allowed=True):
        payload = full_shell_envelope(provider, command)
        payload["cwd"] = str(self.repo)
        if provider == "codex":
            payload["tool_input"]["workdir"] = str(self.repo)
        elif provider == "gemini":
            payload["tool_input"]["dir_path"] = str(self.repo)
        tool = payload["toolName" if provider == "copilot" else "tool_name"]
        permit, updated, _ = self.event(provider, EVENTS[provider][0], payload, tool)
        assert permit == allowed, (provider, command, permit)
        if not permit:
            return None
        value = updated["toolArgs" if provider == "copilot" else "tool_input"]
        exact = value["cmd" if provider == "codex" else "command"]
        return self.run(["/bin/bash", "-c", exact])

    def write(self, provider, relative, old, new):
        path = self.repo / relative
        assert path.read_bytes() == old
        value = {"file_path": relative, "old_string": old.decode(), "new_string": new.decode()}
        fixture = Fixture("i4.actual-repair", "replace", value, "allow", "allow", "native-write", "I4")
        payload = envelope(provider, fixture)
        if provider == "codex":
            payload["tool_input"] = {"command": "\n".join(["*** Begin Patch", "*** Update File: " + relative, "@@",
                *("-" + line for line in old.decode().splitlines()), *("+" + line for line in new.decode().splitlines()), "*** End Patch"])}
        payload["cwd"] = str(self.repo)
        tool = payload["toolName" if provider == "copilot" else "tool_name"]
        permit, updated, _ = self.event(provider, EVENTS[provider][0], payload, tool)
        assert permit, (provider, relative)
        # This is the native tool executor. It interprets only the exact edit
        # grammar submitted above, after installed registered handlers permit it.
        body = updated["toolArgs" if provider == "copilot" else "tool_input"]
        if provider == "codex":
            lines = body["command"].splitlines()
            assert lines[:2] == ["*** Begin Patch", "*** Update File: " + relative]
            assert lines[2] == "@@" and lines[-1] == "*** End Patch"
            removed = "\n".join(line[1:] for line in lines[3:-1] if line.startswith("-")) + "\n"
            added = "\n".join(line[1:] for line in lines[3:-1] if line.startswith("+")) + "\n"
            assert removed.encode() == old and added.encode() == new
        else:
            assert body["path" if provider == "copilot" else "file_path"] == relative
            assert body["old_str" if provider == "copilot" else "old_string"].encode() == old
            assert body["new_str" if provider == "copilot" else "new_string"].encode() == new
        path.write_bytes(new)
        assert path.read_bytes() == new
        return {"provider": provider, "path": relative, "old_sha256": sha(old), "new_sha256": sha(new), "bytes": len(new), "guarded_real_write": True}

    def endturn(self, state, expected):
        before = self.cli_path.read_bytes(); mode = self.cli_path.stat().st_mode & 0o777
        actual = self.cli_path.with_name("i4-real-cli.py")
        trace = self.logs / "status-actions.jsonl"
        actual.write_bytes(before)
        # Scoped trace forwards the real installed CLI. It is never present
        # during checkpoint or Git-gate positive proof; no engine is poisoned.
        wrapper = "import json,os,sys\nfrom pathlib import Path\nwith open(" + repr(str(trace)) + ",'a') as f: f.write(json.dumps(sys.argv[1:])+'\\n')\nos.execv(sys.executable,[sys.executable,'-I','-S','-B'," + repr(str(actual)) + ",*sys.argv[1:]])\n"
        self.cli_path.write_text(wrapper)
        offset = len(trace.read_bytes().splitlines()) if trace.exists() else 0
        try:
            for provider in CONFIGS:
                for active in (False, True, True):
                    event = EVENTS[provider][1]
                    permitted, _, finals = self.event(provider, event, {"cwd": str(self.repo), "hook_event_name": event, "stop_hook_active": active})
                    assert permitted
                    messages = [d["output"] for d in self.dispatches if d["provider"] == provider and d["event"] == event and d["entrypoint"] == "scan-status.py"]
                    assert expected in json.dumps(messages[-1])
                    assert all(f.get("decision") not in {"deny", "block"} and f.get("continue") is not False for f in finals)
            actions = [json.loads(line) for line in trace.read_bytes().splitlines()[offset:]]
            assert len(actions) == 9
            assert all(row == ["status", "--json", "--no-input", "--repo", str(self.repo)] for row in actions)
            return {"state": state, "callbacks": 9, "actions": actions, "continuations": 0}
        finally:
            self.cli_path.write_bytes(before); self.cli_path.chmod(mode); actual.unlink()
            assert self.cli_path.read_bytes() == before


def scenario(lab, merge):
    setup = lab.setup()
    if merge:
        shutil.rmtree(lab.repo)
        lab.run([GIT, "clone", "--shared", "--no-checkout", "-q", str(lab.source), str(lab.repo)], cwd=lab.root)
        lab.git("-c", "core.hooksPath=" + os.devnull, "checkout", "-q", MERGE[0])
        lab.git("-c", "core.hooksPath=" + os.devnull, "merge", "--no-commit", "--no-ff", MERGE[1], expected=1)
    else:
        for n, size in enumerate(SIZES):
            (lab.repo / f"image-{n}.png").write_bytes(b"\x89PNG\0" + bytes(size - 5))
        (lab.repo / "repair.txt").write_bytes(b"safe pending input\n")
    absent = lab.endturn("absent", "not scanned")
    observed = lab.cli("check", expected=1 if merge else 0)
    assert observed["counts"]["candidate_bytes"] == (9453698 if merge else 20026493)
    if merge:
        assert observed["counts"]["inspected_snapshots"] == 223
        assert len(observed["findings"]) == 1 and observed["findings"][0]["pattern"] == "stripe_live_key"
        relative = "scripts/test-codex-hooks-windows.ps1"
        raw = (lab.repo / relative).read_bytes()
        repaired, count = re.subn(rb"sk_live_[A-Za-z0-9]{16,}", lambda m: b"Z" * len(m[0]), raw)
        assert count == 2 and len(repaired) == len(raw)
    else:
        relative, raw, repaired = "repair.txt", b"safe pending input\n", b"safe repaired text\n"
        assert len(raw) == len(repaired) == 19
    repairs = []
    for provider in CONFIGS:
        read = lab.shell(provider, "rtk proxy cat " + shlex.quote(relative))
        assert read.stdout == (lab.repo / relative).read_bytes()
        if not merge:
            for n, size in enumerate(SIZES):
                binary = lab.shell(provider, "rtk proxy cat image-" + str(n) + ".png")
                assert len(binary.stdout) == size and sha(binary.stdout) == sha((lab.repo / f"image-{n}.png").read_bytes())
        previous = (lab.repo / relative).read_bytes()
        # First provider repairs the historical finding. Later providers make
        # distinct same-size real repair writes rather than fixture resets.
        following = repaired if provider == "codex" else previous.replace(b"Z", b"Y", 1) if merge else previous.replace(b"text", b"data") if provider == "copilot" else previous.replace(b"data", b"note")
        repairs.append(lab.write(provider, relative, previous, following))
        if merge:
            lab.shell(provider, "rtk proxy git add -- " + shlex.quote(relative))
        lab.shell(provider, OPERATIONS["hard_reset"], allowed=False)
        lab.shell(provider, OPERATIONS["force_push_protected_branch"], allowed=False)
        lab.shell(provider, "printf '%s\\n' " + shlex.quote(OPERATIONS["force_push_protected_branch"]) + " | bash", allowed=False)
    fixture_clean = lab.cli("check")
    assert fixture_clean["outcome"] == "complete_clean"
    assert fixture_clean["counts"]["candidate_bytes"] == (9453698 if merge else 20026493)
    if merge:
        assert fixture_clean["counts"]["inspected_snapshots"] == 223
    merge_resolution = None
    if merge:
        # Resolve one real unmerged textual path through the same registered
        # read/edit/stage harness, after retaining exact historical coverage.
        unmerged = lab.git("ls-files", "-u", "-z").stdout
        names = sorted({row.split(b"\t", 1)[1].decode() for row in unmerged.split(b"\0") if row})
        for name in names:
            path = lab.repo / name
            if path.is_file() and path.stat().st_size <= 30000 and b"<<<<<<< " in path.read_bytes():
                original = path.read_bytes()
                try:
                    original.decode()
                except UnicodeDecodeError:
                    continue
                ours = lab.shell("codex", "rtk proxy git show " + shlex.quote(":2:" + name)).stdout
                if len(ours) > 30000 or not original.endswith(b"\n") or not ours.endswith(b"\n"):
                    continue
                merge_resolution = lab.write("codex", name, original, ours)
                lab.shell("codex", "rtk proxy git add -- " + shlex.quote(name))
                assert lab.git("ls-files", "-u", "--", name).stdout == b""
                merge_resolution["actual_unmerged_path_resolved"] = True
                break
        assert merge_resolution is not None, "historical merge has no textual conflict to repair"
    clean = lab.cli("check") if merge else fixture_clean
    assert clean["outcome"] == "complete_clean"
    report, = (lab.root / "data/scan-secrets/status").glob("*.json")
    saved = json.loads(report.read_bytes()); saved["completed_at"] = "2001-01-01T00:00:00.000000Z"
    report.write_text(json.dumps(saved))
    states = [absent, lab.endturn("stale", "time 2001-01-01")]
    (lab.repo / "unsafe-fixture").symlink_to(lab.root / "missing")
    assert lab.cli("check", expected=2)["outcome"] == "incomplete"
    incomplete_repairs = []
    for provider in CONFIGS:
        read = lab.shell(provider, "rtk proxy cat " + shlex.quote(relative))
        assert read.stdout == (lab.repo / relative).read_bytes()
        previous = read.stdout
        following = previous + ("# I4 permitted repair during incomplete status: " + provider + "\n").encode()
        incomplete_repairs.append(lab.write(provider, relative, previous, following))
    states.append(lab.endturn("incomplete", "last incomplete"))
    (lab.repo / "unsafe-fixture").unlink()
    report.write_text("{corrupt private fixture}")
    states.append(lab.endturn("corrupt", "unavailable"))
    report.unlink(); report.mkdir()
    states.append(lab.endturn("unavailable", "unavailable"))
    report.rmdir()
    late = lab.repo / "zz-i4-late-control.txt"; late.write_bytes(fake() + b"\n")
    late_check = lab.cli("check", expected=1)
    assert late_check["outcome"] == "complete_findings"
    late_repairs = [lab.write("codex", late.name, late.read_bytes(), b"safe repaired control\n")]
    retry = lab.cli("check"); assert retry["outcome"] == "complete_clean"
    return {"kind": "historical-merge" if merge else "six-binaries", "setup": setup, "initial_checkpoint": observed,
            "guarded_repairs": repairs, "fixture_clean_checkpoint": fixture_clean,
            "actual_merge_resolution": merge_resolution, "clean_checkpoint": clean, "endturn_states": states,
            "permitted_repairs_during_incomplete_status": incomplete_repairs,
            "late_checkpoint": late_check, "late_repairs": late_repairs, "checkpoint_retry": retry,
            "calls": lab.calls, "registered_dispatches": lab.dispatches}


def gate(lab):
    setup = lab.setup()
    installed = lab.cli("hooks", "install", "--git", GIT)
    (lab.repo / "content.txt").write_bytes(b"clean baseline\n")
    lab.shell("codex", "rtk proxy git add -- content.txt")
    lab.shell("codex", "rtk proxy git commit -qm 'clean baseline'")
    lab.write("gemini", "content.txt", b"clean baseline\n", fake() + b"\n")
    lab.shell("gemini", "rtk proxy git add -- content.txt")
    # Guardian permits this ordinary commit request; installed gate must reject.
    payload = full_shell_envelope("codex", "rtk proxy git commit -qm 'late fixture'")
    payload["cwd"] = str(lab.repo); payload["tool_input"]["workdir"] = str(lab.repo)
    permitted, updated, _ = lab.event("codex", "PreToolUse", payload, "exec_command")
    assert permitted
    rejected = lab.run(["/bin/bash", "-c", updated["tool_input"]["cmd"]], expected=None)
    assert rejected.returncode != 0 and b"content.txt" in rejected.stderr
    repair = lab.write("copilot", "content.txt", fake() + b"\n", b"safe retry\n")
    lab.shell("copilot", "rtk proxy git add -- content.txt")
    lab.shell("copilot", "rtk proxy git commit -qm 'repaired retry'")
    assert lab.cli("check")["outcome"] == "complete_clean"
    return {"kind": "installed-gate", "setup": setup, "installation": installed, "late_commit_rejected": rejected.returncode,
            "guarded_repair": repair, "retry_committed": True, "calls": lab.calls, "registered_dispatches": lab.dispatches}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    sys.path.insert(0, str(source / "scripts"))
    global Fixture, envelope, full_shell_envelope, OPERATIONS, native_decision
    from tool_guard_corpus import Fixture, envelope, full_shell_envelope, OPERATIONS
    from tool_guard_test_support import native_decision
    before = fingerprint(source)
    probe = Path(__file__).resolve()
    probe_before = {"sha256": sha(probe.read_bytes()), "mode": oct(probe.stat().st_mode & 0o777)}
    result = {"schema": "i4_probe_v1", "python": sys.version, "executable": sys.executable,
              "command": sys.argv, "source_sha": subprocess.check_output([GIT, "-C", str(source), "rev-parse", "HEAD"]).decode().strip(),
              "probe_input": probe_before, "source_inputs": before, "results": [],
              "limits": "macOS source-free installed harness; no authenticated host or native Windows proof"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    retained = args.output.with_suffix("").with_name(args.output.stem + "-logs")
    retained.mkdir(exist_ok=False)
    try:
        for name in ("historical-merge", "six-binaries", "installed-gate"):
            with tempfile.TemporaryDirectory(prefix="i4-") as directory:
                lab = Lab(Path(directory), source)
                try:
                    observation = gate(lab) if name == "installed-gate" else scenario(lab, name == "historical-merge")
                    result["results"].append(observation)
                except BaseException as error:
                    message = str(error).replace(fake().decode(), "[synthetic credential redacted]")
                    result["failure"] = {"group": name, "type": type(error).__name__, "message": message[:4000], "calls": lab.calls, "registered_dispatches": lab.dispatches}
                    raise
                finally:
                    destination = retained / name
                    shutil.copytree(lab.logs, destination)
                    (destination / "process-receipts.json").write_text(json.dumps({"calls": lab.calls, "dispatches": lab.dispatches}, indent=2) + "\n")
                    result.setdefault("retained_logs", {})[name] = {str(p): {"bytes": p.stat().st_size, "sha256": sha(p.read_bytes())}
                        for p in sorted(destination.rglob("*")) if p.is_file()}
                    result["source_unchanged"] = fingerprint(source) == before
                    result["probe_unchanged"] = {"sha256": sha(probe.read_bytes()), "mode": oct(probe.stat().st_mode & 0o777)} == probe_before
                    args.output.write_text(json.dumps(result, indent=2) + "\n")
        assert result["source_unchanged"]
        assert result["probe_unchanged"]
        assert args.output.stat().st_size < 1048576
        assert fake() not in args.output.read_bytes()
        print(json.dumps({"outcome": "pass", "groups": len(result["results"]), "output": str(args.output), "sha256": sha(args.output.read_bytes())}))
    finally:
        args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
