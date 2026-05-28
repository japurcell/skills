#!/usr/bin/env bash

set -euo pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly SKILLS_SRC="${REPO_ROOT}/skills"
readonly AGENTS_SRC="${REPO_ROOT}/agents"
readonly REFERENCES_SRC="${REPO_ROOT}/references"
readonly HOOKS_SRC="${REPO_ROOT}/.copilot/hooks"
readonly GEMINI_SRC="${REPO_ROOT}/.gemini"
readonly COPILOT_INSTRUCTIONS_SRC="${REPO_ROOT}/.copilot/copilot-instructions.md"
readonly COPILOT_LSP_SRC="${REPO_ROOT}/.copilot/lsp-config.json"

readonly SKILLS_DEST="${HOME}/.agents/skills"
readonly REFERENCES_DEST="${HOME}/.agents/references"
readonly GEMINI_DEST="${HOME}/.gemini"
readonly COPILOT_DEST="${HOME}/.copilot"
readonly AGENTS_DEST="${GEMINI_DEST}/agents"
readonly COPILOT_AGENTS_DEST="${COPILOT_DEST}/agents"
readonly HOOKS_DEST="${HOME}/.copilot/hooks"

copy_skills() {
  local entry
  local name

  while IFS= read -r -d '' entry; do
    name="$(basename "$entry")"

    if [[ "$name" == *-workspace || "$name" == "archive" ]]; then
      continue
    fi

    cp -Rp "$entry" "$SKILLS_DEST/"
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
}

copy_gemini() {
  cp -Rp "$GEMINI_SRC/." "$GEMINI_DEST/"
}

copy_copilot_instructions() {
  cp -p "$COPILOT_INSTRUCTIONS_SRC" "$COPILOT_DEST/"
}

copy_copilot_lsp() {
  cp -p "$COPILOT_LSP_SRC" "$COPILOT_DEST/"
}

for src in "$SKILLS_SRC" "$AGENTS_SRC" "$GEMINI_SRC"; do
  [[ -d "$src" ]] || { echo "Missing source directory: $src" >&2; exit 1; }
done

for src in "$COPILOT_INSTRUCTIONS_SRC" "$COPILOT_LSP_SRC"; do
  [[ -f "$src" ]] || { echo "Missing source file: $src" >&2; exit 1; }
done

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
copy_copilot_instructions
copy_copilot_lsp

echo "Installed skills to $SKILLS_DEST"
echo "Installed agents to $AGENTS_DEST and $COPILOT_AGENTS_DEST"
if [[ -d "$REFERENCES_SRC" ]]; then
  echo "Installed references to $REFERENCES_DEST"
fi
if [[ -d "$HOOKS_SRC" ]]; then
  echo "Installed hooks to $HOOKS_DEST"
fi
echo "Installed Gemini instructions to $GEMINI_DEST"
echo "Installed Copilot instructions to $COPILOT_DEST/copilot-instructions.md"
echo "Installed Copilot LSP config to $COPILOT_DEST/lsp-config.json"
