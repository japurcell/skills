#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
if (-not $IsWindows) {
    Write-Host 'SKIP: native Windows lifecycle envelopes require Windows'
    exit 0
}
$source = @'
import json, os, pathlib, subprocess, sys, tempfile

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
    env = {**os.environ, "AUDIT_LOG": str(base / "audit.log")}

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

print("PASSED: native Windows lifecycle envelopes")
'@
& python -c $source $root
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
