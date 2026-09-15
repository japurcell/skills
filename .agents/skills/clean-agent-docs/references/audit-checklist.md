# Agent-Docs Audit Checklist

Use this checklist when reviewing each relevant file.

## 1. Purpose and loading

Confirm:

- The file has one clear purpose.
- Its intended reader and trigger are clear.
- Default-loaded content applies to most tasks.
- Specialized content is linked rather than loaded by default.
- Pointers say:
  - what to read,
  - when to read it,
  - when the larger document is unnecessary.

## 2. Content quality

Find and fix:

- Duplicate or near-duplicate rules
- Stale instructions
- Contradictory requirements
- Broken, missing, or circular links
- Ambiguous ownership of guidance
- Session history or completed-task notes
- Raw command, script, or debug dumps
- Excessive explanation, examples, or headings
- Mixed topics with different loading triggers

Use direct, imperative language. Prefer short lists and explicit conditions that weaker models can follow.

## 3. Memory indexes

For `.agents/memory/INDEX.md`, confirm:

- Every durable memory document is indexed.
- Every index target exists.
- Each entry explains when to load the target.
- Entries distinguish similar documents.
- Removed or renamed documents have no stale entries.

## 4. Contradictions

When rules conflict:

1. Prefer the source with narrower scope.
2. Prefer explicit repository policy over examples or historical notes.
3. Preserve safety and required process constraints.
4. If authority remains unclear, do not guess. Record the conflict in the final report.

## 5. Removal decisions

Classify removed content in working notes:

- **MOVE** — unique, durable guidance. Move it to the narrowest relevant document.
- **DROP** — exact duplicates, stale task state, session history, secrets, or noncanonical raw dumps.

Redact secrets; never move them into another document.

Before deleting a section, verify that all durable guidance remains available from an appropriate load path.
