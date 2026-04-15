---
name: doc-to-sop
description: Turn a source document or notes file into a concise, reusable SOP-style skill for a specific audience by extracting the repeatable workflow, inputs, outputs, and guardrails.
---

# doc-to-sop

Use this skill when you need to turn an internal document, notes file, or session summary into a reusable SOP-style skill for a specific audience such as support, onboarding, or engineering.

## Arguments

- `$source_doc`: Path to the source document or notes file.
- `$audience`: Intended audience for the SOP, such as support, onboarding, or engineering.

## Inputs

- The source document at `$source_doc`.
- The intended audience described by `$audience`.

## Success Criteria

- The resulting skill is reusable across repositories.
- The instructions stay focused on reading, extracting, and writing rather than shell automation.
- The resulting skill exposes the two confirmed arguments and no unnecessary extras.
- The final response tells the user where to save the generated skill and how to invoke it.

## Workflow

1. Read `$source_doc` closely.
2. Extract the repeatable workflow, required inputs, expected outputs, decision points, and constraints.
3. Adapt the wording and emphasis for `$audience` without changing the underlying process.
4. Reduce the workflow to the smallest stable set of steps that can be reused across repositories.
5. Draft a complete `SKILL.md` for the derived SOP skill.
6. Keep the instructions concrete and focused on the real workflow. Do not add shell commands, package installation steps, or environment setup unless the source material explicitly depends on them.
7. Keep the argument list small and obvious. Prefer only the inputs that are clearly necessary.
8. If the source leaves minor gaps, make conservative assumptions and state them explicitly instead of inventing extra process.
9. Present the result inline so the user can tweak wording before saving.

## Output Format

Return the following in one response:

1. A ready-to-save `SKILL.md` for the derived SOP skill.
2. A short note that states:
   - the recommended save path for the generated skill,
   - the invocation command,
   - any assumptions made while drafting.

## Style Rules

- Write for `$audience`.
- Prefer short sections and direct instructions.
- Preserve real decision points from the source material.
- Avoid repository-specific references unless the source material requires them.
- Do not add extra tooling, automation, or ceremony.
