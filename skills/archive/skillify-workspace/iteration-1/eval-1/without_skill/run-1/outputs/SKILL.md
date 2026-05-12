# doc-to-sop

Create a reusable SOP-style skill from an existing source document or notes file.

## Use When

Use this skill when you have a document that captures a repeated workflow and you want to convert it into a concise, reusable skill for a specific audience.

## Arguments

- `$source_doc`: Path to the source document or notes file.
- `$audience`: Intended audience for the SOP, such as support, onboarding, or engineering.

## Inputs

You will receive:

- A source document to read.
- The target audience.

## Goal

Produce a short, reusable SOP skill that:

- Preserves the real workflow from the source material.
- Clearly states inputs, outputs, and decision points.
- Stays focused on reading, extracting, and writing.
- Avoids adding shell commands, package installation steps, or automation unless the source material explicitly requires them.

## Instructions

1. Read the source document carefully.
2. Extract the repeatable workflow, required inputs, expected outputs, and any key decision points.
3. Identify the minimum set of steps needed for the audience to follow the workflow reliably.
4. Draft a reusable skill in concise markdown.
5. Keep the argument list small and explicit.
6. Include examples or edge-case notes only when they materially improve correct use.
7. End with clear save and invocation guidance.

## Output Requirements

Return a complete `SKILL.md` draft that includes:

- The skill name.
- A short description of what the skill does.
- When to use it.
- The confirmed arguments.
- Step-by-step instructions.
- Success criteria or output expectations.
- A final note that tells the user where to save the skill and how to invoke it.

## Success Criteria

The result is successful when:

- The skill is reusable across repositories.
- The instructions remain concise and operational.
- The skill exposes exactly the confirmed arguments unless the source material requires more.
- The final output tells the user exactly where to save the skill and how to invoke it.

## Final Response Format

Provide:

1. The finished `SKILL.md` content.
2. A short note stating:
   - Save path: `~/.agents/skills/doc-to-sop/SKILL.md`
   - Invocation: `/doc-to-sop $source_doc $audience`
