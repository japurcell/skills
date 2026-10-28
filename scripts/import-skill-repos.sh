#!/usr/bin/env bash
set -u -o pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly SCRIPT_DIR
readonly CHILD_SCRIPT="$SCRIPT_DIR/pull-skill-repos.sh"

if [[ ! -x "$CHILD_SCRIPT" ]]; then
  echo "Error: child script is not executable: $CHILD_SCRIPT" >&2
  exit 1
fi

failures=()
failure_details=()
STEP_LOG="$(mktemp)" || {
  echo "[ERROR] Could not create a temporary file for import diagnostics." >&2
  exit 1
}
cleanup() {
  rm -f -- "$STEP_LOG"
}
trap cleanup EXIT

run_step() {
  local label="$1" status line
  shift
  printf '[INFO] Starting %s\n' "$label" >&2
  if "$@" 2>&1 | tee "$STEP_LOG" >&2; then
    printf '[INFO] Completed %s\n' "$label" >&2
  else
    status=$?
    printf '[ERROR] %s failed (exit %s). See diagnostics above. Command:' "$label" "$status" >&2
    printf ' %q' "$@" >&2
    printf '\n' >&2
    failures+=("$label (exit $status)")
    while IFS= read -r line; do
      case "$line" in
        "[ERROR] "*|"Error: "*) failure_details+=("$label: $line") ;;
      esac
    done < "$STEP_LOG"
  fi
}

run_step "workspace repository updates" "$CHILD_SCRIPT"

run_step "JuliusBrussee/caveman" "$SCRIPT_DIR/copy-from-git.sh" \
  --repo "https://github.com/JuliusBrussee/caveman.git" \
  "skills/caveman" "skills/default"

run_step "anthropics/claude-plugins-official" "$SCRIPT_DIR/copy-from-git.sh" \
  --repo "https://github.com/anthropics/claude-plugins-official.git" \
  "plugins/frontend-design/skills/frontend-design/SKILL.md" "skills/default/frontend-design/SKILL.md" \
  "plugins/skill-creator/skills/skill-creator" "skills/default"

run_step "mattpocock/skills" "$SCRIPT_DIR/copy-from-git.sh" \
  --repo "https://github.com/mattpocock/skills.git" --clone-dir "mattpocock-skills" \
  "skills/engineering/code-review/" "skills/default/code-review-biaxis/" \
  "skills/engineering/codebase-design" "skills/default" \
  "skills/engineering/improve-codebase-architecture" "skills/default" \
  "skills/engineering/pr" "skills/default" \
  "skills/engineering/prototype" "skills/default" \
  "skills/engineering/research" "skills/default" \
  "skills/engineering/retro" "skills/default" \
  "skills/engineering/tdd" "skills/default" \
  "skills/engineering/wayfinder" "skills/default" \
  "skills/productivity/grilling" "skills/default" \
  "skills/productivity/teach" "skills/default" \
  "skills/productivity/writing-for-agents" "skills/default"

run_step "addyosmani/web-quality-skills" "$SCRIPT_DIR/copy-from-git.sh" \
  --repo "https://github.com/addyosmani/web-quality-skills.git" \
  "skills/accessibility/" "skills/default/web-accessibility" \
  "skills/best-practices/" "skills/default/web-best-practices" \
  "skills/performance/" "skills/default/web-performance"

run_step "humanlayer/skills" "$SCRIPT_DIR/copy-from-git.sh" \
  --repo "https://github.com/humanlayer/skills.git" --clone-dir "humanlayer-skills" \
  "plugins/show-me/skills/show-me" "skills/default"

# "$SCRIPT_DIR/copy-from-git.sh" \
#   "https://github.com/kunchenguid/lavish-axi.git" \
#   "skills/lavish" "skills/default"

# "$SCRIPT_DIR/copy-from-git.sh" \
#   --repo "https://github.com/JoelQ/skills.git" --clone-dir "JoelQ-skills" \
#   "retro/" "skills/default/retro-automate/"

if (( ${#failures[@]} )); then
  printf '[ERROR] Import completed with %s failed step(s):\n' "${#failures[@]}" >&2
  printf '  - %s\n' "${failures[@]}" >&2
  if (( ${#failure_details[@]} )); then
    printf '[ERROR] Failure details:\n' >&2
    printf '  - %s\n' "${failure_details[@]}" >&2
  fi
  exit 1
fi
printf '[INFO] All import steps completed successfully.\n' >&2
