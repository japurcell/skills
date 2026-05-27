#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_SRC="${REPO_ROOT}/skills"
AGENTS_SRC="${REPO_ROOT}/agents"
REFERENCES_SRC="${REPO_ROOT}/references"
HOOKS_SRC="${REPO_ROOT}/hooks"
GEMINI_SRC="${REPO_ROOT}/.gemini"
COPILOT_INSTRUCTIONS_SRC="${REPO_ROOT}/.copilot/copilot-instructions.md"
COPILOT_LSP_SRC="${REPO_ROOT}/.copilot/lsp-config.json"
SKILLS_DEST="${HOME}/.agents/skills"
REFERENCES_DEST="${HOME}/.agents/references"
GEMINI_DEST="${HOME}/.gemini"
COPILOT_DEST="${HOME}/.copilot"
AGENTS_DEST="${GEMINI_DEST}/agents"
COPILOT_AGENTS_DEST="${COPILOT_DEST}/agents"
HOOKS_DEST="${HOME}/.copilot/hooks"

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
  local entry

  while IFS= read -r -d '' entry; do
    cp -Rp "$entry" "$REFERENCES_DEST/"
  done < <(find "$REFERENCES_SRC" -mindepth 1 -maxdepth 1 -print0)
}

copy_hooks() {
  local entry

  while IFS= read -r -d '' entry; do
    cp -Rp "$entry" "$HOOKS_DEST/"
  done < <(find "$HOOKS_SRC" -mindepth 1 -maxdepth 1 -print0)
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

[[ -d "$SKILLS_SRC" ]] || {
  echo "Missing skills source directory: $SKILLS_SRC" >&2
  exit 1
}

[[ -d "$AGENTS_SRC" ]] || {
  echo "Missing agents source directory: $AGENTS_SRC" >&2
  exit 1
}

[[ -f "$COPILOT_INSTRUCTIONS_SRC" ]] || {
  echo "Missing Copilot instructions file: $COPILOT_INSTRUCTIONS_SRC" >&2
  exit 1
}

[[ -d "$GEMINI_SRC" ]] || {
  echo "Missing Gemini instructions directory: $GEMINI_SRC" >&2
  exit 1
}

[[ -f "$COPILOT_LSP_SRC" ]] || {
  echo "Missing Copilot LSP config file: $COPILOT_LSP_SRC" >&2
  exit 1
}

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
