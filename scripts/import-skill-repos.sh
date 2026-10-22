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
  "skills/caveman" "skills/default"

"$SCRIPT_DIR/copy-from-git.sh" \
  "https://github.com/anthropics/claude-plugins-official.git" \
  "plugins/frontend-design/skills/frontend-design/SKILL.md" "skills/default/frontend-design/SKILL.md" \
  "plugins/skill-creator/skills/skill-creator" "skills/default"

"$SCRIPT_DIR/copy-from-git.sh" \
  "https://github.com/mattpocock/skills.git" \
  "skills/engineering/code-review/" "skills/default/code-review-biaxis/" \
  "skills/engineering/codebase-design" "skills/default" \
  "skills/engineering/improve-codebase-architecture" "skills/default" \
  "skills/engineering/pr" "skills/default" \
  "skills/engineering/prototype" "skills/default" \
  "skills/engineering/research" "skills/default" \
  "skills/engineering/resolving-merge-conflicts" "skills/default" \
  "skills/engineering/tdd" "skills/default" \
  "skills/engineering/wayfinder" "skills/default" \
  "skills/in-progress/retro" "skills/default" \
  "skills/productivity/grilling" "skills/default" \
  "skills/productivity/teach" "skills/default" \
  "skills/productivity/writing-for-agents" "skills/default"

"$SCRIPT_DIR/copy-from-git.sh" \
  "https://github.com/addyosmani/web-quality-skills.git" \
  "skills/accessibility/" "skills/default/web-accessibility" \
  "skills/best-practices/" "skills/default/web-best-practices" \
  "skills/performance/" "skills/default/web-performance" \

"$SCRIPT_DIR/copy-from-git.sh" \
  "https://github.com/humanlayer/skills.git" \
  "plugins/show-me/skills/show-me" "skills/default"

# "$SCRIPT_DIR/copy-from-git.sh" \
#   "https://github.com/kunchenguid/lavish-axi.git" \
#   "skills/lavish" "skills/default"

# "$SCRIPT_DIR/copy-from-git.sh" \
#   "https://github.com/JoelQ/skills.git" \
#   "retro/" "skills/default/retro-automate/"
