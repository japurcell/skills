- Scenario assumptions used:
  - checklists/ exists for feature-auth
  - ux.md is fully complete
  - test.md has 3 incomplete checklist items

- Checklist gate behavior applied from implement-plan skill:
  - Because at least one checklist has incomplete items, overall status is FAIL.
  - The command must STOP after showing the status table and ask:
    "Some checklists are incomplete. Do you want to proceed with implementation anyway? (yes/no)"
  - It then waits for user input.

- What happens next after the prompt:
  - If user replies "no", "wait", or "stop": halt execution.
  - If user replies "yes", "proceed", or "continue": continue to step 2 and load implementation context (tasks.md, plan.md, and optional spec artifacts).
