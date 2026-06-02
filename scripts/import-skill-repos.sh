#!/usr/bin/env bash
set -u -o pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly SCRIPT_DIR

"$SCRIPT_DIR/copy-from-git.sh" \
  "https://github.com/JuliusBrussee/caveman.git" \
  "skills/caveman/SKILL.md" "skills/caveman/SKILL.md"