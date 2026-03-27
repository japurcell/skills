# Eval Transcript: issue-to-spec (with_skill)

- Date: 2026-03-26
- Eval: eval-2-offline-sync-conflicts
- Prompt: "Use issue-to-spec on acme/mobile issue #233: 'Offline draft sync conflicts overwrite newer edits'. There are 7 comments with contradictory suggestions; produce a clean spec handoff and clearly flag any unresolved high-impact ambiguity."

## Steps

1. Loaded skill instructions from:
   - /home/adam/.agents/skills/issue-to-spec/SKILL.md
2. Validated inputs from prompt:
   - repo: acme/mobile
   - github_issue: 233
3. Ran issue retrieval command:
   - command: gh issue view 233 -R acme/mobile --json number,title,body,labels,assignees,milestone,state,comments
   - exit code: 1
   - error: GraphQL: Could not resolve to a Repository with the name 'acme/mobile'. (repository)
4. Applied skill failure handling:
   - Stopped workflow at retrieval step.
   - Did not run create-spec.
5. Wrote required artifacts:
   - with_skill/outputs/final_response.md
   - with_skill/transcript.md
   - with_skill/outputs/metrics.json

## Result

Run completed via the gh-access failure path defined by the skill.
