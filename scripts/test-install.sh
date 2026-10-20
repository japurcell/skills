#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

# Child fixtures must never inherit an account's custom install destination/selection.
unset CODEX_HOME INSTALL_FOREST_SERVICE_SKILLS

create_fixture_repo() {
  local repo="$1"
  local script provider

  mkdir -p \
    "$repo/scripts" \
    "$repo/skills/default/alpha" \
    "$repo/skills/default/alpha/evals" \
    "$repo/skills/forest-service" \
    "$repo/skills/default/beta-workspace" \
    "$repo/skills/default/archive" \
    "$repo/agents" \
    "$repo/agents/nested" \
    "$repo/references" \
    "$repo/.codex/hooks" \
    "$repo/.copilot/hooks" \
    "$repo/.gemini/policies"

  for script in install.sh install-scan-secrets.py scan-secrets.py scan_install_windows.py file_io.py trusted_hook_launch.py install-codex-agents.py install-codex-hooks.py configure-rtk.py; do
    cp -p "$REPO_ROOT/scripts/$script" "$repo/scripts/$script"
  done
  mkdir -p "$repo/bin"
  printf '%s\n' '#!/bin/sh' 'printf "rtk 0.50.0\\n"' > "$repo/bin/rtk"
  chmod 755 "$repo/bin/rtk"
  PATH="$repo/bin:$PATH"
  export PATH
  for script in install-provider-hooks.py rebase-skill-references.py validate-skill-sources.py; do
    cp -p "$REPO_ROOT/scripts/$script" "$repo/scripts/$script"
  done
  cp -p "$REPO_ROOT/.codex/global-hooks.json" "$repo/.codex/global-hooks.json"
  cp -p "$REPO_ROOT/.codex/AGENTS.md" "$repo/.codex/AGENTS.md"
  cp -p "$REPO_ROOT/.codex/hooks/load-required-skills.py" "$repo/.codex/hooks/load-required-skills.py"
  printf '%s\n' '---' 'name: alpha' '---' 'Standalone.' > "$repo/skills/default/alpha/SKILL.md"
  printf '%s\n' 'fixture eval content' > "$repo/skills/default/alpha/evals/evals.json"
  : > "$repo/skills/forest-service/.gitkeep"
  printf '%s\n' 'workspace skill should not copy' > "$repo/skills/default/beta-workspace/SKILL.md"
  printf '%s\n' 'archive entry should not copy' > "$repo/skills/default/archive/README.md"
  printf '%s\n' '---' 'name: helper' 'description: Fixture helper agent.' '---' 'Use alpha.' > "$repo/agents/helper.md"
  printf '%s\n' '---' 'name: nested-helper' 'description: Nested fixture helper agent.' '---' 'Use alpha deeply.' > "$repo/agents/nested/helper.md"
  cp -p "$REPO_ROOT/.gemini/GEMINI.md" "$repo/.gemini/GEMINI.md"
  printf '%s\n' 'Nested policy.' > "$repo/.gemini/policies/plan-custom-directory.toml"
  printf '%s\n' 'Hidden note.' > "$repo/.gemini/.hidden-note"
  cp -p "$REPO_ROOT/.copilot/copilot-instructions.md" "$repo/.copilot/copilot-instructions.md"
  printf '%s\n' '{}' > "$repo/.copilot/lsp-config.json"
  printf '%s\n' '#!/bin/bash' 'echo hook' > "$repo/.copilot/hooks/test-hook.sh"
  printf '%s\n' '{"version":1,"hooks":{"preToolUse":[{"type":"command","bash":"$HOME/.copilot/hooks/scripts/tool-guard.py"}]}}' > "$repo/.copilot/hooks/hooks.json"
  printf '%s\n' '{"global":"settings"}' > "$repo/.gemini/global-settings.json"
  printf '%s\n' '{"local":"settings"}' > "$repo/.gemini/settings.json"

  mkdir -p "$repo/.gemini/hooks/scripts" "$repo/.copilot/hooks/scripts"
  for provider in .gemini .copilot; do
    printf '%s\n' 'print("hook")' > "$repo/$provider/hooks/scripts/test-hook.py"
  done
  for provider in .gemini .copilot; do
    printf '%s\n' '#!/bin/bash' 'echo hook' > "$repo/$provider/hooks/scripts/test-hook.sh"
  done
  add_generated_hook_fixture "$repo"
}

add_generated_hook_fixture() {
  local repo="$1"

  cp -p "$REPO_ROOT/scripts/generate-hooks.py" "$repo/scripts/generate-hooks.py"
  cp -Rp "$REPO_ROOT/hooks" "$repo/hooks"
  find "$repo/hooks" -type d -name __pycache__ -prune -exec rm -rf -- {} +

  PYTHONDONTWRITEBYTECODE=1 python3 - "$REPO_ROOT" "$repo" <<'PY'
import os
import shutil
import sys
from pathlib import Path

source_root = Path(sys.argv[1])
fixture_root = Path(sys.argv[2])
sys.path.insert(0, str(fixture_root))
from hooks.manifest import targets

for target in targets():
    source = source_root.joinpath(*target.output_path.parts)
    destination = fixture_root.joinpath(*target.output_path.parts)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    os.chmod(destination, target.mode)
PY
  PYTHONDONTWRITEBYTECODE=1 python3 "$repo/scripts/generate-hooks.py" --write >/dev/null
}

test_provider_refresh_preserves_retired_and_user_entries() {
  local workdir repo home first second first_config_inodes second_config_inodes
  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"
  create_fixture_repo "$repo"
  # Model the pending provider retirements in this disposable checkout only.
  python3 - "$repo" <<'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1])
manifest = root / 'hooks/manifest.py'
lines = manifest.read_text().splitlines(keepends=True)
manifest.write_text(''.join(line for line in lines if not ('GeneratedTarget(' in line and ('"repository_state"' in line or '"markdown_health"' in line) and ('"copilot"' in line or '"gemini"' in line))))
for provider in ('copilot', 'gemini'):
    for name in ('repository-state.py', 'markdown-health.py'):
        (root / f'.{provider}/hooks/scripts/{name}').unlink(missing_ok=True)
PY
  printf '%s\n' '{"general":{"enableAutoUpdate":false},"hooks":{"BeforeTool":[{"hooks":[{"command":"python \"$HOME/.gemini/hooks/scripts/tool-guard.py\""}]}]}}' > "$repo/.gemini/global-settings.json"
  PYTHONDONTWRITEBYTECODE=1 python3 "$repo/scripts/generate-hooks.py" --write >/dev/null
  mkdir -p "$home/.copilot/hooks" "$home/.gemini"
  cat > "$home/.copilot/hooks/hooks.json" <<'EOF'
{"version":1,"userSetting":{"keep":true},"hooks":{"preToolUse":[{"type":"command","bash":"python3 \"$HOME/.copilot/hooks/scripts/repository-state.py\"","powershell":"python \"$HOME/.copilot/hooks/scripts/repository-state.py\"","timeoutSec":17},{"type":"command","bash":"$HOME/.copilot/hooks/scripts/tool-guard.py"},{"type":"command","bash":"echo custom"}],"agentStop":[{"type":"command","bash":"python3 \"$HOME/.copilot/hooks/scripts/markdown-health.py\"","env":{"MARKDOWN_HEALTH_EVENT":"final"}},{"type":"command","bash":"echo unrelated"}]}}
EOF
  cat > "$home/.gemini/settings.json" <<'EOF'
{"general":{"enableAutoUpdate":true,"custom":42},"userSetting":{"keep":true},"hooks":{"BeforeTool":[{"matcher":"legacy","hooks":[{"name":"repository-state","type":"command","command":"python \"$HOME/.gemini/hooks/scripts/repository-state.py\"","timeout":17000},{"command":"echo custom"}]}],"AfterAgent":[{"hooks":[{"name":"markdown-health","command":"python \"$HOME/.gemini/hooks/scripts/markdown-health.py\"","env":{"MARKDOWN_HEALTH_EVENT":"final"}}]}]}}
EOF
  HOME="$home" bash "$repo/scripts/install.sh" >/dev/null
  python3 - "$home" <<'PY'
import json
import os
import stat
import sys
from pathlib import Path
home = Path(sys.argv[1])
copilot = json.loads((home / '.copilot/hooks/hooks.json').read_text())
gemini = json.loads((home / '.gemini/settings.json').read_text())
if os.name != 'nt':
    for path in (home / '.copilot/hooks/hooks.json', home / '.gemini/settings.json'):
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
pre = copilot['hooks']['preToolUse']
assert copilot['userSetting'] == {'keep': True}, copilot
assert pre[0] == {'type': 'command', 'bash': 'python3 "$HOME/.copilot/hooks/scripts/repository-state.py"', 'powershell': 'python "$HOME/.copilot/hooks/scripts/repository-state.py"', 'timeoutSec': 17}, pre
assert sum('tool-guard.py' in item.get('bash', '') for item in pre) == 1
assert {'type': 'command', 'bash': 'echo custom'} in pre
assert copilot['hooks']['agentStop'][0]['env'] == {'MARKDOWN_HEALTH_EVENT': 'final'}
assert copilot['hooks']['agentStop'][1]['bash'] == 'echo unrelated'
assert gemini['general'] == {'enableAutoUpdate': False, 'custom': 42}
assert gemini['userSetting'] == {'keep': True}
assert gemini['hooks']['BeforeTool'][0] == {'matcher': 'legacy', 'hooks': [{'name': 'repository-state', 'type': 'command', 'command': 'python "$HOME/.gemini/hooks/scripts/repository-state.py"', 'timeout': 17000}, {'command': 'echo custom'}]}
assert gemini['hooks']['AfterAgent'][0]['hooks'][0] == {'name': 'markdown-health', 'command': 'python "$HOME/.gemini/hooks/scripts/markdown-health.py"', 'env': {'MARKDOWN_HEALTH_EVENT': 'final'}}
PY
  first="$(tree_fingerprint "$home")"
  first_config_inodes="$(python3 - "$home" <<'PY'
import sys
from pathlib import Path
home = Path(sys.argv[1])
print(*(str((home / path).stat().st_ino) for path in ('.copilot/hooks/hooks.json', '.gemini/settings.json')))
PY
)"
  HOME="$home" bash "$repo/scripts/install.sh" >/dev/null
  second="$(tree_fingerprint "$home")"
  assert_equals "$first" "$second" "Expected repeated provider refresh to be idempotent."
  second_config_inodes="$(python3 - "$home" <<'PY'
import sys
from pathlib import Path
home = Path(sys.argv[1])
print(*(str((home / path).stat().st_ino) for path in ('.copilot/hooks/hooks.json', '.gemini/settings.json')))
PY
)"
  assert_equals "$first_config_inodes" "$second_config_inodes" "Expected owner-only unchanged provider configs not to be replaced."
}

test_provider_malformed_json_stops_before_mutation() {
  local workdir repo home before after
  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"
  create_fixture_repo "$repo"
  mkdir -p "$home/.copilot/hooks" "$home/.gemini" "$home/.agents/skills"
  printf '%s\n' 'sentinel' > "$home/.agents/skills/sentinel"
  printf '%s\n' '{"hooks":[],"hooks":{}}' > "$home/.copilot/hooks/hooks.json"
  printf '%s\n' '{"userSetting":true}' > "$home/.gemini/settings.json"
  before="$(tree_fingerprint "$home")"
  if HOME="$home" bash "$repo/scripts/install.sh" >"$workdir/out" 2>"$workdir/err"; then
    echo "Expected ambiguous Copilot JSON to stop installation." >&2
    exit 1
  fi
  after="$(tree_fingerprint "$home")"
  assert_equals "$before" "$after" "Expected malformed provider JSON to stop before home mutation."
  printf '%s\n' '{"hooks":{}}' > "$home/.copilot/hooks/hooks.json"
  printf '%s\n' '{bad' > "$home/.gemini/settings.json"
  before="$(tree_fingerprint "$home")"
  if HOME="$home" bash "$repo/scripts/install.sh" >"$workdir/out" 2>"$workdir/err"; then
    echo "Expected malformed Gemini JSON to stop installation." >&2
    exit 1
  fi
  after="$(tree_fingerprint "$home")"
  assert_equals "$before" "$after" "Expected malformed Gemini JSON to stop before home mutation."
  printf '%s\n' '{"hooks":{"preToolUse":[{"bash":"$HOME/.copilot/hooks/scripts/repository-state.py","powershell":"$HOME/.copilot/hooks/scripts/markdown-health.py"}]}}' > "$home/.copilot/hooks/hooks.json"
  printf '%s\n' '{"hooks":{}}' > "$home/.gemini/settings.json"
  before="$(tree_fingerprint "$home")"
  if HOME="$home" bash "$repo/scripts/install.sh" >"$workdir/out" 2>"$workdir/err"; then
    echo "Expected ambiguous retired commands to stop installation." >&2
    exit 1
  fi
  after="$(tree_fingerprint "$home")"
  assert_equals "$before" "$after" "Expected ambiguous retired commands to stop before home mutation."
}

test_provider_config_hard_links_do_not_change_other_files() {
  local workdir repo home outside path before
  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"
  create_fixture_repo "$repo"
  HOME="$home" bash "$repo/scripts/install.sh" >/dev/null
  for path in .copilot/hooks/hooks.json .gemini/settings.json; do
    outside="$workdir/$(basename "$(dirname "$path")")-outside.json"
    cp -p "$home/$path" "$outside"
    rm -- "$home/$path"
    ln "$outside" "$home/$path"
    chmod 644 "$outside"
    before="$(<"$outside")"
    HOME="$home" bash "$repo/scripts/install.sh" >/dev/null
    assert_equals "$before" "$(<"$outside")" "Expected refresh not to alter the other hard-linked file."
    python3 - "$outside" "$home/$path" <<'PY'
import os
import stat
import sys
from pathlib import Path
outside, installed = map(Path, sys.argv[1:])
assert stat.S_IMODE(outside.stat().st_mode) == 0o644
assert stat.S_IMODE(installed.stat().st_mode) == 0o600
assert os.stat(outside).st_ino != os.stat(installed).st_ino
PY
  done
}

test_provider_config_linked_parent_stops_before_mutation() {
  local workdir repo home outside before_home before_outside
  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  create_fixture_repo "$repo"
  for provider in copilot gemini; do
    home="$workdir/home-$provider"
    outside="$workdir/outside-$provider"
    mkdir -p "$outside" "$home"
    printf '%s\n' sentinel > "$outside/sentinel"
    if [[ "$provider" == copilot ]]; then
      mkdir -p "$home/.copilot"
      ln -s "$outside" "$home/.copilot/hooks"
    else
      ln -s "$outside" "$home/.gemini"
    fi
    before_home="$(tree_fingerprint "$home")"
    before_outside="$(tree_fingerprint "$outside")"
    if HOME="$home" bash "$repo/scripts/install.sh" >"$workdir/out" 2>"$workdir/err"; then
      echo "Expected linked $provider config parent to stop installation." >&2
      exit 1
    fi
    assert_equals "$before_home" "$(tree_fingerprint "$home")" "Expected linked-parent preflight to leave home untouched."
    assert_equals "$before_outside" "$(tree_fingerprint "$outside")" "Expected linked-parent preflight to leave link target untouched."
  done
}

generated_rtk_output_path() {
  local repo="$1"

  PYTHONDONTWRITEBYTECODE=1 python3 - "$repo" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1])
sys.path.insert(0, str(root))
from hooks.manifest import targets

for target in targets():
    if target.family == "rtk" and target.provider == "copilot":
        print(target.output_path.as_posix())
        break
else:
    raise SystemExit("fixture manifest did not declare a Copilot RTK target")
PY
}

tree_fingerprint() {
  local path="$1"

  python3 - "$path" <<'PY'
import hashlib
import os
import stat
import sys
from pathlib import Path

root = Path(sys.argv[1])
digest = hashlib.sha256()
for path in sorted((root, *root.rglob("*")), key=lambda item: item.relative_to(root).as_posix() if item != root else ""):
    relative = "." if path == root else path.relative_to(root).as_posix()
    details = path.lstat()
    digest.update(f"{relative}\0{stat.S_IFMT(details.st_mode)}\0{stat.S_IMODE(details.st_mode)}\0".encode())
    if stat.S_ISLNK(details.st_mode):
        digest.update(os.readlink(path).encode())
    elif stat.S_ISREG(details.st_mode):
        digest.update(path.read_bytes())
    digest.update(b"\0")
print(digest.hexdigest())
PY
}

assert_tree_unchanged() {
  assert_equals "$1" "$(tree_fingerprint "$2")" "$3"
}

assert_no_bytecode_cache() {
  local repo="$1"

  if find "$repo" -type d -name __pycache__ -print -quit | grep -q .; then
    echo "Expected generator preflight to create no __pycache__ directories." >&2
    exit 1
  fi
}

test_fresh_generated_hooks_preflight_installs_without_bytecode() {
  local workdir
  local repo
  local home

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"
  create_fixture_repo "$repo"
  HOME="$home" bash "$repo/scripts/install.sh" >/dev/null

  assert_no_bytecode_cache "$repo"
  if [[ ! -f "$home/.copilot/hooks/scripts/rtk-hook-copilot.py" || ! -f "$home/.gemini/hooks/scripts/rtk-hook-gemini.py" ]]; then
    echo "Expected fresh generated RTK outputs to be installed." >&2
    exit 1
  fi
  python3 -I -S -B - "$repo" "$home" <<'PY'
import json
from pathlib import Path
import subprocess
import sys
repo, home = (Path(value).resolve() for value in sys.argv[1:])
for provider, path, config in (
    ('codex', '.codex/hooks/hooks-diagnostics.py', '.codex/hooks.json'),
    ('copilot', '.copilot/hooks/scripts/hooks-diagnostics.py', '.copilot/hooks/hooks.json'),
    ('gemini', '.gemini/hooks/scripts/hooks-diagnostics.py', '.gemini/settings.json'),
):
    script = home / path
    assert script.read_bytes() == (repo / path).read_bytes(), provider
    assert script.stat().st_mode & 0o777 == 0o755, provider
    before = (home / config).read_bytes()
    result = subprocess.run([sys.executable, '-I', '-S', '-B', str(script), '--doctor'], cwd=home, capture_output=True, timeout=5)
    assert result.returncode == 0, (provider, result.stderr)
    report = json.loads(result.stdout)
    assert len(result.stdout) <= 16384, provider
    assert report['provider'] == provider, provider
    assert report['security']['outcome'] == 'not_scanned', provider
    assert report['audit']['outcome'] == 'not_attempted', provider
    assert report['repository']['health'] == 'not_collected', provider
    assert (home / config).read_bytes() == before, provider
PY
}

test_stale_generated_hooks_stop_before_destination_mutation() {
  local codex before_codex
  local workdir
  local repo
  local home
  local output_path
  local before
  local status

  workdir="$(setup_test_workdir)"
  trap 'cleanup_test_workdir; trap - RETURN' RETURN
  repo="$workdir/repo"
  home="$workdir/home"
  codex="$workdir/codex"
  create_fixture_repo "$repo"
  output_path="$(generated_rtk_output_path "$repo")"
  printf '%s\n' '# stale fixture output' >> "$repo/$output_path"
  mkdir -p "$home/preserved"
  printf '%s\n' 'do not change' > "$home/preserved/sentinel.txt"
  before="$(tree_fingerprint "$home")"
  mkdir -p "$codex"
  printf '%s\n' sentinel > "$codex/sentinel"
  before_codex="$(tree_fingerprint "$codex")"

  status=0
  HOME="$home" CODEX_HOME="$codex" bash "$repo/scripts/install.sh" >"$workdir/stdout" 2>"$workdir/stderr" || status=$?
  assert_equals "1" "$status" "Expected stale generated hooks to exit 1."
  assert_file_contains "$workdir/stderr" "$output_path" "Expected stale output path on stderr."
  assert_equals '' "$(cat "$workdir/stdout")" 'Expected no stdout for stale generated hooks.'
  assert_file_contains "$workdir/stderr" "python3 scripts/generate-hooks.py --write" "Expected stale-output recovery command on stderr."
  assert_tree_unchanged "$before" "$home" "Expected stale preflight to leave the destination tree byte-for-byte unchanged with no new directories."
  assert_tree_unchanged "$before_codex" "$codex" 'Expected stale preflight not to mutate external CODEX_HOME.'
}

test_generator_failure_stops_before_destination_mutation() {
  local codex before_codex
  local workdir
  local repo
  local home
  local before
  local status

  workdir="$(setup_test_workdir)"
  trap 'cleanup_test_workdir; trap - RETURN' RETURN
  repo="$workdir/repo"
  home="$workdir/home"
  codex="$workdir/codex"
  create_fixture_repo "$repo"
  python3 - "$repo/hooks/manifest.py" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
path.write_text(text.replace('GeneratedTarget("send_event", "copilot"', 'GeneratedTarget("send_event", "unknown"', 1), encoding="utf-8")
PY
  mkdir -p "$home/preserved"
  printf '%s\n' 'do not change' > "$home/preserved/sentinel.txt"
  before="$(tree_fingerprint "$home")"
  mkdir -p "$codex"
  printf '%s\n' sentinel > "$codex/sentinel"
  before_codex="$(tree_fingerprint "$codex")"

  status=0
  HOME="$home" CODEX_HOME="$codex" bash "$repo/scripts/install.sh" >"$workdir/stdout" 2>"$workdir/stderr" || status=$?
  assert_equals "1" "$status" "Expected a generator failure to become installer exit 1."
  assert_file_contains "$workdir/stderr" "Unknown provider 'unknown'" "Expected the generator diagnostic on stderr."
  if grep -Fq "python3 scripts/generate-hooks.py --write" "$workdir/stderr"; then
    echo "Expected generator failures to omit stale-output recovery advice." >&2
    exit 1
  fi
  assert_tree_unchanged "$before" "$home" "Expected generator failure preflight to leave the destination tree byte-for-byte unchanged with no new directories."
  assert_tree_unchanged "$before_codex" "$codex" 'Expected generator failure not to mutate external CODEX_HOME.'
}

test_installs_codex_agents_before_other_assets() {
  local workdir
  local repo
  local home
  local first_agent
  local first_manifest

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"
  create_fixture_repo "$repo"

  env -u CODEX_HOME HOME="$home" bash "$repo/scripts/install.sh" >/dev/null

  python3 - "$home/.codex/agents/helper.toml" "$home/.codex/agents/.skills-repo-agents.json" <<'PY'
import json
import stat
import sys
import tomllib
from pathlib import Path

agent_path = Path(sys.argv[1])
manifest_path = Path(sys.argv[2])
agent = tomllib.loads(agent_path.read_text(encoding="utf-8"))
assert agent == {
    "name": "helper",
    "description": "Fixture helper agent.",
    "developer_instructions": "Use alpha.\n",
}
assert json.loads(manifest_path.read_text(encoding="utf-8")) == {
    "version": 1,
    "agents": [{"source": "helper.md", "output": "helper.toml", "name": "helper"}],
}
if sys.platform != "win32":
    assert stat.S_IMODE(agent_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(manifest_path.stat().st_mode) == 0o600
PY
  if [[ -e "$home/.codex/agents/nested.toml" || -e "$home/.codex/agents/nested/helper.toml" ]]; then
    echo "Expected Codex conversion to ignore nested Markdown agents." >&2
    exit 1
  fi
  first_agent="$(<"$home/.codex/agents/helper.toml")"
  first_manifest="$(<"$home/.codex/agents/.skills-repo-agents.json")"

  env -u CODEX_HOME HOME="$home" bash "$repo/scripts/install.sh" >/dev/null
  assert_equals "$first_agent" "$(<"$home/.codex/agents/helper.toml")" "Expected a second Codex install to leave helper.toml unchanged."
  assert_equals "$first_manifest" "$(<"$home/.codex/agents/.skills-repo-agents.json")" "Expected a second Codex install to leave the agent manifest unchanged."
}

test_codex_agents_fail_before_copying_other_assets() {
  local workdir
  local repo
  local home

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"
  create_fixture_repo "$repo"
  printf '%s\n' '---' 'name: helper' '---' 'Invalid fixture.' > "$repo/agents/helper.md"

  if env -u CODEX_HOME HOME="$home" bash "$repo/scripts/install.sh" >"$workdir/stdout" 2>"$workdir/stderr"; then
    echo "Expected invalid Codex agent source to fail installation." >&2
    exit 1
  fi
  assert_file_contains "$workdir/stderr" "helper.md" "Expected the invalid Codex source diagnostic on stderr."
  for path in "$home/.agents/skills" "$home/.gemini/agents" "$home/.copilot/agents" "$home/.codex/hooks"; do
    if [[ -e "$path" ]]; then
      echo "Expected invalid Codex source to stop before copying $path." >&2
      exit 1
    fi
  done
}

test_codex_home_override_selects_one_agent_destination() {
  local workdir
  local repo
  local home
  local codex_home

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"
  codex_home="$workdir/custom-codex"
  create_fixture_repo "$repo"

  HOME="$home" CODEX_HOME="$codex_home" bash "$repo/scripts/install.sh" >/dev/null
  if [[ ! -f "$codex_home/agents/helper.toml" ]]; then
    echo "Expected CODEX_HOME to select the custom Codex agents destination." >&2
    exit 1
  fi
  if [[ -e "$home/.codex/agents/helper.toml" ]]; then
    echo "Expected no duplicate Codex agent under the default home destination." >&2
    exit 1
  fi
}

test_installs_codex_hook_and_global_configuration() {
  local workdir
  local repo
  local home

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"

  create_fixture_repo "$repo"
  mkdir -p "$home/.codex"
  printf '%s\n' 'Stale Codex instructions.' > "$home/.codex/AGENTS.md"

  HOME="$home" bash "$repo/scripts/install.sh" >/dev/null

  if [[ "$(<"$home/.codex/AGENTS.md")" != "$(<"$repo/.codex/AGENTS.md")" ]]; then
    echo "Expected the global Codex instructions to be replaced from the maintained source." >&2
    exit 1
  fi

  if [[ ! -x "$home/.codex/hooks/load-required-skills.py" ]]; then
    echo "Expected the Codex required-skills hook to be installed and executable." >&2
    exit 1
  fi
  for installed in auto-index-brain.py inject-brain.py scan-secrets.py scan-status.py tool-guard.py helpers/common.py helpers/audit.py helpers/tool_guard_policy.py helpers/scan_types.py helpers/scan_reporting.py helpers/scan_allowlist.py helpers/scan_stream.py helpers/scan_git.py helpers/scan_native_file.py helpers/scan_native_process.py helpers/scan_audit.py helpers/scan_engine.py; do
    if [[ ! -x "$home/.codex/hooks/$installed" ]]; then
      echo "Expected maintained Codex hook to be installed and executable: $installed" >&2
      exit 1
    fi
    cmp "$repo/.codex/hooks/$installed" "$home/.codex/hooks/$installed"
  done
  python3 - "$home" <<'PY'
import json
import os
from pathlib import Path
import subprocess
import sys

home = Path(sys.argv[1])
operation = ''.join(map(chr, (103,105,116,32,112,117,115,104,32,45,45,102,111,114,99,101,32,111,114,105,103,105,110,32,109,97,105,110)))
for provider in ('copilot', 'gemini', 'codex'):
    script = home / ('.codex/hooks/tool-guard.py' if provider == 'codex' else f'.{provider}/hooks/scripts/tool-guard.py')
    for command, expected in (('echo safe', 'allow'), (operation, 'deny')):
        if provider == 'copilot':
            payload = {'hook_event_name': 'preToolUse', 'toolName': 'bash', 'toolArgs': {'command': command}}
        else:
            payload = {'hook_event_name': 'PreToolUse' if provider == 'codex' else 'BeforeTool',
                       'tool_name': 'Bash' if provider == 'codex' else 'run_shell_command', 'tool_input': {'command': command}}
        env = {**os.environ, 'HOME': str(home), 'GUARD_MODE': 'block',
               'TOOL_GUARD_LOG_DIR': str(home / ('guard-install-test-' + provider)), 'AUDIT_LOG': str(home / 'guard-audit.log')}
        env.pop('SKIP_TOOL_GUARD', None)
        env.pop('TOOL_GUARD_ALLOWLIST', None)
        result = subprocess.run([sys.executable, '-I', '-S', '-B', str(script)],
                                input=json.dumps(payload), capture_output=True, text=True, env=env, timeout=5)
        assert result.returncode == 0, (provider, result.stderr)
        response = json.loads(result.stdout)
        actual = (response.get('permissionDecision') if provider == 'copilot' else response.get('decision')
                  if provider == 'gemini' else 'allow' if response == {} else response['hookSpecificOutput']['permissionDecision'])
        assert actual == expected, (provider, response)
PY
  if [[ -e "$home/.codex/hooks.json.bak" ]]; then
    echo "Expected a fresh Codex install not to create a backup." >&2
    exit 1
  fi

  python3 - "$home/.codex/hooks.json" "$home" <<'PY'
import json
import stat
import sys
from pathlib import Path

with open(sys.argv[1], encoding="utf-8") as handle:
    config = json.load(handle)

assert stat.S_IMODE(Path(sys.argv[1]).stat().st_mode) == 0o600
groups = config["hooks"]["SessionStart"]
handler = groups[0]["hooks"][0]
assert handler["command"] == "python3 ~/.codex/hooks/load-required-skills.py"
assert handler["commandWindows"] == 'py -3 "%USERPROFILE%\\.codex\\hooks\\load-required-skills.py"'
stop_commands = [hook["command"] for hook in config["hooks"]["Stop"][0]["hooks"]]
assert any(command.endswith("/scan-status.py") and " -I -S -B " in command for command in stop_commands)
assert sum(hook["command"].endswith("/scan-status.py") and " -I -S -B " in hook["command"] for group in config["hooks"]["Stop"] for hook in group["hooks"]) == 1
PY
}

test_preserves_unrelated_codex_configuration_and_replaces_owned_handler() {
  local workdir
  local repo
  local home

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"
  create_fixture_repo "$repo"
  mkdir -p "$home/.codex"
  cat > "$home/.codex/hooks.json" <<'EOF'
{
  "setting": {"keep": true},
  "hooks": {
    "BeforeTool": [{"hooks": [{"type": "command", "command": "echo keep"}]}],
    "SessionStart": [
      {"matcher": "startup", "hooks": [
        {"type": "command", "command": "echo keep"},
        {"type": "command", "command": "python3 ~/.CODEX/hooks/load-required-skills.py"},
        {"type": "command", "command": "echo ~/.codex/hooks/load-required-skills.py"},
        {"type": "command", "command": "python3 /user/hooks/load-required-skills.py"},
        {"type": "command", "command": "python3 ~/.codex/hooks/load-required-skills.py", "commandWindows": "py -3 \"%USERPROFILE%\\.codex\\hooks\\load-required-skills.py\""}
      ]},
      {"matcher": "resume", "hooks": []},
      {"matcher": "clear", "hooks": [
        {"type": "command", "commandWindows": "py -3 \"C:\\user\\load-required-skills.py\""}
      ]}
    ]
  }
}
EOF

  HOME="$home" bash "$repo/scripts/install.sh" >/dev/null

  python3 - "$home/.codex/hooks.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    config = json.load(handle)

assert config["setting"] == {"keep": True}
assert config["hooks"]["BeforeTool"] == [{"hooks": [{"type": "command", "command": "echo keep"}]}]
groups = config["hooks"]["SessionStart"]
assert groups[0]["hooks"] == [
    {"type": "command", "command": "echo keep"},
    {"type": "command", "command": "python3 ~/.CODEX/hooks/load-required-skills.py"},
    {"type": "command", "command": "echo ~/.codex/hooks/load-required-skills.py"},
    {"type": "command", "command": "python3 /user/hooks/load-required-skills.py"},
]
assert groups[1] == {"matcher": "resume", "hooks": []}
assert groups[2]["hooks"] == [
    {"type": "command", "commandWindows": 'py -3 "C:\\user\\load-required-skills.py"'},
]
assert groups[3]["hooks"][0]["command"] == "python3 ~/.codex/hooks/load-required-skills.py"
PY
}

test_codex_config_backup_is_bounded_and_idempotent() {
  local workdir
  local repo
  local home
  local backup_before

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"
  create_fixture_repo "$repo"
  mkdir -p "$home/.codex"
  printf '%s\n' '{"existing": 1}' > "$home/.codex/hooks.json"

  HOME="$home" bash "$repo/scripts/install.sh" >/dev/null
  backup_before="$(<"$home/.codex/hooks.json.bak")"
  assert_equals '{"existing": 1}' "$backup_before" "Expected backup to contain the previous valid config."

  python3 - "$home/.codex/hooks.json" "$home/.codex/hooks.json.bak" <<'PY'
import stat
import sys
from pathlib import Path

for raw_path in sys.argv[1:]:
    mode = stat.S_IMODE(Path(raw_path).stat().st_mode)
    assert mode == 0o600, f"Expected owner-only mode for {raw_path}, got {oct(mode)}"
PY

  HOME="$home" bash "$repo/scripts/install.sh" >/dev/null
  assert_equals "$backup_before" "$(<"$home/.codex/hooks.json.bak")" "Expected no backup churn on an idempotent install."

  chmod 644 "$home/.codex/hooks.json"
  HOME="$home" bash "$repo/scripts/install.sh" >/dev/null
  python3 - "$home/.codex/hooks.json" <<'PY'
import stat
import sys
from pathlib import Path

assert stat.S_IMODE(Path(sys.argv[1]).stat().st_mode) == 0o600
PY
  assert_equals "$backup_before" "$(<"$home/.codex/hooks.json.bak")" "Expected a permission-only repair not to churn the backup."

  python3 - "$home/.codex/hooks.json" <<'PY'
import json
import sys

path = sys.argv[1]
with open(path, encoding="utf-8") as handle:
    config = json.load(handle)
config["hooks"]["SessionStart"][0]["hooks"][0]["timeout"] = 4
with open(path, "w", encoding="utf-8") as handle:
    json.dump(config, handle)
PY
  expected_previous="$(<"$home/.codex/hooks.json")"
  HOME="$home" bash "$repo/scripts/install.sh" >/dev/null
  assert_equals "$expected_previous" "$(<"$home/.codex/hooks.json.bak")" "Expected backup to refresh only for a real config change."

  if compgen -G "$home/.codex/.hooks.json.*.tmp" > /dev/null; then
    echo "Expected the Codex config merger to clean same-directory temporary files." >&2
    exit 1
  fi
}

test_rejects_invalid_codex_configuration_without_mutation_and_can_retry() {
  local workdir
  local repo
  local home
  local malformed

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"
  create_fixture_repo "$repo"
  mkdir -p "$home/.codex"
  malformed='{"hooks":'
  printf '%s\n' "$malformed" > "$home/.codex/hooks.json"

  if HOME="$home" bash "$repo/scripts/install.sh" >/dev/null 2>&1; then
    echo "Expected malformed Codex JSON to reject installation." >&2
    exit 1
  fi
  assert_equals "$malformed" "$(<"$home/.codex/hooks.json")" "Expected malformed Codex config to remain unchanged."
  if [[ -e "$home/.codex/hooks/scan-secrets.py" ]]; then
    echo "Expected malformed Codex config to stop before copying hook files." >&2
    exit 1
  fi
  if [[ -e "$home/.codex/hooks.json.bak" ]]; then
    echo "Expected no backup for a malformed Codex config." >&2
    exit 1
  fi

  printf '%s\n' '[]' > "$home/.codex/hooks.json"
  if HOME="$home" bash "$repo/scripts/install.sh" >/dev/null 2>&1; then
    echo "Expected a non-object Codex config to reject installation." >&2
    exit 1
  fi
  assert_equals '[]' "$(<"$home/.codex/hooks.json")" "Expected non-object Codex config to remain unchanged."

  printf '%s\n' '{"afterFailure": true}' > "$home/.codex/hooks.json"
  HOME="$home" bash "$repo/scripts/install.sh" >/dev/null
  python3 - "$home/.codex/hooks.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    assert "SessionStart" in json.load(handle)["hooks"]
PY
}

test_refuses_symlinked_codex_hook_destination() {
  local workdir
  local repo
  local home
  local outside_hook

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"
  outside_hook="$workdir/outside-hook.py"
  create_fixture_repo "$repo"
  mkdir -p "$home/.codex/hooks"
  printf '%s\n' 'external hook' > "$outside_hook"
  chmod 600 "$outside_hook"
  ln -s "$outside_hook" "$home/.codex/hooks/load-required-skills.py"

  if HOME="$home" bash "$repo/scripts/install.sh" >/dev/null 2>&1; then
    echo "Expected installation to refuse a symlinked Codex hook destination." >&2
    exit 1
  fi
  assert_equals 'external hook' "$(<"$outside_hook")" "Expected the external hook target to remain unchanged."
  [[ -L "$home/.codex/hooks/load-required-skills.py" ]] || {
    echo "Expected the installed hook symlink to remain intact after refusal." >&2
    exit 1
  }
  python3 - "$outside_hook" <<'PY'
import pathlib
import stat
import sys

assert stat.S_IMODE(pathlib.Path(sys.argv[1]).stat().st_mode) == 0o600
PY
}

test_merger_refuses_symlinked_codex_config_destinations() {
  local workdir
  local repo
  local case_dir
  local destination
  local target
  local status

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  create_fixture_repo "$repo"

  for case_name in unchanged changed dangling; do
    case_dir="$workdir/$case_name"
    destination="$case_dir/hooks.json"
    target="$case_dir/target.json"
    mkdir -p "$case_dir"
    if [[ "$case_name" == "unchanged" ]]; then
      cp -p "$repo/.codex/global-hooks.json" "$target"
      chmod 644 "$target"
    elif [[ "$case_name" == "changed" ]]; then
      printf '%s\n' '{"preserve": true}' > "$target"
      chmod 640 "$target"
    fi
    ln -s "$target" "$destination"

    status=0
    python3 "$repo/scripts/install-codex-hooks.py" \
      --template "$repo/.codex/global-hooks.json" \
      --destination "$destination" >/dev/null 2>&1 || status=$?
    [[ "$status" -ne 0 ]] || {
      echo "Expected merger to refuse the $case_name symlinked Codex config destination." >&2
      exit 1
    }
    [[ -L "$destination" ]] || {
      echo "Expected the $case_name destination symlink to remain intact." >&2
      exit 1
    }
    [[ ! -e "$case_dir/hooks.json.bak" ]] || {
      echo "Expected no backup when refusing the $case_name destination symlink." >&2
      exit 1
    }
  done

  python3 - "$workdir/unchanged/target.json" "$workdir/changed/target.json" <<'PY'
import pathlib
import stat
import sys

unchanged = pathlib.Path(sys.argv[1])
changed = pathlib.Path(sys.argv[2])
assert stat.S_IMODE(unchanged.stat().st_mode) == 0o644
assert stat.S_IMODE(changed.stat().st_mode) == 0o640
assert '"preserve": true' in changed.read_text(encoding="utf-8")
assert not pathlib.Path(changed.parent.parent / "dangling" / "target.json").exists()
PY
}

test_installed_hooks_are_executable() {
  local unicode_py unicode_sh
  local hook_path
  local hook_paths=(
    .gemini/hooks/scripts/test-hook.py
    .copilot/hooks/scripts/test-hook.py
    .gemini/hooks/scripts/test-hook.sh
    .copilot/hooks/scripts/test-hook.sh
  )
  local workdir
  local repo
  local home

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"

  create_fixture_repo "$repo"

  for hook_path in "${hook_paths[@]}"; do
    chmod 644 "$repo/$hook_path"
  done
  unicode_py="$(python3 -c 'print("not-hook.p\u00ady")')"
  unicode_sh="$(python3 -c 'print("not-hook.s\u00adh")')"
  printf '%s\n' 'Keep original mode.' > "$repo/.copilot/hooks/scripts/$unicode_py"
  printf '%s\n' 'Keep original mode.' > "$repo/.gemini/hooks/scripts/$unicode_sh"
  chmod 604 "$repo/.copilot/hooks/scripts/$unicode_py" "$repo/.gemini/hooks/scripts/$unicode_sh"

  HOME="$home" bash "$repo/scripts/install.sh" >/dev/null

  for hook_path in "${hook_paths[@]}"; do
    if [[ ! -x "$home/$hook_path" ]]; then
      echo "Expected ~/$hook_path to be executable." >&2
      exit 1
    fi
  done
  python3 - "$home/.copilot/hooks/scripts/$unicode_py" "$home/.gemini/hooks/scripts/$unicode_sh" <<'PY'
import stat
import sys
from pathlib import Path
for filename in sys.argv[1:]:
    assert stat.S_IMODE(Path(filename).stat().st_mode) == 0o604, filename
PY
}

test_excludes_and_prunes_skill_evals() {
  local workdir
  local repo
  local home
  local copied_skill
  local copied_existing_note

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"

  create_fixture_repo "$repo"
  mkdir -p "$home/.agents/skills/alpha/evals"
  printf '%s\n' 'stale eval content' > "$home/.agents/skills/alpha/evals/stale.txt"
  printf '%s\n' 'keep this installed note' > "$home/.agents/skills/alpha/existing-note.txt"

  HOME="$home" bash "$repo/scripts/install.sh" >/dev/null

  if [[ ! -f "$home/.agents/skills/alpha/SKILL.md" ]]; then
    echo "Expected skills/default/alpha to install at ~/.agents/skills/alpha without a category wrapper." >&2
    exit 1
  fi

  if [[ -e "$home/.agents/skills/default" || -e "$home/.agents/skills/forest-service" ]]; then
    echo "Expected category directories and the empty Forest Service marker not to install as skills." >&2
    exit 1
  fi

  copied_skill="$(<"$home/.agents/skills/alpha/SKILL.md")"
  copied_existing_note="$(<"$home/.agents/skills/alpha/existing-note.txt")"
  assert_equals $'---\nname: alpha\n---\nStandalone.' "$copied_skill" "Expected non-evals skill content to remain installed."
  assert_equals "keep this installed note" "$copied_existing_note" "Expected existing non-evals installed content to remain after eval cleanup."

  if [[ -d "$home/.agents/skills/alpha/evals" ]]; then
    echo "Expected ~/.agents/skills/alpha/evals to be removed during install." >&2
    exit 1
  fi

  if [[ -e "$home/.agents/skills/beta-workspace" ]]; then
    echo "Expected *-workspace skills to remain excluded from top-level selection." >&2
    exit 1
  fi

  if [[ -e "$home/.agents/skills/archive" ]]; then
    echo "Expected archive entries to remain excluded from top-level selection." >&2
    exit 1
  fi
}

cleanup_reference_fixture() {
  if [[ -n "${workdir:-}" ]]; then
    chmod -R u+rwX "$workdir"
    rm -rf -- "$workdir"
  fi
}

setup_reference_fixture() {
  # These are caller-declared locals in each reference-test subshell.
  workdir="$(setup_test_workdir)"
  repo="$workdir/repo"
  home="$workdir/home"
  create_fixture_repo "$repo"
}

set_reference_test_environment() {
  local reference_home="$1"
  local reference_codex="$2"
  export HOME="$reference_home" USERPROFILE="$reference_home" APPDATA="$reference_home/AppData/Roaming" LOCALAPPDATA="$reference_home/AppData/Local" XDG_CONFIG_HOME="$reference_home/xdg-config" XDG_CACHE_HOME="$reference_home/xdg-cache" XDG_DATA_HOME="$reference_home/xdg-data" CODEX_HOME="$reference_codex"
}

write_excluded_skill_documents() {
  local skill_directory="$1"
  local license
  printf '%s\n' 'excluded readme' > "$skill_directory/README.md"
  for license in LICENSE.txt LICENSE.md; do
    printf '%s\n' 'excluded license' > "$skill_directory/$license"
  done
}

assert_read_only_hard_link_refusal() {
  assert_equals 1 "$1" "$5"
  assert_file_contains "$2" 'Refusing to change read-only hard-linked file' "$6"
  assert_tree_unchanged "$3" "$4" "$7"
}

test_rebases_shared_reference_links_for_flat_installed_skills() (
  local workdir repo home installed_skill

  trap cleanup_reference_fixture EXIT
  setup_reference_fixture
  printf '%s\n' '---' 'name: alpha' '---' 'See `../../../references/shared.md`, [single](./../../../references/shared.md), and [repeated](././../../../references/shared.md).' 'Keep ~/.agents/skills/alpha and example/../../../references/shared.md unchanged.' > "$repo/skills/default/alpha/SKILL.md"
  mkdir -p "$repo/skills/default/alpha/nested"
  printf '%s\n' '[nested](./../../../../references/shared.md)' > "$repo/skills/default/alpha/nested/note.markdown"
  printf '%s\n' 'Shared reference.' > "$repo/references/shared.md"
  local source_before
  source_before="$(tree_fingerprint "$repo/skills/default/alpha")"

  set_reference_test_environment "$home" "$workdir/codex"
  bash "$repo/scripts/install.sh" >/dev/null

  installed_skill="$(<"$home/.agents/skills/alpha/SKILL.md")"
  assert_equals \
    $'---\nname: alpha\n---\nSee `../../references/shared.md`, [single](../../references/shared.md), and [repeated](../../references/shared.md).\nKeep ~/.agents/skills/alpha and example/../../../references/shared.md unchanged.' \
    "$installed_skill" \
    "Expected source links to shared references to be rebased for the flat installed skill path."

  if [[ ! -f "$home/.agents/skills/alpha/../../references/shared.md" ]]; then
    echo "Expected the installed shared reference link to resolve inside ~/.agents/references." >&2
    exit 1
  fi
  assert_equals '[nested](../../../references/shared.md)' "$(<"$home/.agents/skills/alpha/nested/note.markdown")" 'Expected leading ./ in nested Markdown to rebase.'
  test -f "$home/.agents/skills/alpha/nested/../../../references/shared.md"
  assert_tree_unchanged "$source_before" "$repo/skills/default/alpha" 'Expected rebasing not to mutate source bytes or modes.'
)

test_rebases_read_only_markdown_and_preserves_modes_on_repeat() (
  local workdir repo home before installed_before
  trap cleanup_reference_fixture EXIT
  setup_reference_fixture
  mkdir -p "$repo/skills/default/locked/nested" "$repo/skills/default/locked/evals/nested" "$home/.agents/skills/locked"
  printf '%s\n' 'Reference notes.' > "$repo/references/notes.md"
  printf 'See [shared](../../../references/notes.md).\r\nKeep unicode: café.\r\n' > "$repo/skills/default/locked/SKILL.md"
  printf '%s\n' '[nested](../../../../references/notes.md)' > "$repo/skills/default/locked/nested/note.md"
  printf '%s\n' 'excluded eval fixture' > "$repo/skills/default/locked/evals/nested/evals.json"
  write_excluded_skill_documents "$repo/skills/default/locked"
  printf '%s\n' 'stale writable copy' > "$home/.agents/skills/locked/SKILL.md"
  chmod 640 "$home/.agents/skills/locked/SKILL.md"
  chmod 770 "$home/.agents/skills/locked"
  chmod -R a-w "$repo/skills/default/locked"
  before="$(tree_fingerprint "$repo/skills/default/locked")"
  set_reference_test_environment "$home" "$workdir/codex"
  bash "$repo/scripts/install.sh" >/dev/null
  python3 - "$repo" "$home" <<'PY'
from pathlib import Path
import stat
import sys
source = Path(sys.argv[1]) / 'skills/default/locked'
installed = Path(sys.argv[2]) / '.agents/skills/locked'
for relative, prefix in [('SKILL.md', '../../'), ('nested/note.md', '../../../')]:
    target = installed / relative
    expected = (source / relative).read_bytes().replace(b'../../../references/', b'../../references/', 1)
    assert target.read_bytes() == expected, relative
    assert stat.S_IMODE(target.stat().st_mode) == 0o444, relative
    assert (target.parent / f'{prefix}references/notes.md').resolve() == (installed.parent.parent / 'references/notes.md').resolve()
    assert (target.parent / f'{prefix}references/notes.md').is_file()
for path in (installed, installed / 'nested'):
    assert stat.S_IMODE(path.stat().st_mode) == 0o555, path
assert sorted(p.relative_to(installed).as_posix() for p in installed.rglob('*')) == ['SKILL.md', 'nested', 'nested/note.md']
PY
  installed_before="$(tree_fingerprint "$home/.agents/skills/locked")"
  bash "$repo/scripts/install.sh" >/dev/null
  assert_tree_unchanged "$before" "$repo/skills/default/locked" 'Expected read-only source bytes and directory/file modes to remain unchanged.'
  assert_tree_unchanged "$installed_before" "$home/.agents/skills/locked" 'Expected repeat installs to preserve rebased bytes and modes without temporary artifacts.'

  # A public copy failure must undo temporary permission elevation.
  chmod u+w "$repo/skills/default/locked"
  printf '%s\n' 'unreadable source' > "$repo/skills/default/locked/unreadable.txt"
  chmod 000 "$repo/skills/default/locked/unreadable.txt"
  chmod 555 "$repo/skills/default/locked"
  if bash "$repo/scripts/install.sh" >"$workdir/out" 2>"$workdir/err"; then
    echo 'Expected the unreadable source to stop installation.' >&2
    exit 1
  fi
  python3 - "$home/.agents/skills/locked" <<'PY'
from pathlib import Path
import stat
import sys
root = Path(sys.argv[1])
for relative, mode in [('.', 0o555), ('nested', 0o555), ('SKILL.md', 0o444), ('nested/note.md', 0o444)]:
    assert stat.S_IMODE((root / relative).stat().st_mode) == mode, relative
assert not any(p.name.startswith('.rebase-') for p in root.rglob('*'))
PY
)

test_actual_addy_shared_references_resolve_after_install() (
  local workdir repo home before name
  trap cleanup_reference_fixture EXIT
  setup_reference_fixture
  for name in addy-code-review-and-quality addy-performance-optimization addy-security-and-hardening; do
    mkdir -p "$repo/skills/default/$name"
    cp -p "$REPO_ROOT/skills/default/$name/SKILL.md" "$repo/skills/default/$name/SKILL.md"
  done
  cp -p "$REPO_ROOT/references/security-checklist.md" "$REPO_ROOT/references/performance-checklist.md" "$repo/references/"
  before="$(tree_fingerprint "$repo/skills")"
  set_reference_test_environment "$home" "$workdir/codex"
  bash "$repo/scripts/install.sh" >/dev/null
  python3 - "$repo" "$home" <<'PY'
from pathlib import Path
import re
import sys
repo, home = map(Path, sys.argv[1:])
count = 0
for name in ('addy-code-review-and-quality', 'addy-performance-optimization', 'addy-security-and-hardening'):
    source = repo / 'skills/default' / name / 'SKILL.md'
    installed = home / '.agents/skills' / name / 'SKILL.md'
    links = re.findall(r'`(\.\./\.\./\.\./references/[^`]+)`', source.read_text())
    assert links, name
    assert installed.read_bytes() == source.read_bytes().replace(b'../../../references/', b'../../references/'), name
    for link in links:
        source_target = (source.parent / link).resolve()
        installed_target = (installed.parent / link.removeprefix('../')).resolve()
        assert source_target.parent == (repo / 'references').resolve()
        assert installed_target.parent == (home / '.agents/references').resolve()
        assert source_target.read_bytes() == installed_target.read_bytes()
        count += 1
assert count == 8, count
PY
  assert_tree_unchanged "$before" "$repo/skills" 'Expected actual Addy skill definitions to remain unchanged in source.'
)

test_prunes_without_optional_shared_references() (
  local workdir repo home pass name
  trap cleanup_reference_fixture EXIT
  setup_reference_fixture
  rm -rf -- "$repo/references"
  printf '%s\n' '---' 'name: alpha' '---' 'See ../../../references/unavailable.md.' > "$repo/skills/default/alpha/SKILL.md"
  write_excluded_skill_documents "$repo/skills/default/alpha"
  set_reference_test_environment "$home" "$workdir/codex"
  for pass in first repeat; do
    bash "$repo/scripts/install.sh" >/dev/null
    assert_equals "$(<"$repo/skills/default/alpha/SKILL.md")" "$(<"$home/.agents/skills/alpha/SKILL.md")" 'Expected absent shared references to skip rebasing.'
    for name in evals README.md LICENSE.txt LICENSE.md; do
      test ! -e "$home/.agents/skills/alpha/$name"
    done
  done
)

test_pruning_read_only_hard_link_preserves_external_inode() (
  local workdir repo home outside
  trap cleanup_reference_fixture EXIT
  setup_reference_fixture
  outside="$workdir/external.md"
  mkdir -p "$home/.agents/skills/alpha/evals"
  printf '%s\n' 'external bytes must remain untouched' > "$outside"
  chmod 444 "$outside"
  ln "$outside" "$home/.agents/skills/alpha/evals/stale.md"
  local before_inode
  before_inode="$(python3 -c 'import os,sys; print(os.stat(sys.argv[1]).st_ino)' "$outside")"
  set_reference_test_environment "$home" "$workdir/codex"
  bash "$repo/scripts/install.sh" >/dev/null
  python3 - "$outside" "$before_inode" "$home" <<'PY'
from pathlib import Path
import stat
import sys
outside = Path(sys.argv[1])
assert outside.read_bytes() == b'external bytes must remain untouched\n'
assert outside.stat().st_ino == int(sys.argv[2])
assert stat.S_IMODE(outside.stat().st_mode) == 0o444
assert outside.stat().st_nlink == 1
assert not (Path(sys.argv[3]) / '.agents/skills/alpha/evals').exists()
PY
)

test_read_only_hard_link_copy_refuses_external_mutation() (
  local workdir repo home outside before status
  trap cleanup_reference_fixture EXIT
  setup_reference_fixture
  outside="$workdir/external.md"
  mkdir -p "$home/.agents/skills/alpha"
  printf '%s\n' 'external bytes must remain untouched; see ../../../references/notes.md.' > "$outside"
  chmod 444 "$outside"
  ln "$outside" "$home/.agents/skills/alpha/SKILL.md"
  before="$(tree_fingerprint "$outside")"
  status=0
  set_reference_test_environment "$home" "$workdir/codex"
  bash "$repo/scripts/install.sh" >"$workdir/out" 2>"$workdir/err" || status=$?
  assert_read_only_hard_link_refusal "$status" "$workdir/err" "$before" "$outside" \
    'Expected a read-only hard-linked destination to stop copying before external mutation.' \
    'Expected an actionable hard-link refusal.' \
    'Expected external hard-linked bytes and mode unchanged after copy refusal.'
  status=0
  python3 -B "$repo/scripts/rebase-skill-references.py" \
    --source-dir "$repo/skills/default/alpha" \
    --destination-dir "$home/.agents/skills/alpha" \
    --references-source "$repo/references" \
    --references-destination "$home/.agents/references" >"$workdir/out" 2>"$workdir/err" || status=$?
  assert_read_only_hard_link_refusal "$status" "$workdir/err" "$before" "$outside" \
    'Expected direct rebasing to refuse a read-only shared inode before permission changes.' \
    'Expected the direct rebasing refusal to name the unsafe inode.' \
    'Expected direct rebasing refusal to leave external bytes and mode unchanged.'
  python3 - "$outside" "$home/.agents/skills/alpha/SKILL.md" <<'PY'
from pathlib import Path
import sys
outside, installed = map(Path, sys.argv[1:])
assert installed.stat().st_ino == outside.stat().st_ino
assert outside.stat().st_nlink == 2
PY
)

test_root_linked_skill_is_preserved_without_external_mutation() {
  local workdir repo home external_skill nested_target before nested_before installed_skill

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"
  external_skill="$workdir/external-skill"
  nested_target="$workdir/nested-link-target"

  create_fixture_repo "$repo"
  mkdir -p "$external_skill/evals"
  printf '%s\n' '---' 'name: linked-skill' '---' 'See [the shared reference](../repo/references/shared.md).' > "$external_skill/SKILL.md"
  printf '%s\n' 'external evals must remain untouched' > "$external_skill/evals/keep.txt"
  mkdir -p "$nested_target"
  printf '%s\n' 'See [the shared reference](../../../../references/shared.md).' > "$nested_target/note.md"
  ln -s "$external_skill" "$repo/skills/default/linked-skill"
  ln -s "$nested_target" "$repo/skills/default/alpha/linked-dir"
  before="$(tree_fingerprint "$external_skill")"
  nested_before="$(tree_fingerprint "$nested_target")"

  HOME="$home" bash "$repo/scripts/install.sh" >/dev/null

  installed_skill="$home/.agents/skills/linked-skill"
  if [[ ! -L "$installed_skill" ]]; then
    echo "Expected a root-linked skill to remain a symlink after installation." >&2
    exit 1
  fi
  assert_equals "$external_skill" "$(readlink "$installed_skill")" "Expected a root-linked skill to retain its raw target."
  python3 -B "$repo/scripts/rebase-skill-references.py" \
    --source-dir "$repo/skills/default/linked-skill" \
    --destination-dir "$installed_skill" \
    --references-source "$repo/references" \
    --references-destination "$home/.agents/references"
  assert_tree_unchanged "$before" "$external_skill" "Expected installation to leave a root-linked skill target byte-for-byte unchanged."
  assert_tree_unchanged "$nested_before" "$nested_target" "Expected reference rebasing to leave a nested linked directory target byte-for-byte unchanged."
  assert_equals 'See [the shared reference](../../../../references/shared.md).' "$(<"$nested_target/note.md")" "Expected reference rebasing to skip Markdown reached through a nested directory link."
}

test_copies_full_gemini_tree() {
  local workdir
  local repo
  local home
  local copied_gemini
  local copied_agent
  local copied_nested_agent
  local copied_copilot_agent
  local copied_copilot_nested_agent
  local copied_policy
  local copied_hidden
  local copied_hook

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"

  create_fixture_repo "$repo"

  HOME="$home" bash "$repo/scripts/install.sh" >/dev/null

  copied_gemini="$(<"$home/.gemini/GEMINI.md")"
  copied_agent="$(<"$home/.gemini/agents/helper.md")"
  copied_nested_agent="$(<"$home/.gemini/agents/nested/helper.md")"
  copied_copilot_agent="$(<"$home/.copilot/agents/helper.md")"
  copied_copilot_nested_agent="$(<"$home/.copilot/agents/nested/helper.md")"
  copied_policy="$(<"$home/.gemini/policies/plan-custom-directory.toml")"
  copied_hidden="$(<"$home/.gemini/.hidden-note")"
  copied_hook="$(<"$home/.copilot/hooks/test-hook.sh")"
  copied_global_settings="$(<"$home/.gemini/settings.json")"

  assert_equals "$(<"$repo/.gemini/GEMINI.md")" "$copied_gemini" "Expected GEMINI.md to be copied into ~/.gemini."
  assert_equals $'---\nname: helper\ndescription: Fixture helper agent.\n---\nUse alpha.' "$copied_agent" "Expected agents to be copied into ~/.gemini/agents."
  assert_equals $'---\nname: nested-helper\ndescription: Nested fixture helper agent.\n---\nUse alpha deeply.' "$copied_nested_agent" "Expected nested agents to be copied recursively into ~/.gemini/agents."
  assert_equals $'---\nname: helper\ndescription: Fixture helper agent.\n---\nUse alpha.' "$copied_copilot_agent" "Expected agents to be copied into ~/.copilot/agents."
  assert_equals $'---\nname: nested-helper\ndescription: Nested fixture helper agent.\n---\nUse alpha deeply.' "$copied_copilot_nested_agent" "Expected nested agents to be copied recursively into ~/.copilot/agents."
  assert_equals "Nested policy." "$copied_policy" "Expected nested Gemini files to be copied recursively."
  assert_equals "Hidden note." "$copied_hidden" "Expected hidden Gemini files to be copied recursively."
  assert_equals $'#!/bin/bash\necho hook' "$copied_hook" "Expected hooks to be copied into ~/.copilot/hooks."
  python3 - "$home/.gemini/settings.json" <<'PY'
import json
import sys
from pathlib import Path
assert json.loads(Path(sys.argv[1]).read_text()) == {'global': 'settings'}
PY
  assert_equals "$(<"$repo/.copilot/copilot-instructions.md")" "$(<"$home/.copilot/copilot-instructions.md")" "Expected Copilot instructions to be copied into ~/.copilot."
  assert_equals "$(<"$repo/.codex/AGENTS.md")" "$(<"$home/.codex/AGENTS.md")" "Expected Codex instructions to be copied into ~/.codex."

  if [[ -e "$home/.gemini/.gemini" ]]; then
    echo "Expected the installer to copy Gemini contents into ~/.gemini, not nest another .gemini directory." >&2
    exit 1
  fi

}

seed_cli_destinations() {
  local fixture_home="$1"
  local fixture_codex="$2"
  printf '%s\n' sentinel > "$fixture_home/sentinel"
  printf '%s\n' sentinel > "$fixture_codex/sentinel"
}

create_script_only_cli_fixture() {
  local fixture_repo="$1"
  local fixture_home="$2"
  local fixture_codex="$3"
  mkdir -p "$fixture_repo/scripts" "$fixture_home" "$fixture_codex"
  cp -p "$REPO_ROOT/scripts/install.sh" "$fixture_repo/scripts/install.sh"
  seed_cli_destinations "$fixture_home" "$fixture_codex"
}

write_regular_skill_fixture() {
  local skill_directory="$1"
  shift
  mkdir -p "$skill_directory"
  printf '%s\n' "$@" > "$skill_directory/SKILL.md"
}

test_help_without_sources_or_dependencies() {
  local workdir repo home codex before before_codex arguments status
  workdir="$(setup_test_workdir)"
  trap 'cleanup_test_workdir; trap - RETURN' RETURN
  repo="$workdir/repo"; home="$workdir/home"; codex="$workdir/codex"
  create_script_only_cli_fixture "$repo" "$home" "$codex"
  before="$(tree_fingerprint "$home")"; before_codex="$(tree_fingerprint "$codex")"
  for arguments in '-h' '--help' '--fs --help --forest-service' '--help --no-forest-service --no-forest-service'; do
    set -- $arguments
    status=0
    HOME="$home" CODEX_HOME="$codex" INSTALL_FOREST_SERVICE_SKILLS=banana bash "$repo/scripts/install.sh" "$@" >"$workdir/out" 2>"$workdir/err" || status=$?
    assert_equals 0 "$status" "Expected help to bypass missing sources/dependencies and invalid environment."
    assert_file_contains "$workdir/out" 'Usage:' 'Expected usage on stdout.'
    assert_file_contains "$workdir/out" 'Use --forest-service' 'Expected selection options in help.'
    assert_file_contains "$workdir/out" 'Examples:' 'Expected examples in help.'
    assert_equals '' "$(cat "$workdir/err")" 'Expected help stderr to be empty.'
    assert_tree_unchanged "$before" "$home" 'Expected help not to mutate home.'
    assert_tree_unchanged "$before_codex" "$codex" 'Expected help not to mutate CODEX_HOME.'
  done
}

test_explicit_forest_service_selection() {
  local workdir repo home status
  workdir="$(setup_test_workdir)"
  trap 'cleanup_test_workdir; trap - RETURN' RETURN
  repo="$workdir/repo"; home="$workdir/home"
  create_fixture_repo "$repo"
  write_regular_skill_fixture "$repo/skills/forest-service/agency-priorities" '---' 'name: unrelated-frontmatter-identity' '---' 'Agency priorities.'
  status=0
  HOME="$home" INSTALL_FOREST_SERVICE_SKILLS=banana bash "$repo/scripts/install.sh" --fs >"$workdir/out" 2>"$workdir/err" || status=$?
  assert_equals 0 "$status" 'Expected explicit selection to override invalid environment.'
  assert_equals '' "$(cat "$workdir/out")" 'Expected successful installation status only on stderr.'
  assert_file_contains "$workdir/err" 'Installed skills to' 'Expected installation progress on stderr.'
  [[ -f "$home/.agents/skills/agency-priorities/SKILL.md" ]] || { echo 'Expected flat Forest Service skill installation.' >&2; exit 1; }
  [[ -f "$home/.agents/skills/alpha/SKILL.md" ]] || { echo 'Expected default skills with Forest Service selection.' >&2; exit 1; }
}

test_selection_environment_and_repeats() {
  local workdir repo home value expected arguments status first
  workdir="$(setup_test_workdir)"
  trap 'cleanup_test_workdir; trap - RETURN' RETURN
  repo="$workdir/repo"
  create_fixture_repo "$repo"
  write_regular_skill_fixture "$repo/skills/forest-service/agency-priorities" 'Forest Service.'
  while IFS='|' read -r expected value arguments; do
    home="$workdir/home-$expected-$value-${arguments// /_}"
    # The fixture arguments are fixed literals, intentionally split into argv.
    set -- $arguments
    status=0
    (
      if [[ "$value" == unset ]]; then unset INSTALL_FOREST_SERVICE_SKILLS; else export INSTALL_FOREST_SERVICE_SKILLS="$value"; fi
      HOME="$home" bash "$repo/scripts/install.sh" "$@"
    ) >"$workdir/out" 2>"$workdir/err" || status=$?
    assert_equals 0 "$status" "Expected successful selection: $value $arguments."
    [[ -f "$home/.agents/skills/alpha/SKILL.md" ]] || { echo 'Expected default skill.' >&2; exit 1; }
    if [[ "$expected" == both ]]; then
      [[ -f "$home/.agents/skills/agency-priorities/SKILL.md" ]] || { echo "Expected Forest Service skill: $value $arguments." >&2; exit 1; }
    else
      [[ ! -e "$home/.agents/skills/agency-priorities" ]] || { echo "Expected default only: $value $arguments." >&2; exit 1; }
    fi
  done <<'CASES'
both|TrUe|
both|1|
default|unset|
default||
default|0|
default|FaLsE|
both|0|--forest-service
both|false|--fs
both|banana|--forest-service
both|banana|--fs --forest-service --fs
default|true|--no-forest-service
default|banana|--no-forest-service
default|banana|--no-forest-service --no-forest-service
CASES
  home="$workdir/repeat-home"
  HOME="$home" INSTALL_FOREST_SERVICE_SKILLS=banana bash "$repo/scripts/install.sh" --fs >"$workdir/out" 2>"$workdir/err"
  first="$(cat "$home/.agents/skills/agency-priorities/SKILL.md")"
  HOME="$home" INSTALL_FOREST_SERVICE_SKILLS=0 bash "$repo/scripts/install.sh" >"$workdir/out" 2>"$workdir/err"
  assert_equals "$first" "$(cat "$home/.agents/skills/agency-priorities/SKILL.md")" 'Expected default repeat to preserve previously installed Forest Service skills.'
}

test_invalid_selection_is_immutable() {
  local workdir repo home codex before before_codex arguments value status diagnostic
  workdir="$(setup_test_workdir)"
  trap 'cleanup_test_workdir; trap - RETURN' RETURN
  repo="$workdir/repo"; home="$workdir/home"; codex="$workdir/codex"
  create_script_only_cli_fixture "$repo" "$home" "$codex"
  before="$(tree_fingerprint "$home")"; before_codex="$(tree_fingerprint "$codex")"
  while IFS='|' read -r value diagnostic arguments; do
    set -- $arguments
    status=0
    HOME="$home" CODEX_HOME="$codex" INSTALL_FOREST_SERVICE_SKILLS="$value" bash "$repo/scripts/install.sh" "$@" >"$workdir/out" 2>"$workdir/err" || status=$?
    assert_equals 2 "$status" "Expected invalid selection to exit 2: $value $arguments."
    assert_file_contains "$workdir/err" "$diagnostic" 'Expected actionable argument/environment stderr.'
    assert_equals '' "$(cat "$workdir/out")" 'Expected no stdout for invalid selection.'
    assert_tree_unchanged "$before" "$home" 'Expected invalid selection not to mutate home.'
    assert_tree_unchanged "$before_codex" "$codex" 'Expected invalid selection not to mutate CODEX_HOME.'
  done < <(cat <<'CASES'
|Conflicting|--fs --no-forest-service
|Conflicting|--no-forest-service --forest-service
|Conflicting|--help --fs --no-forest-service
|Conflicting|-h --no-forest-service --fs
|Unknown argument|--wat
|Unknown argument|operand
|Unknown argument|--fs=true
|Unknown argument|--forest-service=1
|Unknown argument|--no-forest-service=false
|Unknown argument|--help --wat
|Unknown argument|--wat --help
|Unknown argument|--help operand
|Unknown argument|--help --fs=true
|Unknown argument|-fs
|Unknown argument|-ForestService
|Unknown argument|-help
|Unknown argument|-?
|Unknown argument|--FS
|Unknown argument|--
banana|INSTALL_FOREST_SERVICE_SKILLS|
 true|INSTALL_FOREST_SERVICE_SKILLS|
false |INSTALL_FOREST_SERVICE_SKILLS|
yes|INSTALL_FOREST_SERVICE_SKILLS|
on|INSTALL_FOREST_SERVICE_SKILLS|
2|INSTALL_FOREST_SERVICE_SKILLS|
CASES
    python3 - <<'PY'
print('|Unknown argument|--f\u00ads')
print('|Unknown argument|--hel\u200bp')
for value in ('tr\u00adue', 'tru\u200be', '1\u00ad'):
    print(f'{value}|INSTALL_FOREST_SERVICE_SKILLS|')
PY
  )
}

test_source_preflight_is_immutable() {
  local workdir repo home codex before before_codex scenario diagnostic default_diagnostic status nfc_name nfd_name
  workdir="$(setup_test_workdir)"
  trap 'cleanup_test_workdir; trap - RETURN' RETURN
  nfc_name="$(python3 -B -c 'print("caf\u00e9")')"
  nfd_name="$(python3 -B -c 'print("cafe\u0301")')"
  for scenario in missing-default missing-forest-disabled missing-forest-enabled malformed-default malformed-forest equal-name case-name nfc-nfd-disabled nfc-nfd-enabled; do
    repo="$workdir/$scenario/repo"; home="$workdir/$scenario/home"; codex="$workdir/$scenario/codex"
    create_fixture_repo "$repo"
    mkdir -p "$home" "$codex"
    seed_cli_destinations "$home" "$codex"
    # Any dependency/configuration or converter stage reached before validation is a failure.
    printf '%s\n' 'from pathlib import Path' "Path('$workdir/stage-reached').write_text('reached')" 'raise SystemExit(98)' > "$repo/scripts/configure-rtk.py"
    cp "$repo/scripts/configure-rtk.py" "$repo/scripts/install-codex-agents.py"
    set --
    default_diagnostic='skills/default/alpha'
    case "$scenario" in
      missing-default) rm -rf -- "$repo/skills/default"; diagnostic='skills/default' ;;
      missing-forest-disabled|missing-forest-enabled)
        rm -rf -- "$repo/skills/forest-service"; diagnostic='skills/forest-service'
        if [[ "$scenario" == missing-forest-enabled ]]; then set -- --fs; fi ;;
      malformed-default) mkdir -p "$repo/skills/default/incomplete"; diagnostic='skills/default/incomplete' ;;
      malformed-forest) mkdir -p "$repo/skills/forest-service/incomplete"; diagnostic='skills/forest-service/incomplete' ;;
      equal-name|case-name)
        diagnostic='skills/forest-service/alpha'
        if [[ "$scenario" == case-name ]]; then diagnostic='skills/forest-service/ALPHA'; fi
        write_regular_skill_fixture "$repo/$diagnostic" 'A different frontmatter name.' ;;
      nfc-nfd-disabled|nfc-nfd-enabled)
        # Different category parents keep both spellings representable even on
        # filesystems that collapse canonically equivalent destination names.
        default_diagnostic="skills/default/$nfc_name"; diagnostic="skills/forest-service/$nfd_name"
        write_regular_skill_fixture "$repo/$default_diagnostic" '---' 'name: default-unicode' '---' 'Default Unicode skill.'
        write_regular_skill_fixture "$repo/$diagnostic" '---' 'name: forest-unicode' '---' 'Forest Unicode skill.'
        if [[ "$scenario" == nfc-nfd-enabled ]]; then set -- --fs; fi ;;
    esac
    before="$(tree_fingerprint "$home")"; before_codex="$(tree_fingerprint "$codex")"
    status=0
    HOME="$home" CODEX_HOME="$codex" INSTALL_FOREST_SERVICE_SKILLS=0 bash "$repo/scripts/install.sh" "$@" >"$workdir/out" 2>"$workdir/err" || status=$?
    assert_equals 1 "$status" "Expected source error exit 1: $scenario."
    assert_file_contains "$workdir/err" "$diagnostic" "Expected bad source path: $scenario."
    if [[ "$scenario" == equal-name || "$scenario" == case-name || "$scenario" == nfc-nfd-* ]]; then
      assert_file_contains "$workdir/err" "$default_diagnostic" 'Expected both original collision paths.'
    fi
    assert_equals '' "$(cat "$workdir/out")" 'Expected no stdout for source errors.'
    assert_tree_unchanged "$before" "$home" 'Expected source error not to mutate home.'
    assert_tree_unchanged "$before_codex" "$codex" 'Expected source error not to mutate CODEX_HOME.'
    [[ ! -e "$workdir/stage-reached" ]] || { echo 'Expected source validation before dependency, RTK, or converter stages.' >&2; exit 1; }
  done
}

test_helper_failures_are_installer_errors() {
  local workdir repo home codex helper before before_codex status
  workdir="$(setup_test_workdir)"
  trap 'cleanup_test_workdir; trap - RETURN' RETURN
  for helper in validate-skill-sources.py configure-rtk.py generate-hooks.py install-provider-hooks.py install-codex-agents.py rebase-skill-references.py; do
    repo="$workdir/$helper/repo"; home="$workdir/$helper/home"; codex="$workdir/$helper/codex"
    create_fixture_repo "$repo"
    mkdir -p "$home" "$codex"
    seed_cli_destinations "$home" "$codex"
    printf '%s\n' 'import sys' 'print("Fixture helper status")' 'print("Fixture helper failed; repair its input.", file=sys.stderr)' 'raise SystemExit(2)' > "$repo/scripts/$helper"
    before="$(tree_fingerprint "$home")"; before_codex="$(tree_fingerprint "$codex")"
    status=0
    HOME="$home" CODEX_HOME="$codex" INSTALL_FOREST_SERVICE_SKILLS=0 bash "$repo/scripts/install.sh" >"$workdir/out" 2>"$workdir/err" || status=$?
    assert_equals 1 "$status" "Expected helper exit 2 to become installer exit 1: $helper."
    assert_file_contains "$workdir/err" 'Fixture helper failed; repair its input.' 'Expected helper diagnostic and recovery preserved.'
    assert_equals '' "$(cat "$workdir/out")" 'Expected helper status not to leak stdout.'
    case "$helper" in
      install-codex-agents.py|rebase-skill-references.py) ;;
      *)
        assert_tree_unchanged "$before" "$home" 'Expected preflight helper failure not to mutate home.'
        assert_tree_unchanged "$before_codex" "$codex" 'Expected preflight helper failure not to mutate CODEX_HOME.' ;;
    esac
  done
}

test_empty_categories_markers_and_exclusions() {
  local workdir repo home category selection status unicode_archive unicode_workspace
  workdir="$(setup_test_workdir)"
  trap 'cleanup_test_workdir; trap - RETURN' RETURN
  repo="$workdir/repo"
  create_fixture_repo "$repo"
  for category in default forest-service; do
    mkdir -p "$repo/skills/$category/archive" "$repo/skills/$category/agency-workspace" "$repo/skills/$category/weird[1]-workspace"
    printf '%s\n' 'Non-directory marker.' > "$repo/skills/$category/notes.txt"
  done
  for selection in --fs --no-forest-service; do
    home="$workdir/home-$selection"
    status=0
    HOME="$home" INSTALL_FOREST_SERVICE_SKILLS=banana bash "$repo/scripts/install.sh" "$selection" >"$workdir/out" 2>"$workdir/err" || status=$?
    assert_equals 0 "$status" 'Expected empty Forest Service category to be valid when enabled or disabled.'
    [[ -f "$home/.agents/skills/alpha/SKILL.md" ]] || { echo 'Expected flat default alpha.' >&2; exit 1; }
    for category in default forest-service .gitkeep notes.txt archive agency-workspace 'weird[1]-workspace'; do
      [[ ! -e "$home/.agents/skills/$category" ]] || { echo "Expected marker/category/exclusion omitted: $category." >&2; exit 1; }
    done
  done
  rm -rf -- "$repo/skills/default/archive"
  unicode_archive="$(python3 -c 'print("archiv\u00ade")')"
  unicode_workspace="$(python3 -c 'print("x-work\u00adspace")')"
  mkdir -p "$repo/skills/default/Archive" "$repo/skills/default/My-Workspace" "$repo/skills/forest-service/second-name" "$repo/skills/default/$unicode_archive" "$repo/skills/default/$unicode_workspace"
  for category in "$unicode_archive" "$unicode_workspace" Archive My-Workspace; do
    write_regular_skill_fixture "$repo/skills/default/$category" 'Not excluded.'
  done
  cp "$repo/skills/default/alpha/SKILL.md" "$repo/skills/forest-service/second-name/SKILL.md"
  home="$workdir/case-home"
  HOME="$home" INSTALL_FOREST_SERVICE_SKILLS=0 bash "$repo/scripts/install.sh" --fs >"$workdir/out" 2>"$workdir/err"
  for category in Archive My-Workspace second-name "$unicode_archive" "$unicode_workspace"; do
    [[ -f "$home/.agents/skills/$category/SKILL.md" ]] || { echo "Expected basename candidate despite case/frontmatter: $category." >&2; exit 1; }
  done
  rm -rf -- "$repo/skills/default" "$repo/skills/forest-service"
  mkdir -p "$repo/skills/default" "$repo/skills/forest-service"
  home="$workdir/empty-home"
  HOME="$home" INSTALL_FOREST_SERVICE_SKILLS=0 bash "$repo/scripts/install.sh" --fs >"$workdir/out" 2>"$workdir/err"
  assert_equals '' "$(find "$home/.agents/skills" -mindepth 1 -maxdepth 1 -print)" 'Expected both empty categories valid without leaf copies.'
}

test_refreshed_imports_install_from_default_category() {
  local workdir repo home origin name source_path destination
  workdir="$(setup_test_workdir)"
  trap 'cleanup_test_workdir; trap - RETURN' RETURN
  repo="$workdir/repo"
  home="$workdir/home"
  origin="$workdir/upstream"
  create_fixture_repo "$repo"
  cp -p "$REPO_ROOT/scripts/copy-from-git.sh" "$repo/scripts/copy-from-git.sh"

  # Read import declarations as data, without running human-only orchestration.
  python3 - "$REPO_ROOT/scripts/import-skill-repos.sh" "$origin" "$repo" > "$workdir/mappings" <<'PY'
from pathlib import Path
import shlex
import sys

script, origin, repo = map(Path, sys.argv[1:])
expected = {"caveman", "show-me", "lavish"}
found = set()
for line in script.read_text().replace("\\\n", "").splitlines():
    args = shlex.split(line)
    if not args or args[0] != "$SCRIPT_DIR/copy-from-git.sh":
        continue
    for source, destination in zip(args[2::2], args[3::2]):
        name = Path(source.rstrip("/")).name
        if name not in expected:
            continue
        assert name not in found, name
        found.add(name)
        upstream = origin / source / "SKILL.md"
        upstream.parent.mkdir(parents=True, exist_ok=True)
        upstream.write_text(f"---\nname: {name}\n---\nRefreshed {name}.\n")
        stale = repo / "skills/default" / name / "SKILL.md"
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.write_text(f"Stale {name}.\n")
        print(name, source, destination, sep="\t")
assert found == expected, found
PY
  git -C "$origin" init -q -b main
  git -C "$origin" add .
  git -C "$origin" -c user.name=Fixture -c user.email=fixture@example.invalid -c commit.gpgsign=false commit -qm 'Fixture imported skills'
  while IFS=$'\t' read -r name source_path destination; do
    bash "$repo/scripts/copy-from-git.sh" "$origin" "$source_path" "$destination" > "$workdir/import-out" 2> "$workdir/import-err"
  done < "$workdir/mappings"

  HOME="$home" bash "$repo/scripts/install.sh" > "$workdir/out" 2> "$workdir/err"
  for name in caveman show-me lavish; do
    assert_file_contains "$home/.agents/skills/$name/SKILL.md" "Refreshed $name." \
      "Expected refreshed $name import to reach the flat installed skill."
    [[ ! -e "$repo/skills/$name" ]] || { echo "Expected no uncategorized $name import." >&2; exit 1; }
  done
}

main() {
  test_refreshed_imports_install_from_default_category
  test_helper_failures_are_installer_errors
  test_empty_categories_markers_and_exclusions
  test_source_preflight_is_immutable
  test_invalid_selection_is_immutable
  test_selection_environment_and_repeats
  test_explicit_forest_service_selection
  test_help_without_sources_or_dependencies
  test_provider_config_hard_links_do_not_change_other_files
  test_provider_config_linked_parent_stops_before_mutation
  test_provider_refresh_preserves_retired_and_user_entries
  test_provider_malformed_json_stops_before_mutation
  test_fresh_generated_hooks_preflight_installs_without_bytecode
  test_stale_generated_hooks_stop_before_destination_mutation
  test_generator_failure_stops_before_destination_mutation
  test_installs_codex_agents_before_other_assets
  test_codex_agents_fail_before_copying_other_assets
  test_codex_home_override_selects_one_agent_destination
  test_installs_codex_hook_and_global_configuration
  test_preserves_unrelated_codex_configuration_and_replaces_owned_handler
  test_codex_config_backup_is_bounded_and_idempotent
  test_rejects_invalid_codex_configuration_without_mutation_and_can_retry
  test_refuses_symlinked_codex_hook_destination
  test_merger_refuses_symlinked_codex_config_destinations
  test_rebases_shared_reference_links_for_flat_installed_skills
  test_rebases_read_only_markdown_and_preserves_modes_on_repeat
  test_actual_addy_shared_references_resolve_after_install
  test_prunes_without_optional_shared_references
  test_pruning_read_only_hard_link_preserves_external_inode
  test_read_only_hard_link_copy_refuses_external_mutation
  test_root_linked_skill_is_preserved_without_external_mutation
  test_excludes_and_prunes_skill_evals
  test_copies_full_gemini_tree
  test_installed_hooks_are_executable
}

main "$@"
