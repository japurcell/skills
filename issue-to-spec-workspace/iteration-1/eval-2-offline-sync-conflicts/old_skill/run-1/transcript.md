# Eval Transcript: issue-to-spec (old_skill)

- Date: 2026-03-26
- Eval: eval-2-offline-sync-conflicts
- Prompt: "Use issue-to-spec on acme/mobile issue #233: 'Offline draft sync conflicts overwrite newer edits'. There are 7 comments with contradictory suggestions; produce a clean spec handoff and clearly flag any unresolved high-impact ambiguity."

## Steps

1. Read skill instructions from:
   - /home/adam/.agents/skills/issue-to-spec-workspace/skill-snapshot-SKILL.md

2. Snapshot workflow step 1: attempted to read GitHub issue and comments using gh-cli:
   - Command: `gh issue view 233 -R acme/mobile --comments --json number,title,body,labels,assignees,milestone,state,comments,author`
   - Exit code: 1
   - stderr/stdout: `GraphQL: Could not resolve to a Repository with the name 'acme/mobile'. (repository)`

3. Snapshot workflow step 2 (call create-spec) was not reachable:
   - Required issue payload (body + 7 comments) was unavailable due retrieval failure.
   - Therefore no spec/checklist artifacts were produced.

4. Wrote eval artifacts:
   - old_skill/outputs/final_response.md
   - old_skill/transcript.md
   - old_skill/outputs/metrics.json

## Result

Baseline run completed in failure-handling mode due to GitHub repository resolution failure before spec generation.