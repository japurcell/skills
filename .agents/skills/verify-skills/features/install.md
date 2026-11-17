# Default installation and refresh

## Sub-features

- Install default skills and provider assets into an empty home.
- Refresh an existing install without corrupting its configuration.
- Show help without installing.

## How to get to it (user POV)

Run `./scripts/install.sh` from the checkout; PowerShell users run `pwsh -NoProfile -File scripts/install.ps1`. Both accept `--help`.

## Driving it with Bash

After Launch and Doctor, with an empty `$VERIFY_HOME`:

```bash
printf '%s\n' 'bash scripts/install.sh (isolated HOME and CODEX_HOME, selection=0)' > "$VERIFY_EVIDENCE/actions.txt"
rtk proxy env HOME="$VERIFY_HOME" CODEX_HOME="$VERIFY_HOME/.codex" INSTALL_FOREST_SERVICE_SKILLS=0 bash scripts/install.sh > "$VERIFY_EVIDENCE/install.stdout" 2> "$VERIFY_EVIDENCE/install.stderr"
VERIFY_EXIT=$?
printf '%s\n' "$VERIFY_EXIT" > "$VERIFY_EVIDENCE/install.exit"
rtk proxy test "$VERIFY_EXIT" -eq 0
rtk proxy python3 - "$VERIFY_ROOT" "$VERIFY_HOME" > "$VERIFY_EVIDENCE/readback.txt" <<'PY'
import json, sys, tomllib
from pathlib import Path
root, home = map(Path, sys.argv[1:])
expected = {p.name for p in (root/'skills/default').iterdir()
            if p.is_dir() and p.name != 'archive' and not p.name.endswith('-workspace')}
actual = {p.name for p in (home/'.agents/skills').iterdir() if p.is_dir()}
assert expected == actual, (expected-actual, actual-expected)
for name in sorted(expected):
    assert (home/'.agents/skills'/name/'SKILL.md').stat().st_size
print('Installed default skills:', len(expected))
assert (home/'.codex/AGENTS.md').read_bytes() == (root/'.codex/AGENTS.md').read_bytes()
for relative in ('.codex/hooks.json', '.copilot/hooks/hooks.json', '.gemini/settings.json'):
    value = json.loads((home/relative).read_text())
    assert isinstance(value, dict) and 'hooks' in value, relative
    print('Parsed:', relative)
agents = list((home/'.codex/agents').glob('*.toml'))
assert agents
for path in agents:
    assert tomllib.loads(path.read_text())['developer_instructions'].strip(), path
print('Parsed Codex agents:', len(agents))
assert not list((home/'.agents/skills').rglob('*.pyc'))
print('PASS: real installation file readback')
PY
```

Stop on any nonzero command and clean up, retaining the failure. For refresh coverage, snapshot installed file contents and modes, rerun the same install into this home, and compare before/after; unchanged inputs must give identical contents. Save both manifests. For help coverage, use a separate empty home, run `--help`, require exit 0 and `Usage:` on stdout, and assert the home remains empty. Repeat through `pwsh -NoProfile -File scripts/install.ps1` for PowerShell coverage, using a new home and distinct logs.

## Gotchas

- Fresh-install success requires exit 0, expected default skill names, valid configs, parsed agents, and readback PASS. Merely finding one skill is insufficient.
- Source rebasing intentionally changes some installed Markdown; byte equality is appropriate only for assets that are copied unchanged.
- No provider is launched here. Client trust and runtime hook delivery remain unverified.
- RTK or source preflight failures must be reported before generating a success claim.
