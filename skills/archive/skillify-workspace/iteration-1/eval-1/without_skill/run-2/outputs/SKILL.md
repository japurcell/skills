# doc-to-sop

Turn a confirmed documentation workflow into a concise, reusable SOP skill for a specific audience.

## Invocation

`/doc-to-sop $source_doc $audience`

## Arguments

- `$source_doc`: Path to the source document or notes file.
- `$audience`: The intended audience for the SOP, such as support, onboarding, or engineering.

## Use This When

- You have a source document that describes a repeatable process.
- You need to extract the stable workflow and rewrite it as a reusable SOP.
- You want the output tailored to a specific audience without adding unrelated tooling steps.

## Inputs

- The source document content.
- The intended audience.

## Output

Produce a reusable SOP skill draft that:

- Captures the repeatable workflow from the source material.
- States the inputs, outputs, and decision points clearly.
- Stays focused on reading, extracting, and writing.
- Avoids shell commands, package installation steps, or automation unless they are explicitly present in the source material.
- Keeps the workflow concise and easy to reuse across repositories.

## Workflow

1. Read the source document carefully.
2. Extract the repeatable workflow, required inputs, expected outputs, and decision points.
3. Remove repo-specific or one-off details unless they are essential to the workflow.
4. Rewrite the workflow as a concise SOP for the specified audience.
5. Add examples or edge-case notes only if they materially improve correct reuse.
6. Present the finished SOP skill content and include the recommended save path and invocation command.

## Quality Bar

- The result should be reusable across repositories.
- The argument list should stay limited to `$source_doc` and `$audience` unless the source material proves more are required.
- The wording should be easy to tweak before saving.
- The final output should make clear where to save the skill and how to invoke it.

## Final Response Format

Provide:

1. The completed skill content.
2. The recommended save path: `~/.agents/skills/doc-to-sop/SKILL.md`
3. The invocation command: `/doc-to-sop $source_doc $audience`
4. Any assumptions you made while translating the source document into the SOP.
