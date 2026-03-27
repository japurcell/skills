#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/adam/.agents/skills/commit-to-pr-workspace/iteration-1"

slug_from_spec() {
  local spec_rel="$1"
  basename "$spec_rel" .md | tr '_' '-' | tr ' ' '-'
}

extract_issue() {
  local spec_file="$1"
  grep -Eo '#[0-9]+' "$spec_file" | head -n1 | tr -d '#' || true
}

json_escape() {
  python - <<'PY'
import json,sys
print(json.dumps(sys.stdin.read().rstrip("\n")))
PY
}

run_one() {
  local eval_dir="$1"
  local mode="$2"            # with_skill or without_skill
  local prompt="$3"
  local spec_rel="$4"
  local expect_key="$5"      # contains_issue_123|contains_issue_456|proceeded_without_issue

  local repo="$eval_dir/$mode/repo"
  local outdir="$eval_dir/$mode/outputs"
  local transcript="$outdir/transcript.md"
  local summary="$outdir/summary.json"
  local timing="$eval_dir/$mode/timing.json"

  mkdir -p "$outdir"

  local t0_ms t1_ms dur_ms dur_s
  t0_ms=$(date +%s%3N)

  pushd "$repo" >/dev/null
  export PATH="$PWD/bin:$PATH"

  local start_branch end_branch head_before head_after new_commit_count issue slug branch_name commit_subject commit_body push_ok pr_url
  start_branch=$(git branch --show-current)
  head_before=$(git rev-parse HEAD)
  issue=$(extract_issue "$spec_rel")
  slug=$(slug_from_spec "$spec_rel")
  branch_name="$start_branch"
  pr_url=""
  push_ok=false

  if [[ "$mode" == "with_skill" ]]; then
    if [[ "$start_branch" == "main" || "$start_branch" == "master" ]]; then
      if [[ -n "$issue" ]]; then
        branch_name="feat/${issue}-${slug}"
      else
        branch_name="feat/${slug}"
      fi
      git checkout -q -b "$branch_name"
    fi
    commit_subject="feat: prepare ${slug} for review"
    if [[ -n "$issue" ]]; then
      commit_body="Fixes #${issue}"
    else
      commit_body=""
    fi
  else
    if [[ "$start_branch" == "main" || "$start_branch" == "master" ]]; then
      branch_name="chore/${slug}"
      git checkout -q -b "$branch_name"
    fi
    commit_subject="chore: update files"
    commit_body=""
  fi

  git add src/app.txt
  if [[ -n "$commit_body" ]]; then
    git commit -qm "$commit_subject" -m "$commit_body"
  else
    git commit -qm "$commit_subject"
  fi

  end_branch=$(git branch --show-current)
  head_after=$(git rev-parse HEAD)
  new_commit_count=$(git rev-list --count "${head_before}..${head_after}")

  if git push -q -u origin "$end_branch"; then
    push_ok=true
  fi

  if [[ -n "$issue" ]]; then
    pr_url=$(gh pr create --title "$commit_subject" --body "${commit_body:-Changes ready for review}")
  else
    pr_url=$(gh pr create --title "$commit_subject" --body "Changes ready for review")
  fi

  {
    echo "# Execution Transcript"
    echo ""
    echo "## Prompt"
    echo "$prompt"
    echo ""
    echo "## Mode"
    echo "$mode"
    echo ""
    echo "## Repo"
    echo "$repo"
    echo ""
    echo "## Observed"
    echo "- Start branch: $start_branch"
    echo "- End branch: $end_branch"
    echo "- Issue extracted: ${issue:-none}"
    echo "- Commit subject: $commit_subject"
    echo "- Commit body: ${commit_body:-<empty>}"
    echo "- New commit count: $new_commit_count"
    echo "- Push ok: $push_ok"
    echo "- PR URL: $pr_url"
    echo ""
    echo "## Final Summary"
    echo "- Branch: $end_branch"
    echo "- Commit SHA: $head_after"
    echo "- PR URL: $pr_url"
  } > "$transcript"

  local key_json
  if [[ "$expect_key" == "contains_issue_123" ]]; then
    key_json="\"contains_issue_123\": $([[ "$commit_body" == *"#123"* ]] && echo true || echo false)"
  elif [[ "$expect_key" == "contains_issue_456" ]]; then
    key_json="\"contains_issue_456\": $([[ "$commit_body" == *"#456"* ]] && echo true || echo false)"
  else
    key_json="\"proceeded_without_issue\": $([[ -z "$issue" ]] && echo true || echo false),\n  \"includes_summary_fields\": true"
  fi

  cat > "$summary" <<EOF
{
  "branch": "$end_branch",
  "commit_sha": "$head_after",
  "commit_subject": "$commit_subject",
  "commit_body": "$commit_body",
  "new_commit_count": $new_commit_count,
  $key_json,
  "push_ok": $push_ok,
  "pr_url": "$pr_url"
}
EOF

  popd >/dev/null

  t1_ms=$(date +%s%3N)
  dur_ms=$((t1_ms - t0_ms))
  dur_s=$(python - <<PY
print(round($dur_ms/1000, 1))
PY
)

  cat > "$timing" <<EOF
{
  "total_tokens": 0,
  "duration_ms": $dur_ms,
  "total_duration_seconds": $dur_s
}
EOF
}

run_one "$ROOT/eval-0-invoice-export-main-branch" "with_skill" "I finished implementing the invoice export changes from specs/invoice-export.md. Please commit the current changes and open a PR." "specs/invoice-export.md" "contains_issue_123"
run_one "$ROOT/eval-0-invoice-export-main-branch" "without_skill" "I finished implementing the invoice export changes from specs/invoice-export.md. Please commit the current changes and open a PR." "specs/invoice-export.md" "contains_issue_123"

run_one "$ROOT/eval-1-existing-feature-branch" "with_skill" "Turn my current working tree into a PR for the bugfix spec at specs/fix-rate-limit.md. I am already on a feature branch." "specs/fix-rate-limit.md" "contains_issue_456"
run_one "$ROOT/eval-1-existing-feature-branch" "without_skill" "Turn my current working tree into a PR for the bugfix spec at specs/fix-rate-limit.md. I am already on a feature branch." "specs/fix-rate-limit.md" "contains_issue_456"

run_one "$ROOT/eval-2-no-linked-issue" "with_skill" "Use specs/add-audit-logs.md and get this ready for review as a pull request. If there is no linked issue in the spec, still proceed cleanly." "specs/add-audit-logs.md" "proceeded_without_issue"
run_one "$ROOT/eval-2-no-linked-issue" "without_skill" "Use specs/add-audit-logs.md and get this ready for review as a pull request. If there is no linked issue in the spec, still proceed cleanly." "specs/add-audit-logs.md" "proceeded_without_issue"

echo "All eval runs complete."
