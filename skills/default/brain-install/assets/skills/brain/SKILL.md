---
name: brain
description: Read/write brain files at brain/. Use when modifying any file in brain/. Use for any task that persists knowledge - reflection, planning, or direct edits. Use after debugging sessions, mistakes, corrections, architectural decisions, or any insight worth preserving across sessions. Use when the user says 'add to brain', 'remember this', or 'write a note'.
---

# Brain

Persistent memory across sessions at `brain/`.

The brain is the foundation of the entire workflow - every agent, skill, and session reads it. Low-quality or speculative content degrades everything downstream. Before adding anything, ask: "Does this genuinely improve how the system operates?" If the answer isn't a clear yes, don't write it.

## Before Writing

Read `brain/index.md` first. Then read the relevant entrypoint for your topic:

- `brain/principles.md` for principle updates
- `brain/plans/index.md` for plan-related notes

For other topics, read the dedicated index when present. Otherwise scan nearby files directly and edit an existing note when possible.

## Structure

```
brain/
├── index.md              ← root entry point, links to everything
├── principles.md         ← index for principles/
├── todos.md              ← product backlog
├── vision.md             ← elevator pitch + link to architecture
├── architecture.md       ← full technical reference
├── principles/           ← engineering and design principles
├── codebase/             ← project-specific knowledge and gotchas
├── plans/                ← numbered feature plans (02-arrow-bindings/, etc.)
└── audits/               ← design and quality audits (date-prefixed filenames, e.g. 2026-02-20-quality-audit.md)
```

**Rules:**

- One topic per file. `brain/codebase/noodle-spawn-gotchas.md`, not a mega-file.
- Maintain existing index entrypoints: `brain/index.md`, `brain/principles.md`, `brain/plans/index.md`.
- If you introduce a new top-level category, add an index-style entrypoint for it (links only, no inlined content).
- `brain/index.md` is the root. Every brain file must be reachable from it.
- File names: lowercase, hyphenated. `worktree-gotchas.md`.
- Plan directories: prefixed with the todo ID from `brain/todos.md`. `02-arrow-bindings/` with `overview.md` and `phase-N-*.md` inside.

## Links

Use standard Markdown links with destinations relative to the file containing the link, including the file extension: `[Topic](relative/topic.md)`. Use `../` for parent directories, preserve heading fragments such as `#section-heading`, and percent-encode spaces or special destination characters. Keep explicit link labels when converting existing references. Do not use Obsidian note-link syntax.

## Writing Style

- Bullets over prose. No preamble.
- Plain markdown with `# Title`. No Obsidian frontmatter.
- Keep notes under ~50 lines. Split if longer.

## After Writing

Let the brain hooks reconcile the machine-owned `brain/index.md` after additions or removals. If hooks are unavailable, run the bundled indexer manually with Python 3.12+. From the target repository root, run this Python snippet, replacing `<brain-skill-path>` with this skill's directory:

```python
import json
from pathlib import Path
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-I", "-S", "-B",
     "<brain-skill-path>/scripts/auto-index-brain.py", "--provider", "codex"],
    input=json.dumps({"cwd": str(Path.cwd()), "hook_event_name": "PostToolUse"}),
    text=True, capture_output=True,
)
print(result.stderr, end="")
```

The `codex` payload is a manual invocation format; Codex need not be installed. Check diagnostics and verify that `brain/index.md` contains the expected links: hooks can exit zero after reporting a nonblocking error. Keep human prose in topic notes. Also update the relevant existing curated entrypoint (`brain/principles.md` or `brain/plans/index.md`) when applicable. Keep indexes link-only and scannable.

## Durability Test

Ask: "Would I include this in a prompt for a _different_ task?"

- **Yes** → write to `brain/`. It's durable knowledge.
- **No, it's plan-specific** → update the plan's phase doc instead.
- **No, it's a skill issue** → update the skill file directly.
- **No, it needs follow-up work** → file a todo with the `todo` skill.

## Maintenance

- Delete outdated or subsumed notes.
- Delete random-named files in `brain/plans/` - stale plan-mode artifacts.
- Merge overlapping notes before adding new ones.
