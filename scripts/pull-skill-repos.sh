#!/usr/bin/env bash
set -u -o pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly CONFIG_FILE="$REPO_ROOT/../skills.code-workspace"

had_error=0
success_count=0
failure_count=0
failed_paths=()

if [ ! -e "$CONFIG_FILE" ] && [ ! -L "$CONFIG_FILE" ]; then
  echo "[INFO] Skipping workspace repository updates: optional config file not found: $CONFIG_FILE" >&2
  exit 0
fi

command -v python3 >/dev/null 2>&1 || {
  echo "Error: Python 3 is required to read the VS Code workspace file." >&2
  exit 1
}

folder_paths="$(python3 "$REPO_ROOT/scripts/read-workspace-folders.py" "$CONFIG_FILE")" || {
  echo "Error: failed to parse config file: $CONFIG_FILE" >&2
  exit 1
}

while IFS= read -r FOLDER_PATH; do
  [ -n "$FOLDER_PATH" ] || continue

  TARGET_DIR="$REPO_ROOT/../$FOLDER_PATH"

  if [ ! -d "$TARGET_DIR" ]; then
    echo "Directory does not exist: $TARGET_DIR" >&2
    had_error=1
    failure_count=$((failure_count + 1))
    failed_paths+=("$FOLDER_PATH")
    continue
  fi

  if [ ! -d "$TARGET_DIR/.git" ]; then
    echo "Not a git repository: $TARGET_DIR" >&2
    had_error=1
    failure_count=$((failure_count + 1))
    failed_paths+=("$FOLDER_PATH")
    continue
  fi

  echo "Updating $TARGET_DIR"
  
  if ! (
    cd "$TARGET_DIR" && git pull
  ); then
    echo "Failed to update $TARGET_DIR" >&2
    had_error=1
    failure_count=$((failure_count + 1))
    failed_paths+=("$FOLDER_PATH")
    continue
  fi

  success_count=$((success_count + 1))
done <<< "$folder_paths"

echo
echo "Done."
echo "Succeeded: $success_count"
echo "Failed:    $failure_count"

if [ "$failure_count" -gt 0 ]; then
  echo "Failed paths:" >&2
  for path in "${failed_paths[@]}"; do
    echo "  - $path" >&2
  done
fi

exit "$had_error"
