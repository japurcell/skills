#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

create_fixture_repo() {
  local repo="$1"

  mkdir -p \
    "$repo/scripts" \
    "$repo/skills/alpha" \
    "$repo/skills/alpha/evals" \
    "$repo/skills/beta-workspace" \
    "$repo/skills/archive" \
    "$repo/agents" \
    "$repo/agents/nested" \
    "$repo/references" \
    "$repo/.codex/hooks" \
    "$repo/.copilot/hooks" \
    "$repo/.gemini/policies"

  cp -p "$REPO_ROOT/scripts/install.sh" "$repo/scripts/install.sh"
  cp -p "$REPO_ROOT/scripts/install-codex-agents.py" "$repo/scripts/install-codex-agents.py"
  cp -p "$REPO_ROOT/scripts/install-codex-hooks.py" "$repo/scripts/install-codex-hooks.py"
  cp -p "$REPO_ROOT/.codex/global-hooks.json" "$repo/.codex/global-hooks.json"
  cp -p "$REPO_ROOT/.codex/AGENTS.md" "$repo/.codex/AGENTS.md"
  cp -p "$REPO_ROOT/.codex/hooks/load-required-skills.py" "$repo/.codex/hooks/load-required-skills.py"
  printf '%s\n' '---' 'name: alpha' '---' 'Standalone.' > "$repo/skills/alpha/SKILL.md"
  printf '%s\n' 'fixture eval content' > "$repo/skills/alpha/evals/evals.json"
  printf '%s\n' 'workspace skill should not copy' > "$repo/skills/beta-workspace/SKILL.md"
  printf '%s\n' 'archive entry should not copy' > "$repo/skills/archive/README.md"
  printf '%s\n' '---' 'name: helper' 'description: Fixture helper agent.' '---' 'Use alpha.' > "$repo/agents/helper.md"
  printf '%s\n' '---' 'name: nested-helper' 'description: Nested fixture helper agent.' '---' 'Use alpha deeply.' > "$repo/agents/nested/helper.md"
  cp -p "$REPO_ROOT/.gemini/GEMINI.md" "$repo/.gemini/GEMINI.md"
  printf '%s\n' 'Nested policy.' > "$repo/.gemini/policies/plan-custom-directory.toml"
  printf '%s\n' 'Hidden note.' > "$repo/.gemini/.hidden-note"
  cp -p "$REPO_ROOT/.copilot/copilot-instructions.md" "$repo/.copilot/copilot-instructions.md"
  printf '%s\n' '{}' > "$repo/.copilot/lsp-config.json"
  printf '%s\n' '#!/bin/bash' 'echo hook' > "$repo/.copilot/hooks/test-hook.sh"
  printf '%s\n' '{"global":"settings"}' > "$repo/.gemini/global-settings.json"
  printf '%s\n' '{"local":"settings"}' > "$repo/.gemini/settings.json"

  mkdir -p "$repo/.gemini/hooks/scripts" "$repo/.copilot/hooks/scripts"
  printf '%s\n' 'print("hook")' > "$repo/.gemini/hooks/scripts/test-hook.py"
  printf '%s\n' 'print("hook")' > "$repo/.copilot/hooks/scripts/test-hook.py"
  printf '%s\n' '#!/bin/bash' 'echo hook' > "$repo/.gemini/hooks/scripts/test-hook.sh"
  printf '%s\n' '#!/bin/bash' 'echo hook' > "$repo/.copilot/hooks/scripts/test-hook.sh"
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
}

test_stale_generated_hooks_stop_before_destination_mutation() {
  local workdir
  local repo
  local home
  local output_path
  local before
  local after
  local status

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"
  create_fixture_repo "$repo"
  output_path="$(generated_rtk_output_path "$repo")"
  printf '%s\n' '# stale fixture output' >> "$repo/$output_path"
  mkdir -p "$home/preserved"
  printf '%s\n' 'do not change' > "$home/preserved/sentinel.txt"
  before="$(tree_fingerprint "$home")"

  status=0
  HOME="$home" bash "$repo/scripts/install.sh" >"$workdir/stdout" 2>"$workdir/stderr" || status=$?
  assert_equals "1" "$status" "Expected stale generated hooks to exit 1."
  assert_file_contains "$workdir/stdout" "$output_path" "Expected stale output path on stdout."
  assert_file_contains "$workdir/stderr" "python3 scripts/generate-hooks.py --write" "Expected stale-output recovery command on stderr."
  after="$(tree_fingerprint "$home")"
  assert_equals "$before" "$after" "Expected stale preflight to leave the destination tree byte-for-byte unchanged with no new directories."
}

test_generator_failure_stops_before_destination_mutation() {
  local workdir
  local repo
  local home
  local before
  local after
  local status

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"
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

  status=0
  HOME="$home" bash "$repo/scripts/install.sh" >"$workdir/stdout" 2>"$workdir/stderr" || status=$?
  assert_equals "2" "$status" "Expected a generator failure to exit 2."
  assert_file_contains "$workdir/stderr" "Unknown provider 'unknown'" "Expected the generator diagnostic on stderr."
  if grep -Fq "python3 scripts/generate-hooks.py --write" "$workdir/stderr"; then
    echo "Expected generator failures to omit stale-output recovery advice." >&2
    exit 1
  fi
  after="$(tree_fingerprint "$home")"
  assert_equals "$before" "$after" "Expected generator failure preflight to leave the destination tree byte-for-byte unchanged with no new directories."
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
  for installed in scan-secrets.py tool-guard.py markdown-health.py helpers/common.py helpers/audit.py; do
    if [[ ! -x "$home/.codex/hooks/$installed" ]]; then
      echo "Expected maintained Codex hook to be installed and executable: $installed" >&2
      exit 1
    fi
    cmp "$repo/.codex/hooks/$installed" "$home/.codex/hooks/$installed"
  done
  if [[ -e "$home/.codex/hooks.json.bak" ]]; then
    echo "Expected a fresh Codex install not to create a backup." >&2
    exit 1
  fi

  python3 - "$home/.codex/hooks.json" <<'PY'
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
pre_tool = config["hooks"]["PreToolUse"]
assert len(pre_tool) == 2
assert pre_tool[0]["hooks"][0]["command"] == "python3 ~/.codex/hooks/rtk-explicit-codex.py"
pre_commands = [hook["command"] for hook in pre_tool[1]["hooks"]]
assert "python3 ~/.codex/hooks/scan-secrets.py" in pre_commands
assert "python3 ~/.codex/hooks/tool-guard.py" in pre_commands
stop_commands = [hook["command"] for hook in config["hooks"]["Stop"][0]["hooks"]]
assert "python3 ~/.codex/hooks/scan-secrets.py" in stop_commands
for event in ("PreToolUse", "PostToolUse", "Stop"):
    commands = [hook["command"] for group in config["hooks"][event] for hook in group["hooks"]]
    assert "python3 ~/.codex/hooks/markdown-health.py" in commands
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
        {"type": "command", "command": "python3 ~/.codex/hooks/load-required-skills.py"},
        {"type": "command", "command": "python3 ~/.codex/hooks/load-required-skills.py", "commandWindows": "py -3 \"%USERPROFILE%\\.codex\\hooks\\load-required-skills.py\""}
      ]},
      {"matcher": "resume", "hooks": []},
      {"matcher": "clear", "hooks": [
        {"type": "command", "commandWindows": "py -3 \"%USERPROFILE%\\.codex\\hooks\\load-required-skills.py\""}
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
    {"type": "command", "command": "python3 ~/.codex/hooks/load-required-skills.py"},
]
assert groups[1] == {"matcher": "resume", "hooks": []}
assert groups[2]["hooks"] == [
    {"type": "command", "commandWindows": 'py -3 "%USERPROFILE%\\.codex\\hooks\\load-required-skills.py"'},
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
  local workdir
  local repo
  local home

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"

  create_fixture_repo "$repo"

  chmod 644 "$repo/.gemini/hooks/scripts/test-hook.py"
  chmod 644 "$repo/.copilot/hooks/scripts/test-hook.py"
  chmod 644 "$repo/.gemini/hooks/scripts/test-hook.sh"
  chmod 644 "$repo/.copilot/hooks/scripts/test-hook.sh"

  HOME="$home" bash "$repo/scripts/install.sh" >/dev/null

  if [[ ! -x "$home/.gemini/hooks/scripts/test-hook.py" ]]; then
    echo "Expected ~/.gemini/hooks/scripts/test-hook.py to be executable." >&2
    exit 1
  fi

  if [[ ! -x "$home/.copilot/hooks/scripts/test-hook.py" ]]; then
    echo "Expected ~/.copilot/hooks/scripts/test-hook.py to be executable." >&2
    exit 1
  fi

  if [[ ! -x "$home/.gemini/hooks/scripts/test-hook.sh" ]]; then
    echo "Expected ~/.gemini/hooks/scripts/test-hook.sh to be executable." >&2
    exit 1
  fi

  if [[ ! -x "$home/.copilot/hooks/scripts/test-hook.sh" ]]; then
    echo "Expected ~/.copilot/hooks/scripts/test-hook.sh to be executable." >&2
    exit 1
  fi
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
  if [[ "$copied_gemini" != *'use `write_file` to create the complete script as a saved file, then execute that saved file.'* ]]; then
    echo "Expected installed Gemini guidance to require file-first PowerShell authoring." >&2
    exit 1
  fi
  assert_equals $'---\nname: helper\ndescription: Fixture helper agent.\n---\nUse alpha.' "$copied_agent" "Expected agents to be copied into ~/.gemini/agents."
  assert_equals $'---\nname: nested-helper\ndescription: Nested fixture helper agent.\n---\nUse alpha deeply.' "$copied_nested_agent" "Expected nested agents to be copied recursively into ~/.gemini/agents."
  assert_equals $'---\nname: helper\ndescription: Fixture helper agent.\n---\nUse alpha.' "$copied_copilot_agent" "Expected agents to be copied into ~/.copilot/agents."
  assert_equals $'---\nname: nested-helper\ndescription: Nested fixture helper agent.\n---\nUse alpha deeply.' "$copied_copilot_nested_agent" "Expected nested agents to be copied recursively into ~/.copilot/agents."
  assert_equals "Nested policy." "$copied_policy" "Expected nested Gemini files to be copied recursively."
  assert_equals "Hidden note." "$copied_hidden" "Expected hidden Gemini files to be copied recursively."
  assert_equals $'#!/bin/bash\necho hook' "$copied_hook" "Expected hooks to be copied into ~/.copilot/hooks."
  assert_equals '{"global":"settings"}' "$copied_global_settings" "Expected global Gemini settings to overwrite repo-local settings during install."
  assert_equals "$(<"$repo/.copilot/copilot-instructions.md")" "$(<"$home/.copilot/copilot-instructions.md")" "Expected Copilot instructions to be copied into ~/.copilot."
  if [[ "$(<"$home/.copilot/copilot-instructions.md")" != *"use Copilot's native file-create or file-edit tool to create the complete script as a saved file, then execute that saved file."* ]]; then
    echo "Expected installed Copilot guidance to require file-first PowerShell authoring." >&2
    exit 1
  fi
  if [[ "$(<"$home/.codex/AGENTS.md")" != *"use Codex's native file-write or file-edit tool, such as \`apply_patch\`, to create the complete script as a saved file, then execute that saved file."* ]]; then
    echo "Expected installed Codex guidance to require file-first PowerShell authoring." >&2
    exit 1
  fi

  if [[ -e "$home/.gemini/.gemini" ]]; then
    echo "Expected the installer to copy Gemini contents into ~/.gemini, not nest another .gemini directory." >&2
    exit 1
  fi

}

main() {
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
  test_excludes_and_prunes_skill_evals
  test_copies_full_gemini_tree
  test_installed_hooks_are_executable
}

main "$@"
