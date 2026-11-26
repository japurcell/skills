# Live router reuse regression

Run the [shared prompt](fixtures/router-reuse.txt) once per caller in a fresh workspace. Keep the grader and its expectations outside the workspace. From the repository root, run the following in Bash or Zsh with a signed-in Codex CLI. The loop makes two live model runs and retains their native parent rollouts.

```sh
(
set -e
trial=$(mktemp -d)
for caller in execplan-implement delegate-to-subagents; do
  work="$trial/$caller"
  mkdir -p "$work/.agents/skills"
  cp -R "skills/default/$caller" skills/default/subagent-model-router "$work/.agents/skills/"
  printf 'release = ivy\nartifact = release-ivy.txt\n' > "$work/manifest.txt"
  printf 'checksum = 7814\n' > "$work/release-ivy.txt"
  sed "s/{caller}/$caller/g" scripts/tests/orchestration/fixtures/router-reuse.txt > "$work/prompt.txt"
  codex exec --ignore-user-config --enable multi_agent --skip-git-repo-check \
    -s workspace-write -C "$work" --json - < "$work/prompt.txt" > "$work/trace.jsonl"
  thread=$(python3 -c 'import json,sys; print(json.loads(open(sys.argv[1]).readline())["thread_id"])' "$work/trace.jsonl")
  rollout=$(find "${CODEX_HOME:-$HOME/.codex}/sessions" -name "*-$thread.jsonl")
  python3 scripts/tests/orchestration/grade_router_reuse.py "$caller" "$rollout"
done
)
```

Grade each caller independently. The parent must load router instructions once, read CLI help once, and run two successful routing evaluations. The first precedes spawn. The second follows the worker’s first completion and precedes the follow-up call to that same worker. Both routes must authorize the model and effort sent in the original spawn call. Host-default effort requires an omitted spawn argument. The grader recognizes a model-wide blocker from a matching failed spawn receipt reporting an unavailable or unsupported primary model. Other blocker formats need manual verification. Check the final result against both fixture files. The expected release is `ivy` and checksum is `7814`.

The grader prints native rollout line numbers and observed worker IDs. Exit 0 means the expected sequence matched, 1 means a mismatch, and 2 means invalid input or insufficient dispatch evidence. Review the command evidence for indirect or compound reads and invocations, which the direct-command matcher cannot reliably interpret. Count each actual operation, including a reload embedded in a larger command. Ignore mentions in assignment records. Mark missing or ambiguous evidence inconclusive. Preserve both the raw trace and any manual finding. Compact `codex exec --json` output alone can omit dispatch arguments.
