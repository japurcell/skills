# Confirmed Session Summary: doc-to-sop

## What Happened

- The user wanted to turn a repeated documentation workflow into a reusable skill that works across repositories.
- In the source session, the agent repeatedly converted long internal docs into short standard operating procedure skills for teammates.
- The work ended when a reusable skill file was drafted and the user had a clean invocation example.

## Confirmed Answers

- Confirmed skill name: `doc-to-sop`
- Confirmed save location: `~/.agents/skills/doc-to-sop/SKILL.md`
- Confirmed invocation style: `/doc-to-sop $source_doc $audience`
- Confirmed arguments:
  - `$source_doc`: path to the source document or notes file
  - `$audience`: who the SOP is for, such as support, onboarding, or engineering
- Confirmed context choice: inline is fine because the user likes to tweak wording before saving

## Inputs And Success Criteria

- Inputs: a source document and intended audience
- Success artifact: a saved personal skill plus concise invocation instructions
- Hard success criteria:
  - The skill can be reused across repositories
  - The instructions stay focused on reading, extracting, and writing rather than shell automation
  - The resulting skill exposes the two confirmed arguments
  - The final output tells the user exactly where to save it and how to invoke it

## Observed Workflow Steps

1. Read the source notes or document.
2. Extract the repeatable workflow, inputs, outputs, and decision points.
3. Draft a skill with clear steps and success criteria.
4. Check whether the workflow needs examples or extra edge-case notes.
5. Present the final SKILL.md and tell the user the save path plus invocation command.

## User Corrections And Preferences

- The user said this workflow should follow them across repos, so it belongs in personal skills rather than a repo folder.
- The user did not want shell or package-install steps added unless the source workflow actually used them.
- The user wanted the argument list to stay small and obvious.

## Tools And Agents Used

- `Read`
- `Grep`
- `Glob`
- `Edit`
- `Write`
- No shell tools were used.
