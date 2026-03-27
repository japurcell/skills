# Eval Transcript: issue-to-spec (with_skill)

- Date: 2026-03-26
- Eval: eval-2-offline-sync-conflicts
- Prompt: "Use issue-to-spec on acme/mobile issue #233: 'Offline draft sync conflicts overwrite newer edits'. There are 7 comments with contradictory suggestions; produce a clean spec handoff and clearly flag any unresolved high-impact ambiguity."

## Steps

1. Read skill instructions from:
   - /home/adam/.agents/skills/issue-to-spec/SKILL.md

2. Ran GitHub issue retrieval command required by the skill:
   - Command: gh issue view 233 -R acme/mobile --json number,title,body,labels,assignees,milestone,state,comments
   - Exit code: 1
   - stderr/stdout: GraphQL: Could not resolve to a Repository with the name 'acme/mobile'. (repository)

3. Applied failure handling from skill:
   - Since gh could not access the repository/issue, stopped workflow at retrieval step.
   - Did not invoke create-spec.

4. Wrote eval artifacts:
   - with_skill/outputs/final_response.md
   - with_skill/transcript.md
   - with_skill/outputs/metrics.json

## Result

Run completed in failure-handling mode due to GitHub access/repository resolution failure.
