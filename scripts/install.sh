#!/usr/bin/env bash

set -euo pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly SKILLS_SRC="${REPO_ROOT}/skills"
readonly AGENTS_SRC="${REPO_ROOT}/agents"
readonly REFERENCES_SRC="${REPO_ROOT}/references"
readonly HOOKS_SRC="${REPO_ROOT}/.copilot/hooks"
readonly GEMINI_SRC="${REPO_ROOT}/.gemini"
readonly GEMINI_GLOBAL_SETTINGS_SRC="${REPO_ROOT}/.gemini/global-settings.json"
readonly COPILOT_INSTRUCTIONS_SRC="${REPO_ROOT}/.copilot/copilot-instructions.md"
readonly COPILOT_LSP_SRC="${REPO_ROOT}/.copilot/lsp-config.json"
readonly CODEX_HOOK_SRC_DIR="${REPO_ROOT}/.codex/hooks"
readonly CODEX_HOOK_FILES=(load-required-skills.py scan-secrets.py tool-guard.py markdown-health.py rtk-explicit-codex.py rtk-agent-launcher.py helpers/common.py helpers/audit.py)
readonly CODEX_INSTRUCTIONS_SRC="${REPO_ROOT}/.codex/AGENTS.md"
readonly CODEX_HOOK_TEMPLATE_SRC="${REPO_ROOT}/.codex/global-hooks.json"
readonly CODEX_HOOK_MERGER="${REPO_ROOT}/scripts/install-codex-hooks.py"
readonly CODEX_AGENT_INSTALLER="${REPO_ROOT}/scripts/install-codex-agents.py"
readonly GENERATE_HOOKS="${REPO_ROOT}/scripts/generate-hooks.py"
readonly CANONICAL_HOOKS_SRC="${REPO_ROOT}/hooks"

readonly SKILLS_DEST="${HOME}/.agents/skills"
readonly REFERENCES_DEST="${HOME}/.agents/references"
readonly GEMINI_DEST="${HOME}/.gemini"
readonly COPILOT_DEST="${HOME}/.copilot"
readonly AGENTS_DEST="${GEMINI_DEST}/agents"
readonly COPILOT_AGENTS_DEST="${COPILOT_DEST}/agents"
readonly HOOKS_DEST="${HOME}/.copilot/hooks"
readonly CODEX_HOOKS_DEST="${HOME}/.codex/hooks"
readonly CODEX_HOOK_CONFIG_DEST="${HOME}/.codex/hooks.json"
readonly CODEX_INSTRUCTIONS_DEST="${HOME}/.codex/AGENTS.md"
readonly CODEX_AGENTS_DEST="${CODEX_HOME:-${HOME}/.codex}/agents"

copy_skills() {
  local entry
  local name

  while IFS= read -r -d '' entry; do
    name="$(basename "$entry")"

    if [[ "$name" == *-workspace || "$name" == "archive" ]]; then
      continue
    fi
    cp -Rp "$entry" "$SKILLS_DEST/"
    rm -rf "${SKILLS_DEST}/${name}/evals"
    rm -rf "${SKILLS_DEST}/${name}/README.md"
    rm -rf "${SKILLS_DEST}/${name}/LICENSE.txt"
    rm -rf "${SKILLS_DEST}/${name}/LICENSE.md"
  done < <(find "$SKILLS_SRC" -mindepth 1 -maxdepth 1 -print0)
}

copy_agents() {
  cp -Rp "$AGENTS_SRC/." "$AGENTS_DEST/"
  cp -Rp "$AGENTS_SRC/." "$COPILOT_AGENTS_DEST/"
}

copy_references() {
  cp -Rp "$REFERENCES_SRC/." "$REFERENCES_DEST/"
}

copy_hooks() {
  cp -Rp "$HOOKS_SRC/." "$HOOKS_DEST/"
  find "$HOOKS_DEST" -type f \( -name "*.py" -o -name "*.sh" \) -exec chmod 755 {} +
}

copy_gemini() {
  local entry
  local name

  while IFS= read -r -d '' entry; do
    name="$(basename "$entry")"
    if [[ "$name" == "hooks" ]]; then
      continue
    fi
    cp -Rp "$entry" "$GEMINI_DEST/"
  done < <(find "$GEMINI_SRC" -mindepth 1 -maxdepth 1 -print0)

  mkdir -p "$GEMINI_DEST/hooks"
  while IFS= read -r -d '' entry; do
    name="$(basename "$entry")"
    if [[ "$name" == "logs" ]]; then
      continue
    fi
    cp -Rp "$entry" "$GEMINI_DEST/hooks/"
  done < <(find "$GEMINI_SRC/hooks" -mindepth 1 -maxdepth 1 -print0)

  rm -f "$GEMINI_DEST/global-settings.json"
  rm -f "$GEMINI_DEST/settings.json"
  if [[ -d "$GEMINI_DEST/hooks" ]]; then
    find "$GEMINI_DEST/hooks" -type f \( -name "*.py" -o -name "*.sh" \) -exec chmod 755 {} +
  fi
}

copy_gemini_global_settings() {
  cp -p "$GEMINI_GLOBAL_SETTINGS_SRC" "$GEMINI_DEST/settings.json"
}

copy_copilot_instructions() {
  cp -p "$COPILOT_INSTRUCTIONS_SRC" "$COPILOT_DEST/"
}

copy_copilot_lsp() {
  cp -p "$COPILOT_LSP_SRC" "$COPILOT_DEST/"
}

install_codex_hook() {
  local hook
  python3 "$CODEX_HOOK_MERGER" \
    --template "$CODEX_HOOK_TEMPLATE_SRC" \
    --destination "$CODEX_HOOK_CONFIG_DEST" \
    --check
  for hook in "$CODEX_HOOKS_DEST" "$CODEX_HOOKS_DEST/helpers"; do
    if [[ -L "$hook" ]]; then
      echo "Refusing linked Codex hook directory: $hook" >&2
      return 1
    fi
  done
  for hook in "${CODEX_HOOK_FILES[@]}"; do
    if [[ -L "$CODEX_HOOKS_DEST/$hook" || ( -e "$CODEX_HOOKS_DEST/$hook" && ! -f "$CODEX_HOOKS_DEST/$hook" ) ]]; then
      echo "Refusing linked or non-file Codex hook destination: $CODEX_HOOKS_DEST/$hook" >&2
      return 1
    fi
  done
  mkdir -p "$CODEX_HOOKS_DEST/helpers"
  for hook in "${CODEX_HOOK_FILES[@]}"; do
    cp -p "$CODEX_HOOK_SRC_DIR/$hook" "$CODEX_HOOKS_DEST/$hook"
    chmod 755 "$CODEX_HOOKS_DEST/$hook"
  done
  python3 "$CODEX_HOOK_MERGER" \
    --template "$CODEX_HOOK_TEMPLATE_SRC" \
    --destination "$CODEX_HOOK_CONFIG_DEST"
}

install_codex_instructions() {
  mkdir -p "$(dirname "$CODEX_INSTRUCTIONS_DEST")"
  cp -p "$CODEX_INSTRUCTIONS_SRC" "$CODEX_INSTRUCTIONS_DEST"
}

for src in "$SKILLS_SRC" "$AGENTS_SRC" "$GEMINI_SRC" "$CANONICAL_HOOKS_SRC"; do
  [[ -d "$src" ]] || { echo "Missing source directory: $src" >&2; exit 1; }
done

for src in "$COPILOT_INSTRUCTIONS_SRC" "$COPILOT_LSP_SRC" "$GEMINI_GLOBAL_SETTINGS_SRC"; do
  [[ -f "$src" ]] || { echo "Missing source file: $src" >&2; exit 1; }
done

for src in "$CODEX_INSTRUCTIONS_SRC" "$CODEX_HOOK_TEMPLATE_SRC" "$CODEX_HOOK_MERGER" "$CODEX_AGENT_INSTALLER" "$GENERATE_HOOKS"; do
  [[ -f "$src" ]] || { echo "Missing source file: $src" >&2; exit 1; }
done
for hook in "${CODEX_HOOK_FILES[@]}"; do
  [[ -f "$CODEX_HOOK_SRC_DIR/$hook" ]] || { echo "Missing source file: $CODEX_HOOK_SRC_DIR/$hook" >&2; exit 1; }
done

if PYTHONDONTWRITEBYTECODE=1 python3 "$GENERATE_HOOKS" --check; then
  :
else
  status=$?
  if [[ "$status" -eq 1 ]]; then
    echo "Generated hooks are stale. Run: python3 scripts/generate-hooks.py --write" >&2
    exit 1
  fi
  echo "Generated hook freshness preflight failed." >&2
  if [[ "$status" -eq 2 ]]; then
    exit 2
  fi
  exit "$status"
fi

python3 "$CODEX_AGENT_INSTALLER" --source-dir "$AGENTS_SRC" --destination-dir "$CODEX_AGENTS_DEST"

mkdir -p "$SKILLS_DEST" "$COPILOT_DEST" "$GEMINI_DEST" "$AGENTS_DEST" "$COPILOT_AGENTS_DEST"

copy_skills
copy_agents
if [[ -d "$REFERENCES_SRC" ]]; then
  mkdir -p "$REFERENCES_DEST"
  copy_references
fi
if [[ -d "$HOOKS_SRC" ]]; then
  mkdir -p "$HOOKS_DEST"
  copy_hooks
fi
copy_gemini
copy_gemini_global_settings
copy_copilot_instructions
copy_copilot_lsp
install_codex_instructions
install_codex_hook

echo "Installed skills to $SKILLS_DEST"
echo "Installed agents to $AGENTS_DEST and $COPILOT_AGENTS_DEST"
echo "Installed Codex agents to $CODEX_AGENTS_DEST"
if [[ -d "$REFERENCES_SRC" ]]; then
  echo "Installed references to $REFERENCES_DEST"
fi
if [[ -d "$HOOKS_SRC" ]]; then
  echo "Installed hooks to $HOOKS_DEST"
fi
echo "Installed Gemini instructions to $GEMINI_DEST"
echo "Installed Gemini settings to $GEMINI_DEST/settings.json"
echo "Installed Copilot instructions to $COPILOT_DEST/copilot-instructions.md"
echo "Installed Copilot LSP config to $COPILOT_DEST/lsp-config.json"
echo "Installed Codex instructions to $CODEX_INSTRUCTIONS_DEST"
echo "Installed Codex hook to $CODEX_HOOKS_DEST/load-required-skills.py"
echo "Installed Codex hook configuration to $CODEX_HOOK_CONFIG_DEST"
