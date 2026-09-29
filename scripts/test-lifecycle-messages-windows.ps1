#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
if (-not $IsWindows) {
    Write-Host 'SKIP: native Windows lifecycle envelopes require Windows'
    exit 0
}
$source = @'
import json, os, pathlib, shutil, subprocess, sys, tempfile

source = pathlib.Path(sys.argv[1])
assert os.name == "nt", "native Windows execution required"

def invoke(script, payload, *, cwd=None, environment=None):
    completed = subprocess.run(
        [sys.executable, str(script)], input=json.dumps(payload), text=True,
        capture_output=True, cwd=cwd, env=environment, timeout=12,
    )
    assert completed.returncode == 0, (script, completed.stderr)
    lines = [json.loads(line) for line in completed.stdout.splitlines()]
    assert lines and all(isinstance(line, dict) for line in lines), (script, completed.stdout)
    assert all(item.get("type") == "progress" for item in lines[:-1]), lines
    assert len(completed.stdout.encode()) < 8192, (script, len(completed.stdout.encode()))
    return lines

with tempfile.TemporaryDirectory(prefix="lifecycle-windows-") as temporary:
    base = pathlib.Path(temporary)
    root = base / "repo"
    shutil.copytree(source / "scripts/fixtures/okf-valid-repo", root)
    shutil.copytree(source / "scripts", root / "scripts")
    for relative in (
        ".github/hooks/scripts/validate-stop.py",
        ".github/hooks/scripts/lint-okf.py",
        ".github/hooks/scripts/inject-auto-ingest-context.py",
        ".gemini/hooks/scripts/lint-okf.py",
        ".codex/hooks/repository-okf.py",
    ):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, target)
    for relative in (
        ".github/hooks/scripts/helpers",
        ".gemini/hooks/scripts/helpers",
        ".codex/hooks/helpers",
    ):
        shutil.copytree(source / relative, root / relative)
    env = {**os.environ, "AUDIT_LOG": str(base / "audit.log")}
    payloads = (
        (root / ".github/hooks/scripts/validate-stop.py", {"hook_event_name": "agentStop", "cwd": str(root)}),
        (root / ".gemini/hooks/scripts/lint-okf.py", {"hook_event_name": "AfterAgent", "cwd": str(root)}),
        (root / ".codex/hooks/repository-okf.py", {"hook_event_name": "Stop", "cwd": str(root)}),
    )
    clean = [invoke(script, payload, environment=env) for script, payload in payloads]
    assert clean[0][0] == {"type": "progress", "message": "validate-stop: pass; 2 checks"}, clean[0]
    assert clean[1][-1] == {"systemMessage": "lint-okf: pass; 0 diagnostics"}, clean[1]
    assert clean[2][-1] == {"systemMessage": "repository-okf: pass; 0 diagnostics"}, clean[2]

    document = root / ".agents/instructions/repo.md"
    document.write_text(document.read_text().replace("type: Agent Instruction", "type: Agent Memory"))
    failed = [invoke(script, payload, environment=env) for script, payload in payloads]
    assert failed[0][-1]["decision"] == "block" and "validate-stop: blocked;" in failed[0][-1]["reason"], failed[0]
    assert failed[1][-1]["decision"] == "deny" and "lint-okf: blocked;" in failed[1][-1]["reason"], failed[1]
    assert failed[2][-1]["decision"] == "block" and "repository-okf: blocked;" in failed[2][-1]["reason"], failed[2]
    for script, payload in payloads:
        retry = invoke(script, {**payload, "stop_hook_active": True}, environment=env)
        assert "unresolved" in json.dumps(retry), (script, retry)

    (root / "scripts/lint-okf.py").unlink()
    for script, payload in payloads:
        incomplete = invoke(script, payload, environment=env)
        assert "incomplete" in json.dumps(incomplete).lower() or "OKF900" in json.dumps(incomplete), (script, incomplete)

    home = base / "home"
    skill = home / ".agents/skills/caveman/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("# Caveman\n")
    startup_env = {**env, "HOME": str(home), "USERPROFILE": str(home),
                   "COPILOT_SKILLS_DIR": str(skill.parent.parent),
                   "AGENTS_SKILLS_DIR": str(skill.parent.parent),
                   "AGENTS_REQUIRED_SKILL_FILES": "caveman/SKILL.md"}
    startup = (
        (source / ".copilot/hooks/scripts/load-required-skills.py", {"hook_event_name": "sessionStart"}),
        (source / ".gemini/hooks/scripts/skill-context-injector.py", {"hook_event_name": "SessionStart"}),
        (source / ".codex/hooks/load-required-skills.py", {"hook_event_name": "SessionStart", "source": "startup"}),
    )
    for script, payload in startup:
        lines = invoke(script, payload, environment=startup_env)
        visible = lines[0].get("message") or lines[-1].get("systemMessage")
        assert "pass; 1 skill file" in visible, (script, lines)

    scan_root = base / "scan-repo"
    scan_root.mkdir()
    subprocess.run(["git", "init", "-q", str(scan_root)], check=True)
    scanners = (
        ("copilot", source / ".copilot/hooks/scripts/scan-secrets.py", {"sessionId": "test"}),
        ("gemini", source / ".gemini/hooks/scripts/scan-secrets.py", {"hook_event_name": "BeforeTool", "cwd": str(scan_root)}),
        ("codex", source / ".codex/hooks/scan-secrets.py", {"hook_event_name": "PreToolUse", "cwd": str(scan_root)}),
    )
    for provider, script, payload in scanners:
        scan_env = {**env, "SCAN_MODE": "block", "SECRETS_LOG_DIR": str(base / (provider + "-logs"))}
        assert invoke(script, payload, cwd=scan_root, environment=scan_env)[-1] == {}, provider
        credential = scan_root / "credential.txt"
        credential.write_text("sk_live_1234567890abcdefghij\n")
        warning = invoke(script, payload, cwd=scan_root, environment={**scan_env, "SCAN_MODE": "warn"})[-1]
        assert "scan-secrets warning" in warning["systemMessage"], (provider, warning)
        denied = invoke(script, payload, cwd=scan_root, environment=scan_env)[-1]
        assert denied.get("decision") in {"deny", "block"} or denied.get("permissionDecision") == "deny" or denied.get("hookSpecificOutput", {}).get("permissionDecision") == "deny", (provider, denied)
        assert "sk_live_" not in json.dumps(denied), (provider, denied)
        credential.unlink()

print("PASSED: native Windows lifecycle envelopes")
'@
& python -c $source $root
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
