Need exact stop response from skill file. Reading skill + fixture, then write `outputs/decision.md`.
Need exact local rules paths, then write stop response per skill.
Writing required stop response to `outputs/decision.md`.
Verifying written output matches required dry-run stop shape.
1. State that review-fix iteration limit is reached.
2. Do not fix directly.
3. Do not dispatch another review-fix implementer.
4. Reread `prd_file`.
5. Append stop-state entry to `progress_file`.
6. Human decision required: ask user to decide blocker.
