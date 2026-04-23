## Summary

## Workflow artifacts
- Work ID: `<work-id>`
- Intake: `.ai/artifacts/<work-id>/00-intake.md`
- Plan: `.ai/artifacts/<work-id>/05-plan.md`
- Task graph: `.ai/artifacts/<work-id>/06-task-graph.yaml`
- Reviews: `.ai/artifacts/<work-id>/08-code-review.md`, `.ai/artifacts/<work-id>/08-security-review.md`, `.ai/artifacts/<work-id>/08-tech-debt.md`
- Verification: `.ai/artifacts/<work-id>/09-verification.md`

## Issue hierarchy
- Parent issue: #
- Phase issues: #
- Task issues: #

## Verification
- [ ] Targeted tests/checks passed
- [ ] Security review completed
- [ ] Tech debt review completed
- [ ] Stop gates validated (`python3 .ai/scripts/validate-artifacts.py --work-id <work-id>`)
