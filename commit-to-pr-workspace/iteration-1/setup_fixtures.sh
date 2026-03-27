#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/adam/.agents/skills/commit-to-pr-workspace/iteration-1"

setup_repo() {
  local repo_path="$1"
  local spec_rel="$2"
  local issue_line="$3"
  local start_branch="$4"

  rm -rf "$repo_path"
  mkdir -p "$repo_path"
  pushd "$repo_path" >/dev/null

  git init >/dev/null
  git config user.name "Eval Bot"
  git config user.email "eval@example.com"
  git config commit.gpgsign false

  git checkout -q -B main

  mkdir -p specs src bin
  printf "# Commit-to-PR Eval Repo\n" > README.md
  printf "base line\n" > src/app.txt
  git add .
  git commit -qm "chore: initial commit"

  mkdir -p .remotes
  git init --bare .remotes/origin.git >/dev/null
  git remote add origin "$repo_path/.remotes/origin.git"
  git push -q -u origin main

  printf "feature update %s\n" "$(date +%s)" >> src/app.txt

  mkdir -p "$(dirname "$spec_rel")"
  {
    printf "# Spec\n"
    if [[ -n "$issue_line" ]]; then
      printf "%s\n" "$issue_line"
    fi
    printf "\n## Goal\n"
    printf "Prepare this change for review.\n"
  } > "$spec_rel"

  cat > bin/gh <<'GH'
#!/usr/bin/env bash
set -euo pipefail
cmd1="${1:-}"
cmd2="${2:-}"
if [[ "$cmd1" == "auth" && "$cmd2" == "status" ]]; then
  echo "github.com"
  echo "  ✓ Logged in to github.com as eval-bot"
  exit 0
fi
if [[ "$cmd1" == "pr" && "$cmd2" == "create" ]]; then
  branch="$(git branch --show-current)"
  echo "https://example.com/org/repo/pull/42"
  echo "PR_CREATED_BRANCH=$branch" > .gh_last_pr
  exit 0
fi
echo "gh stub: unsupported args: $*" >&2
exit 1
GH
  chmod +x bin/gh

  if [[ "$start_branch" != "main" ]]; then
    git checkout -q -b "$start_branch"
  fi

  popd >/dev/null
}

setup_repo "$ROOT/eval-0-invoice-export-main-branch/with_skill/repo" "specs/invoice-export.md" "Linked issue: #123" "main"
setup_repo "$ROOT/eval-0-invoice-export-main-branch/without_skill/repo" "specs/invoice-export.md" "Linked issue: #123" "main"

setup_repo "$ROOT/eval-1-existing-feature-branch/with_skill/repo" "specs/fix-rate-limit.md" "Linked issue: #456" "feat/rate-limit-fix"
setup_repo "$ROOT/eval-1-existing-feature-branch/without_skill/repo" "specs/fix-rate-limit.md" "Linked issue: #456" "feat/rate-limit-fix"

setup_repo "$ROOT/eval-2-no-linked-issue/with_skill/repo" "specs/add-audit-logs.md" "" "main"
setup_repo "$ROOT/eval-2-no-linked-issue/without_skill/repo" "specs/add-audit-logs.md" "" "main"

echo "Fixture repos initialized under $ROOT"
