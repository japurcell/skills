#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <work-id> [base-branch]" >&2
  exit 1
fi

WORK_ID="$1"
BASE_BRANCH="${2:-main}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ARTIFACT_DIR="$REPO_ROOT/.ai/artifacts/$WORK_ID"
TEMPLATES_DIR="$REPO_ROOT/.ai/templates"

CREATE_WORKTREE_SCRIPT="$REPO_ROOT/.ai/scripts/create-worktree.sh"
if ! WORKTREE_PATH="$($CREATE_WORKTREE_SCRIPT "$WORK_ID" "$BASE_BRANCH")"; then
  echo "Failed to create worktree for '$WORK_ID' from base '$BASE_BRANCH'." >&2
  exit 1
fi

mkdir -p "$ARTIFACT_DIR"
cp "$TEMPLATES_DIR/00-intake.md" "$ARTIFACT_DIR/00-intake.md"
cp "$TEMPLATES_DIR/02-exploration-summary.md" "$ARTIFACT_DIR/02-exploration-summary.md"
cp "$TEMPLATES_DIR/03-research-findings.md" "$ARTIFACT_DIR/03-research-findings.md"
cp "$TEMPLATES_DIR/04-clarifications.md" "$ARTIFACT_DIR/04-clarifications.md"
cp "$TEMPLATES_DIR/05-plan.md" "$ARTIFACT_DIR/05-plan.md"
cp "$TEMPLATES_DIR/06-task-graph.yaml" "$ARTIFACT_DIR/06-task-graph.yaml"
cp "$TEMPLATES_DIR/08-code-review.md" "$ARTIFACT_DIR/08-code-review.md"
cp "$TEMPLATES_DIR/08-security-review.md" "$ARTIFACT_DIR/08-security-review.md"
cp "$TEMPLATES_DIR/08-tech-debt.md" "$ARTIFACT_DIR/08-tech-debt.md"
cp "$TEMPLATES_DIR/09-verification.md" "$ARTIFACT_DIR/09-verification.md"

cat > "$ARTIFACT_DIR/01-worktree.md" <<EON
---
work_id: $WORK_ID
phase: "01"
status: complete
depends_on: ["00"]
updated_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)
---

# Worktree setup

- Branch: ai/$WORK_ID
- Base branch: $BASE_BRANCH
- Worktree path: $WORKTREE_PATH
EON

echo "Initialized workflow artifacts at: $ARTIFACT_DIR"
echo "Worktree path: $WORKTREE_PATH"
