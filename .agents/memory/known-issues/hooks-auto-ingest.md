---
type: Known Issue
description: Source auto-ingest hook failures and recovery; load only for scanners, injectors, pending gates, summaries, or manifest behavior
---

# Hook Auto-Ingest - Known Issues

## Manifest summary paths can traverse directories

Treat manifest `summary_path` values as untrusted. Reduce previous summary paths to `Path(summary_name).name` before resolving them below the summaries directory.

## Expected manifests and linked parents cannot establish freshness

Missing/damaged expected manifests, duplicate keys, non-finite JSON, boolean versions and invalid entry types remain unavailable before scaffold/save effects. Validate every linked path component before raw/summary/manifest/skill access; checking only the endpoint permits linked parent writes. Keep legacy summary-path strings basename-scoped. Canonical locks must fail closed on timeout/unavailability and support Windows byte locking without an unlocked fallback.

## Active semantic ingestion needs pre-effect inverse history

A scanner success or manually current manifest cannot establish semantic integration. Activated source passes retain pre-pass summary/knowledge bases, propose semantic bytes through checked reversible publication, and bind exact current source/summary evidence. Direct canonical changes followed by recover are preserved and rejected. Verified no-change may keep attributable prior guidance notes if they already establish current source claims. Source drift retains joined work; removed-source orphan review stays separate from ingesting existing sources.

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
