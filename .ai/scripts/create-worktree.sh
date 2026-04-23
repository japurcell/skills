#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <work-id> [base-branch]" >&2
  exit 1
fi

WORK_ID="$1"
BASE_BRANCH="${2:-main}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPO_NAME="$(basename "$REPO_ROOT")"
WORKTREE_PATH="${REPO_ROOT%/*}/${REPO_NAME}-${WORK_ID}"
BRANCH_NAME="ai/${WORK_ID}"

if [[ -d "$WORKTREE_PATH/.git" || -f "$WORKTREE_PATH/.git" ]]; then
  echo "Worktree already exists: $WORKTREE_PATH" >&2
  exit 1
fi

if git -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/${BRANCH_NAME}"; then
  git -C "$REPO_ROOT" worktree add "$WORKTREE_PATH" "$BRANCH_NAME"
else
  git -C "$REPO_ROOT" worktree add -b "$BRANCH_NAME" "$WORKTREE_PATH" "$BASE_BRANCH"
fi

echo "$WORKTREE_PATH"
