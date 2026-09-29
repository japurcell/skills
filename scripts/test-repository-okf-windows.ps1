#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$source = @'
import json, os, pathlib, shutil, subprocess, sys, tempfile

source = pathlib.Path(sys.argv[1])
assert os.name == "nt", "native Windows execution required"
with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary) / "repo"
    shutil.copytree(source / "scripts/fixtures/okf-valid-repo", root)
    shutil.copytree(source / "scripts", root / "scripts")
    adapters = (
        (source / ".github/hooks/scripts", root / ".github/hooks/scripts"),
        (source / ".gemini/hooks/scripts", root / ".gemini/hooks/scripts"),
        (source / ".codex/hooks", root / ".codex/hooks"),
    )
    for origin, target in adapters:
        target.mkdir(parents=True)
        for name in ("lint-okf.py", "repository-okf.py"):
            if (origin / name).exists():
                shutil.copy2(origin / name, target / name)
        shutil.copytree(origin / "helpers", target / "helpers")
    file = root / ".agents/instructions/repo.md"
    file.write_text(file.read_text().replace("type: Agent Instruction", "type: Agent Memory"))
    nested = root / "nested/work"
    nested.mkdir(parents=True)
    payloads = (
        (root / ".github/hooks/scripts/lint-okf.py", {"cwd": str(nested), "hook_event_name": "Stop"}),
        (root / ".gemini/hooks/scripts/lint-okf.py", {"cwd": str(nested), "hook_event_name": "AfterAgent"}),
        (root / ".codex/hooks/repository-okf.py", {"cwd": str(nested), "hook_event_name": "Stop"}),
    )
    for script, payload in payloads:
        env = {**os.environ, "AUDIT_LOG": str(root / (script.parent.parent.name + "-audit.log"))}
        response = subprocess.run([sys.executable, str(script)], input=json.dumps(payload), text=True, capture_output=True, env=env, timeout=11)
        assert response.returncode == 0, (script, response.stderr)
        output = json.loads(response.stdout)
        assert "OKF101" in output["reason"], (script, output)
        assert "python scripts/lint-okf.py" in output["reason"], (script, output)
        assert len(response.stdout.encode()) < 8192, script
    registration = json.loads((source / ".codex/hooks.json").read_text())["hooks"]["Stop"][0]["hooks"][0]
    assert "git','rev-parse','--show-toplevel" in registration["commandWindows"]
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    registered = subprocess.run(registration["commandWindows"], shell=True, cwd=nested,
        input=json.dumps({"cwd": str(nested), "hook_event_name": "Stop"}), text=True, capture_output=True,
        env={**os.environ, "AUDIT_LOG": str(root / "registered-audit.log")}, timeout=11)
    assert registered.returncode == 0 and "OKF101" in json.loads(registered.stdout)["reason"], registered
print("PASSED: native Windows repository OKF envelopes")
'@
if (-not $IsWindows) {
    Write-Host 'SKIP: native Windows repository OKF envelopes require Windows'
    exit 0
}
& python -c $source $root
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
