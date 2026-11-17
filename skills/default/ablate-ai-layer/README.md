# Maintenance

This bundle originated at `coleam00/skills/.claude/skills/ablate-ai-layer` and is
now maintained locally. The import script deliberately leaves it untouched.
Review upstream updates manually so they preserve local discovery and process
ownership.

Run the public CLI suite from the repository root:

```sh
python3 skills/default/ablate-ai-layer/scripts/test_ablation.py
```

Tests use disposable Git repositories and local fake runners, with no agent API
calls. They cover help and usage errors, reference discovery and stripping scope,
repository containment, timeout escalation, normal-exit descendant cleanup, and
SIGTERM cancellation. The suite is registered in `scripts/test-all.py`.

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
