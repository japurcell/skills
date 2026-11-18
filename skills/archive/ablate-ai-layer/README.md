# Maintenance

This bundle originated at `coleam00/skills/.claude/skills/ablate-ai-layer` and is
now maintained locally. The import script deliberately leaves it untouched.
Review upstream updates manually so they preserve local discovery and process
ownership.

Run the public CLI suite from the repository root:

```sh
python3 skills/archive/ablate-ai-layer/scripts/test_ablation.py
```

Tests use disposable Git repositories and local fake runners, with no agent API
calls. They cover help and usage errors, reference discovery and stripping scope,
repository containment, timeout escalation, normal-exit descendant cleanup, and
SIGTERM cancellation. Stream tests cover exact binary bytes, long Claude JSON and
Codex-shaped JSONL, malformed/partial JSON, invalid UTF-8, arrays/scalars, malformed
optional metadata, empty streams, queued cancellation, explicit retention, and
controlled shutdown/cleanup failures. The suite is registered in
`scripts/test-all.py`. These offline fixtures establish harness behavior, not a
live provider's transcript completeness or billing accuracy.

Outcome regressions also cover nonzero runner exits with JSON output, invalid task
inputs, history exclusions through direct patterns and aliases, and empty stripped
arms. Agent diffs use a Git tree captured after preparation, so setup removals do
not count as agent work.

Discovery follows Markdown links, reference-style links, and inline code paths
from known instruction artifacts. Directory references in instruction entrypoints
expand Markdown context. Secondary documents can link files but directory mentions
there do not expand whole source trees. External references, paths outside the
repository, and `plans`, `archive`, and `archives` directories are excluded.
References are candidates for instruction context, not proof they load every time.
`referenced_by` records provenance. Explicit Claude `@file` imports inherit the
source's loading scope; other references are on-demand.

Agent execution requires POSIX process groups. Runner descendants must stay in
their inherited group: deliberately detached services are outside this ownership
contract. A timeout or cancellation sends TERM, then KILL if necessary, and verifies
group disappearance before deleting the worktree. If verification fails, the run
is unusable and `worktree_kept` records the retained location. Mapping and dry-run
work without POSIX execution support. Native Windows execution requires a future
implementation with equivalent process ownership.

## Result artifacts

`--out` is resolved to an absolute path before execution. Choose a fresh external
directory for each invocation to preserve previous results; reusing one can
overwrite files with matching run names. Each arm/index writes:

- `control-1.stdout` and `control-1.stderr` (and corresponding stripped/run
  names): complete binary runner output, redirected directly to durable files.
- `control-1.diff`: agent changes against the prepared Git tree, including new
  files staged by `git add -A`. Setup stripping is excluded. No diff file is
  written when no diff was collected.
- `summary.json`: comparison metadata and per-run records, excluding diff bodies.
- `task.md`: the prompt supplied to runners.

Raw streams remain after worktree removal, including nonzero exit, malformed
output, timeout, and orderly SIGINT/SIGTERM cancellation. Pre-launch cancellation
has empty stream files. Binary bytes are never decoded or rewritten in the raw
artifacts; only previews replace invalid UTF-8. File retention is not a guarantee
against host crashes, power loss, disk failure, or runners deliberately detaching
from their inherited process group.

### Per-run stream and lifecycle fields

Existing arm/index, removed-file, duration, exit, error, diff/file-change, and
usability fields remain. Fields that require a completed runner or collected diff
may be absent on failure. Stream and lifecycle fields are:

| Field | Type | Meaning |
| --- | --- | --- |
| `stdout_path`, `stderr_path` | absolute string | Raw files outside disposable runner worktrees |
| `stdout_bytes`, `stderr_bytes` | nonnegative integer | Raw file sizes observed during finalization |
| `result_text` | string, at most 4,000 characters | Claude string result when recognized; otherwise decoded raw stdout prefix |
| `stderr_tail` | string, at most 600 characters | Decoded stderr suffix |
| `result_text_truncated`, `stderr_tail_truncated` | boolean | Whether the corresponding decoded preview omits characters |
| `shutdown_confirmed` | boolean | No owned process group remains; true also when none was launched |
| `cleanup_status` | string enum | `removed`, `retained`, `failed`, or `not_created` |

Truncation flags describe previews, not whether raw capture is complete. Parseable
Claude JSON dictionaries recognize well-typed `is_error`, string `result`, numeric
`total_cost_usd` as `cost_usd`, integer `num_turns`, and integer
`usage.output_tokens` as `output_tokens`. A nonzero exit or boolean
`is_error: true` makes the run unusable. Unknown text, JSONL, malformed/partial
JSON, non-dictionary JSON, and malformed optional metadata fall back safely
without discarding the streams or otherwise valid diffs. No provider-specific
JSONL semantics are inferred.

`removed` means worktree cleanup completed. `retained` means explicit
`--keep-worktrees` or unconfirmed shutdown; `failed` means cleanup raised an error;
`not_created` means no worktree was created. Retention and cleanup failure include
`worktree_kept`. Unconfirmed shutdown and cleanup failure force `ok: false`.
Explicit retention alone can remain usable. Inspect the diagnostic and confirm
process absence before manual cleanup. If shutdown is unconfirmed, descendants
may still write to raw files, so byte counts are observations rather than a
terminal completeness guarantee. Filesystem errors can prevent artifact creation
or metadata finalization and are reported as run failures.

## Capture gate and grading

Within the approved budget, run one pair first. Both raw streams must remain
accessible after cleanup with matching byte counts; stdout must include the
expected final answer or provider terminal event. Verify usable diffs including
new files, confirmed shutdown, and completed cleanup (or intentional
`--keep-worktrees`). Exit 0 and nonempty diffs alone are insufficient. Stop before
more spend on missing or inadequate capture; preserve the failed output and use a
fresh directory for a replacement gate. A passing pair counts toward the approved
run total.

Grade workflow/tool claims using full raw streams as well as diffs. Previews and
final assertions cannot prove unobserved tool results. Keep raw originals intact
and create neutral shuffled grading copies that remove arm-revealing instruction
contents, labels, and paths; record redactions and untestable claims. The runtime
procedure is in [SKILL.md](SKILL.md); the evidence and blinding rubric is in
[comparison.md](references/comparison.md).
