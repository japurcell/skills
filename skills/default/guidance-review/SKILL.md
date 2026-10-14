---
name: guidance-review
description: Review guidance for contradictions, ambiguity, duplication, omissions, and opportunities for concise wording.
argument-hint: "[guidance text or path/to/file.md]"
disable-model-invocation: true
---

Resolve `guidance_corpus` as follows:

1. If `$ARGUMENTS` identifies an existing, readable file, use its contents and the contents of readable local references that are clearly part of the same guidance set. Do not follow external links or revisit files. Note any applicable local references that cannot be accessed.
2. Otherwise, treat `$ARGUMENTS` as the guidance text.

Review `guidance_corpus` for:

- contradictions or incompatible instructions;
- ambiguous, confusing, or underspecified guidance;
- unnecessary duplication;
- information apparently missing for the guidance's stated purpose; and
- wording that can be shortened without changing the intended meaning.

Report findings by category. For each finding, identify the relevant text or location, explain the issue briefly, and suggest a correction when useful. Distinguish definite issues from possible omissions that depend on unstated context.

Keep the report concise. If no material issues are found, state that explicitly.