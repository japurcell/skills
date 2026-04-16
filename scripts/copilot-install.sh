#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_SRC="${REPO_ROOT}/skills"
AGENTS_SRC="${REPO_ROOT}/agents"
REFERENCES_SRC="${REPO_ROOT}/references"
HOOKS_SRC="${REPO_ROOT}/hooks"
COPILOT_INSTRUCTIONS_SRC="${REPO_ROOT}/.copilot/copilot-instructions.md"
SKILLS_DEST="${HOME}/.agents/skills"
REFERENCES_DEST="${HOME}/.agents/references"
COPILOT_DEST="${HOME}/.copilot"
AGENTS_DEST="${HOME}/.copilot/agents"
HOOKS_DEST="${HOME}/.copilot/hooks"

copy_skills() {
  local entry
  local name

  while IFS= read -r -d '' entry; do
    name="$(basename "$entry")"

    if [[ "$name" == *-workspace ]]; then
      continue
    fi

    cp -Rp "$entry" "$SKILLS_DEST/"
  done < <(find "$SKILLS_SRC" -mindepth 1 -maxdepth 1 -print0)
}

copy_agents() {
  local file

  while IFS= read -r -d '' file; do
    cp -p "$file" "$AGENTS_DEST/"
  done < <(find "$AGENTS_SRC" -mindepth 1 -maxdepth 1 -type f -print0)
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

copy_copilot_instructions() {
  cp -p "$COPILOT_INSTRUCTIONS_SRC" "$COPILOT_DEST/"
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

mkdir -p "$SKILLS_DEST" "$COPILOT_DEST" "$AGENTS_DEST"

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
copy_copilot_instructions

echo "Installed skills to $SKILLS_DEST"
echo "Installed agents to $AGENTS_DEST"
if [[ -d "$REFERENCES_SRC" ]]; then
  echo "Installed references to $REFERENCES_DEST"
fi
if [[ -d "$HOOKS_SRC" ]]; then
  echo "Installed hooks to $HOOKS_DEST"
fi
echo "Installed Copilot instructions to $COPILOT_DEST/copilot-instructions.md"
