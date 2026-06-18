Orchestrator -> self-improve inputs:
- Provide: dirname(prd_file)+"/progress.txt" `## Codebase Patterns` block; all Progress blocks (per-story and FINALIZATION) plus prd.json story metadata (id, title, priority, passes).

Mining scope:
- From every Progress block extract: "Patterns discovered", "Gotchas encountered", "Useful context"; include FINALIZATION notes.

Preserve as durable guidance:
- Module conventions, non-obvious gotchas, testing expectations (time ranges, staged dist), config/env requirements, UX invariants, validation rules (decoded-prefix), accessibility rules (aria-describedby order), cache vs fresh-fetch pattern, test-framework quirks.

Do NOT record story-specific step-by-step fixes or file lists; generalize into reusable rules.
