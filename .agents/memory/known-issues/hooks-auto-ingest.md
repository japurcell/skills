---
type: Known Issue
description: Source auto-ingest hook failures and recovery; load only for scanners, injectors, pending gates, summaries, or manifest behavior
---

# Hook Auto-Ingest - Known Issues

## Manifest summary paths can traverse directories

Treat manifest `summary_path` values as untrusted. Reduce previous summary paths to `Path(summary_name).name` before resolving them below the summaries directory.

## Literal draft searches create permanent pending loops

Searching an entire summary for `status: draft` misclassifies completed bodies that mention the phrase. Parse frontmatter, require `type: Source Summary` plus draft status semantics, normalize quoted or commented top-level scalars, and ignore body text.

## Prompt-time injection must complement startup scanning

Copilot `userPromptTransformed` can run before `sessionStart`; startup context alone can miss the first model-facing prompt. Keep the repo-local startup scanner for persistent state and pair it with the prompt-time injector. Gemini needs the equivalent `BeforeAgent` pairing.

## Separate Copilot stop hooks can lose a blocking reason

Live simultaneous-failure evidence preserved only the later reason. Register `.github/hooks/scripts/validate-stop.py` as one stop entry point, keep both validators independent, and combine source-ingest before OKF.

## Pending gates need canonical recovery and a backstop

Prompt-time context only steers. Keep the final-response denial active while manifest entries remain blocking. Use `.agents/skills/ingest-source/SKILL.md` as the recovery path; if the skill is missing or broken, show the short inline checklist and keep the gate closed.

## Gemini final response is `AfterAgent`

Use `AfterAgent` for final-response completion and pending-ingest denial. Reserve `AfterModel` for intentional per-model-output observability.
