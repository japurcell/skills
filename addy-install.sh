#!/usr/bin/env bash

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly DEFAULT_SOURCE_ROOT="${SCRIPT_DIR}/../addy-agent-skills"
readonly DEFAULT_DEST_ROOT="${SCRIPT_DIR}/skills"
readonly PREFIX="${ADDY_PREFIX:-addy-}"
readonly AGENTS_SRC="${ADDY_AGENTS_SRC:-${DEFAULT_SOURCE_ROOT}/agents}"
readonly SKILLS_SRC="${ADDY_SKILLS_SRC:-${DEFAULT_SOURCE_ROOT}/skills}"
readonly AGENTS_DEST="${ADDY_AGENTS_DEST:-${DEFAULT_DEST_ROOT}/agents}"
readonly SKILLS_DEST="${ADDY_SKILLS_DEST:-${DEFAULT_DEST_ROOT}/skills}"

declare -a COPIED_AGENT_FILES=()
declare -a COPIED_SKILL_DIRS=()

rewrite_name_field() {
  local file="$1"
  local original_name="$2"
  local prefixed_name="$3"

  python3 - "$file" "$original_name" "$prefixed_name" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
original_name = sys.argv[2]
prefixed_name = sys.argv[3]

if not path.is_file():
    raise SystemExit(f"Missing file to rewrite: {path}")

content = path.read_text(encoding="utf-8")
updated_content, replacements = re.subn(
    rf"(?m)^name:\s*{re.escape(original_name)}\s*$",
    f"name: {prefixed_name}",
    content,
    count=1,
)

if replacements != 1:
    raise SystemExit(
        f"Missing expected name field in {path}: name: {original_name}"
    )

path.write_text(updated_content, encoding="utf-8")
PY
}

build_name_map() {
  local map_file="$1"
  local source_file
  local source_dir
  local base_name

  : > "$map_file"

  while IFS= read -r -d '' source_file; do
    base_name="$(basename "$source_file" .md)"
    printf '%s\t%s%s\n' "$base_name" "$PREFIX" "$base_name" >> "$map_file"
  done < <(find "$AGENTS_SRC" -mindepth 1 -maxdepth 1 -type f -name '*.md' -print0 | sort -z)

  while IFS= read -r -d '' source_dir; do
    base_name="$(basename "$source_dir")"
    printf '%s\t%s%s\n' "$base_name" "$PREFIX" "$base_name" >> "$map_file"
  done < <(find "$SKILLS_SRC" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)

  sort -u "$map_file" -o "$map_file"
}

rewrite_references() {
  local map_file="$1"

  ((${#COPIED_AGENT_FILES[@]} + ${#COPIED_SKILL_DIRS[@]} > 0)) || return 0

  python3 - "$map_file" "${COPIED_AGENT_FILES[@]}" "${COPIED_SKILL_DIRS[@]}" <<'PY'
from pathlib import Path
import re
import sys

map_path = Path(sys.argv[1])
targets = [Path(arg) for arg in sys.argv[2:]]

mappings = []
for line in map_path.read_text(encoding="utf-8").splitlines():
    if not line:
        continue
    original_name, prefixed_name = line.split("\t", 1)
    mappings.append((original_name, prefixed_name))

mappings.sort(key=lambda item: len(item[0]), reverse=True)


def iter_files(target: Path):
    if target.is_dir():
        yield from sorted(path for path in target.rglob("*") if path.is_file())
        return

    if target.is_file():
        yield target


for target in targets:
    for path in iter_files(target):
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        updated_content = content
        for original_name, prefixed_name in mappings:
            updated_content = re.sub(
                rf"(?<![A-Za-z0-9_-]){re.escape(original_name)}(?![A-Za-z0-9_-])",
                prefixed_name,
                updated_content,
            )

        if updated_content != content:
            path.write_text(updated_content, encoding="utf-8")
PY
}

copy_agents() {
  local source_file
  local base_name
  local target_file

  while IFS= read -r -d '' source_file; do
    base_name="$(basename "$source_file" .md)"
    target_file="${AGENTS_DEST}/${PREFIX}${base_name}.md"

    cp -p "$source_file" "$target_file"
    rewrite_name_field "$target_file" "$base_name" "${PREFIX}${base_name}"
    COPIED_AGENT_FILES+=("$target_file")
  done < <(find "$AGENTS_SRC" -mindepth 1 -maxdepth 1 -type f -name '*.md' -print0 | sort -z)
}

copy_skills() {
  local source_dir
  local base_name
  local target_dir
  local skill_file

  while IFS= read -r -d '' source_dir; do
    base_name="$(basename "$source_dir")"
    target_dir="${SKILLS_DEST}/${PREFIX}${base_name}"
    skill_file="${target_dir}/SKILL.md"

    rm -rf "$target_dir"
    cp -Rp "$source_dir" "$target_dir"
    rewrite_name_field "$skill_file" "$base_name" "${PREFIX}${base_name}"
    COPIED_SKILL_DIRS+=("$target_dir")
  done < <(find "$SKILLS_SRC" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)
}

[[ -n "$PREFIX" ]] || {
  echo "Prefix must not be empty" >&2
  exit 1
}

[[ -d "$AGENTS_SRC" ]] || {
  echo "Missing agents source directory: $AGENTS_SRC" >&2
  exit 1
}

[[ -d "$SKILLS_SRC" ]] || {
  echo "Missing skills source directory: $SKILLS_SRC" >&2
  exit 1
}

readonly NAME_MAP_FILE="$(mktemp)"
trap 'rm -f "$NAME_MAP_FILE"' EXIT

mkdir -p "$AGENTS_DEST" "$SKILLS_DEST"

build_name_map "$NAME_MAP_FILE"
copy_agents
copy_skills
rewrite_references "$NAME_MAP_FILE"

echo "Installed addy agents to $AGENTS_DEST"
echo "Installed addy skills to $SKILLS_DEST"
