---
name: guidance-review
description: Review agent guidance for contradictions, ambiguity, missing steps, and misleading examples. Use when asked to review instructions or when creating or editing skills, AGENTS.md, CLAUDE.md, copilot-instructions.md, GEMINI.md, or brain principles.
argument-hint: "[guidance text or path/to/file.md]"
---

Resolve `guidance_corpus` as follows:

1. If `$ARGUMENTS` identifies an existing, readable file, read it and relevant local references. Keep the review local. Avoid recursive discovery and redundant reads. Note any inaccessible reference that limits a finding.
2. Otherwise, treat `$ARGUMENTS` as the guidance text.

Review `guidance_corpus` for:

- contradictions or incompatible instructions;
- ambiguous, confusing, or underspecified guidance;
- misleading or incorrect examples;
- information missing for the guidance's stated purpose.

Trace what a reader following the instructions literally would do:

- For repetitive or wordy passages, identify the decision a deletion or shorter phrasing would change. If none changes, recommend the cut. If uncertain, name the smallest case that distinguishes the two versions.
- At each decision, identify the evidence the reader has and what only becomes observable after acting. Check whether the guidance distinguishes descriptive examples from enforced restrictions.
- Walk examples in order. Track what each step changes and whether the required proof is still observable when collected. For prose examples, compare each claim with the evidence supplied.
- When guidance describes a local CLI, schema, template, or evaluation, compare a representative case with the relevant source. Trace a boundary case when it could change the finding.

Order findings by consequence and label each with its category. Give the location, the concrete consequence for the reader, and the smallest correction that preserves the intended behavior. Distinguish definite issues from possible omissions that depend on unstated context.

Keep the report concise. If no material issues are found, state that explicitly.
