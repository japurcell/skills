#!/usr/bin/env bash

set -euo pipefail

readonly REPO_ROOT="${ADDY_REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
readonly DEFAULT_SOURCE_ROOT="${REPO_ROOT}/../addy-agent-skills"
readonly SOURCE_ROOT="${ADDY_SOURCE_ROOT:-${DEFAULT_SOURCE_ROOT}}"
readonly SOURCE_REMOTE_URL="${ADDY_REMOTE_URL:-https://github.com/addyosmani/agent-skills}"
readonly DEFAULT_DEST_ROOT="${REPO_ROOT}"
readonly PREFIX="${ADDY_PREFIX:-addy-}"
readonly AGENTS_SRC="${ADDY_AGENTS_SRC:-${SOURCE_ROOT}/agents}"
readonly SKILLS_SRC="${ADDY_SKILLS_SRC:-${SOURCE_ROOT}/skills}"
readonly REFERENCES_SRC="${ADDY_REFERENCES_SRC:-${SOURCE_ROOT}/references}"
readonly AGENTS_DEST="${ADDY_AGENTS_DEST:-${DEFAULT_DEST_ROOT}/agents}"
readonly SKILLS_DEST="${ADDY_SKILLS_DEST:-${DEFAULT_DEST_ROOT}/skills}"
readonly REFERENCES_DEST="${ADDY_REFERENCES_DEST:-${DEFAULT_DEST_ROOT}/references}"

declare -a COPIED_AGENT_FILES=()
declare -a COPIED_SKILL_DIRS=()
declare -a COPIED_REFERENCE_DIRS=()
declare -a SELECTED_SKILLS=()

usage() {
  cat <<'EOF'
Usage: scripts/addy-install.sh [--skills name1,name2] [--skills name3]

Copies addy agents and skills into this repository with the configured prefix.
If --skills is omitted, all skills are copied.
Referenced skills are copied automatically.
EOF
}

add_selected_skills() {
  local raw_names="$1"
  local skill_name
  local parsed_names=()

  [[ -n "$raw_names" ]] || {
    echo "Skill names must not be empty" >&2
    exit 1
  }

  IFS=',' read -r -a parsed_names <<< "$raw_names"

  for skill_name in "${parsed_names[@]}"; do
    [[ -n "$skill_name" ]] || {
      echo "Skill names must not be empty" >&2
      exit 1
    }

    if ! has_selected_skill "$skill_name"; then
      SELECTED_SKILLS+=("$skill_name")
    fi
  done
}

has_selected_skill() {
  local skill_name="$1"
  local selected_skill

  ((${#SELECTED_SKILLS[@]} > 0)) || return 1

  for selected_skill in "${SELECTED_SKILLS[@]}"; do
    if [[ "$selected_skill" == "$skill_name" ]]; then
      return 0
    fi
  done

  return 1
}

parse_args() {
  local value

  while (($# > 0)); do
    case "$1" in
      --skills)
        shift
        [[ $# -gt 0 && "$1" != --* ]] || {
          echo "Missing value for --skills" >&2
          exit 1
        }
        value="$1"
        ;;
      --skills=*)
        value="${1#--skills=}"
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        echo "Unknown argument: $1" >&2
        usage >&2
        exit 1
        ;;
    esac

    add_selected_skills "$value"
    shift
  done
}

should_sync_source_root() {
  if [[ -n "${ADDY_SOURCE_ROOT:-}" ]]; then
    return 0
  fi

  if [[ -n "${ADDY_AGENTS_SRC:-}" || -n "${ADDY_SKILLS_SRC:-}" || -n "${ADDY_REFERENCES_SRC:-}" ]]; then
    return 1
  fi

  return 0
}

sync_source_root() {
  local current_branch

  should_sync_source_root || return 0

  mkdir -p "$(dirname "$SOURCE_ROOT")"

  if [[ ! -e "$SOURCE_ROOT" ]]; then
    git clone --quiet "$SOURCE_REMOTE_URL" "$SOURCE_ROOT"
    return 0
  fi

  [[ -d "$SOURCE_ROOT" ]] || {
    echo "Existing addy source path is not a directory: $SOURCE_ROOT" >&2
    exit 1
  }

  [[ -d "$SOURCE_ROOT/.git" ]] || {
    echo "Existing addy source path is not a git repository: $SOURCE_ROOT" >&2
    exit 1
  }

  if git -C "$SOURCE_ROOT" remote get-url origin >/dev/null 2>&1; then
    git -C "$SOURCE_ROOT" remote set-url origin "$SOURCE_REMOTE_URL"
  else
    git -C "$SOURCE_ROOT" remote add origin "$SOURCE_REMOTE_URL"
  fi

  current_branch="$(git -C "$SOURCE_ROOT" symbolic-ref --quiet --short HEAD)" || {
    echo "Unable to determine current branch for $SOURCE_ROOT" >&2
    exit 1
  }

  git -C "$SOURCE_ROOT" pull --ff-only --quiet origin "$current_branch"
}

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
  done < <(iter_skill_source_dirs)

  sort -u "$map_file" -o "$map_file"
}

rewrite_references() {
  local map_file="$1"

  ((${#COPIED_AGENT_FILES[@]} + ${#COPIED_SKILL_DIRS[@]} + ${#COPIED_REFERENCE_DIRS[@]} > 0)) || return 0

  python3 - "$map_file" "$REFERENCES_DEST" \
    ${COPIED_AGENT_FILES[@]+"${COPIED_AGENT_FILES[@]}"} \
    ${COPIED_SKILL_DIRS[@]+"${COPIED_SKILL_DIRS[@]}"} \
    ${COPIED_REFERENCE_DIRS[@]+"${COPIED_REFERENCE_DIRS[@]}"} <<'PY'
import os
from pathlib import Path
import re
import sys

map_path = Path(sys.argv[1])
references_root = Path(sys.argv[2]).resolve()
targets = [Path(arg) for arg in sys.argv[3:]]

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


def rewrite_reference_paths(content: str, path: Path) -> str:
    try:
        path.resolve().relative_to(references_root)
    except ValueError:
        relative_references_dir = os.path.relpath(references_root, start=path.resolve().parent)
        return re.sub(
            r"(?<![A-Za-z0-9._/-])references/",
            f"{relative_references_dir}/",
            content,
        )

    return content


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

        updated_content = rewrite_reference_paths(updated_content, path)

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

iter_skill_source_dirs() {
  local source_dir
  local base_name

  while IFS= read -r -d '' source_dir; do
    base_name="$(basename "$source_dir")"

    if ((${#SELECTED_SKILLS[@]} > 0)) && ! has_selected_skill "$base_name"; then
      continue
    fi

    printf '%s\0' "$source_dir"
  done < <(find "$SKILLS_SRC" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)
}

validate_selected_skills() {
  local skill_name
  local missing=0

  ((${#SELECTED_SKILLS[@]} == 0)) && return 0

  for skill_name in "${SELECTED_SKILLS[@]}"; do
    if [[ ! -d "${SKILLS_SRC}/${skill_name}" ]]; then
      echo "Missing skill source directory: ${SKILLS_SRC}/${skill_name}" >&2
      missing=1
    fi
  done

  ((missing == 0)) || exit 1
}

resolve_selected_skills() {
  local resolved_skill

  ((${#SELECTED_SKILLS[@]} == 0)) && return 0

  while IFS= read -r resolved_skill; do
    [[ -n "$resolved_skill" ]] || continue
    add_selected_skills "$resolved_skill"
  done < <(
    python3 - "$SKILLS_SRC" "${SELECTED_SKILLS[@]}" <<'PY'
from collections import deque
from pathlib import Path
import re
import sys

skills_src = Path(sys.argv[1])
selected = sys.argv[2:]
skill_dirs = {
    path.name: path
    for path in sorted(skills_src.iterdir())
    if path.is_dir()
}
skill_names = sorted(skill_dirs)
patterns = {
    name: re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(name)}(?![A-Za-z0-9_-])")
    for name in skill_names
}


def iter_text_files(skill_dir: Path):
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file():
            continue
        try:
            yield path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue


def referenced_skills(skill_name: str):
    found = set()
    for content in iter_text_files(skill_dirs[skill_name]):
        for candidate in skill_names:
            if candidate == skill_name or candidate in found:
                continue
            if patterns[candidate].search(content):
                found.add(candidate)
    return sorted(found)


resolved = []
seen = set(selected)
queue = deque(selected)

while queue:
    skill_name = queue.popleft()
    for dependency in referenced_skills(skill_name):
        if dependency in seen:
            continue
        seen.add(dependency)
        resolved.append(dependency)
        queue.append(dependency)

for skill_name in resolved:
    print(skill_name)
PY
  )
}

prune_unselected_skills() {
  local source_dir
  local base_name
  local target_dir

  ((${#SELECTED_SKILLS[@]} == 0)) && return 0

  while IFS= read -r -d '' source_dir; do
    base_name="$(basename "$source_dir")"

    if has_selected_skill "$base_name"; then
      continue
    fi

    target_dir="${SKILLS_DEST}/${PREFIX}${base_name}"
    rm -rf "$target_dir"
  done < <(find "$SKILLS_SRC" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)
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
  done < <(iter_skill_source_dirs)
}

copy_references() {
  rm -rf "$REFERENCES_DEST"
  cp -Rp "$REFERENCES_SRC" "$REFERENCES_DEST"
  COPIED_REFERENCE_DIRS+=("$REFERENCES_DEST")
}

parse_args "$@"

[[ -n "$PREFIX" ]] || {
  echo "Prefix must not be empty" >&2
  exit 1
}

sync_source_root

[[ -d "$AGENTS_SRC" ]] || {
  echo "Missing agents source directory: $AGENTS_SRC" >&2
  exit 1
}

[[ -d "$SKILLS_SRC" ]] || {
  echo "Missing skills source directory: $SKILLS_SRC" >&2
  exit 1
}

[[ -d "$REFERENCES_SRC" ]] || {
  echo "Missing references source directory: $REFERENCES_SRC" >&2
  exit 1
}

validate_selected_skills
resolve_selected_skills

readonly NAME_MAP_FILE="$(mktemp)"
trap 'rm -f "$NAME_MAP_FILE"' EXIT

mkdir -p "$AGENTS_DEST" "$SKILLS_DEST" "$(dirname "$REFERENCES_DEST")"

build_name_map "$NAME_MAP_FILE"
copy_agents
prune_unselected_skills
copy_skills
copy_references
rewrite_references "$NAME_MAP_FILE"

echo "Installed addy agents to $AGENTS_DEST"
echo "Installed addy skills to $SKILLS_DEST"
echo "Installed addy references to $REFERENCES_DEST"
