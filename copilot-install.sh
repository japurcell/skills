#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="${SCRIPT_DIR}/skills"
AGENTS_SRC="${SCRIPT_DIR}/agents"
SKILLS_DEST="${HOME}/.agents/skills"
AGENTS_DEST="${HOME}/.copilot/agents"

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

[[ -d "$SKILLS_SRC" ]] || {
  echo "Missing skills source directory: $SKILLS_SRC" >&2
  exit 1
}

[[ -d "$AGENTS_SRC" ]] || {
  echo "Missing agents source directory: $AGENTS_SRC" >&2
  exit 1
}

mkdir -p "$SKILLS_DEST" "$AGENTS_DEST"

# copy_skills
copy_agents

echo "Installed skills to $SKILLS_DEST"
echo "Installed agents to $AGENTS_DEST"
