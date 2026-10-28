---
name: ruminate
description: Mine past conversations for uncaptured patterns, corrections, and knowledge. Cross-references with existing brain content. Triggers on "ruminate", "mine my history", "what have I been working on", "review past sessions", "extract learnings".
disable-model-invocation: true
---

# Ruminate

Mine conversation history for brain-worthy knowledge that was never captured. Complements `reflect` (current session) and `meditate` (brain vault audit) by looking at the full archive of past conversations across available providers.

## Process

Track each step through the available planning tools or a short checklist.

### 1. Read the brain

Create one temporary directory with Python's `tempfile.mkdtemp(prefix="ruminate-")`. Retain its exact path for extraction, snapshot, findings, and cleanup. Run the snapshot helper with Python 3.12+:

`python <meditate-skill-path>/scripts/snapshot.py brain <temporary-directory>/brain-snapshot.md`

Use the available Python 3.12+ executable (`python`, `python3`, or `py -3.12`). Pass the snapshot path to each analysis agent. This avoids loading the full brain into the ruminate orchestrator's context.

### 2. Locate conversations

Find available supported provider roots:

1. Claude project directory:
   `~/.claude/projects/-<cwd-with-dashes-replacing-slashes>/`
2. Codex sessions root:
   `~/.codex/sessions/`

The bundled extractor supports Claude and Codex JSONL formats only. Other provider histories require a separate supported extraction route; do not pass unsupported options to this script.

### 3. Extract conversations

Run the extraction script to parse both JSONL formats into readable text and split into batches:

```python
from pathlib import Path
import subprocess
import sys

subprocess.run([
    sys.executable, "<ruminate-skill-path>/scripts/extract-conversations.py",
    "<temporary-directory>/extracted",
    "--claude-dir", str(Path.home() / ".claude/projects/<project-slug>"),
    "--codex-dir", str(Path.home() / ".codex/sessions"),
    "--cwd", str(Path.cwd()), "--batches", "2",
], check=True)
```

Replace placeholders with actual skill and temporary paths; omit unavailable provider options. Choose the batch count based on total extracted conversations (Claude + Codex): ~1 batch per 20 conversations, minimum 2, maximum 10.

Keep `--cwd` for project-scoped extraction: it includes only conversations with matching working-directory metadata, skipping different or missing attribution even within a provider's project directory. Omitting `--cwd` leaves extraction unfiltered by project.

### 4. Spawn analysis team

Analyze each batch with available general analysis subagents, following the model-routing skill when available and respecting harness concurrency limits. Use bounded local passes if delegation is unavailable.

Each agent's prompt should include:

- The actual batch manifest path (`<temporary-directory>/extracted/batches/batch_N.txt`)
- The actual output path (`<temporary-directory>/findings_N.md`)
- The list of topics **already captured** in the brain (compiled from step 1) - so agents skip known knowledge
- A reminder that each extracted file includes provider/source metadata headers (`[PROVIDER]`, `[CWD]`, `[SOURCE_FILE]`) and should be used as evidence context
- Instructions to extract from each conversation:
  - **User corrections**: times the user corrected the assistant's approach, code, or understanding
  - **Recurring preferences**: things the user explicitly asked for or pushed back on repeatedly
  - **Technical learnings**: codebase-specific knowledge, gotchas, patterns discovered
  - **Workflow patterns**: how the user prefers to work
  - **Frustrations**: friction points, wasted effort, things that went wrong
  - **Skills wished for**: capabilities the user expressed wanting

Agents write structured findings to their output files.

### 5. Synthesize

After all agents complete, read all findings files. Cross-reference with existing brain content. Deduplicate across batches.

**Filter by frequency and impact.** Most findings won't be worth adding. Apply these filters before presenting:

- **Frequency**: Did this come up in multiple conversations, or was the user correcting the same mistake repeatedly? One-off corrections are usually not worth a brain entry - the brain should capture _patterns_, not incidents.
- **Factual accuracy**: Is something in the brain now wrong? (e.g. a rule was disabled but the brain still documents it as active). These are always worth fixing regardless of frequency.
- **Impact**: Would failing to capture this cause repeated wasted effort in future sessions? A gotcha that cost 5 minutes once is low-impact. A pattern that caused 3 rounds of corrections is high-impact.

**Discard aggressively.** It's better to present 3 high-signal findings than 9 that include noise. If a finding only happened once and isn't a factual correction, skip it.

### 6. Present and apply

Present findings to the user in a table with columns: finding, frequency/evidence, and proposed action. Be honest about which findings are one-offs vs. recurring patterns - let the user decide what's worth adding.

**Route skill-specific learnings.** Check if any findings are about how a specific skill should work - its process, prompts, edge cases, or troubleshooting. Update the skill's SKILL.md or references/ directly. Read the skill first to avoid duplicating or contradicting existing content.

Apply only the changes the user approves. Follow brain writing conventions:

- One topic per file, organized in directories
- Use file-relative Markdown links to connect related notes
- Activate the `brain` skill to maintain curated indexes and reconcile the root inventory, using manual indexing if hooks are unavailable
- Default to updating existing notes over creating new ones

### 7. Clean up

After all analysis finishes, remove only the temporary directory this invocation created. Replace the placeholder with the exact retained path, never a provider history directory:

```python
import shutil
shutil.rmtree("<temporary-directory>")
```

## Guidelines

- **Filter aggressively.** Most conversations will have low signal - automated tasks, trivial exchanges, already-captured knowledge. Only surface what's genuinely new and impactful.
- **Prefer reduction.** If a finding is a special case of an existing brain principle, update the existing note rather than creating a new one.
- **Quote the user.** When a finding stems from a direct user correction, include the user's words and source file path - they carry the most signal about what matters.
- **Shut down agents** when analysis is complete. Don't leave them idle.
