#!/usr/bin/env bash
set -u -o pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly SCRIPT_DIR
readonly CHILD_SCRIPT="$SCRIPT_DIR/pull-skill-repos.sh"

if [[ ! -x "$CHILD_SCRIPT" ]]; then
  echo "Error: child script is not executable: $CHILD_SCRIPT" >&2
  exit 1
fi

"$CHILD_SCRIPT"

"$SCRIPT_DIR/copy-from-git.sh" \
  "https://github.com/JuliusBrussee/caveman.git" \
  "skills/caveman" "skills"

"$SCRIPT_DIR/copy-from-git.sh" \
  "https://github.com/anthropics/claude-plugins-official.git" \
  "plugins/frontend-design/skills/frontend-design/SKILL.md" "skills/frontend-design/SKILL.md" \
  "plugins/skill-creator/skills/skill-creator" "skills"

"$SCRIPT_DIR/copy-from-git.sh" \
  "https://github.com/mattpocock/skills.git" \
  "skills/engineering/improve-codebase-architecture" "skills" \
  "skills/engineering/tdd" "skills" \
  "skills/engineering/to-issues" "skills" \
  "skills/engineering/to-prd" "skills" \
  "skills/engineering/setup-matt-pocock-skills" "skills" \
  "skills/engineering/codebase-design" "skills" \
  "skills/engineering/prototype" "skills" \
  "skills/engineering/resolving-merge-conflicts" "skills" \
  "skills/productivity/grill-me" "skills" \
  "skills/productivity/grilling" "skills" \
  "skills/productivity/teach" "skills" \
  "skills/productivity/writing-great-skills" "skills"
