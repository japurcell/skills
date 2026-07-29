# Browser verification

Use this file only when the selected task mentions or implies browser-visible behavior.

## Required when

Browser verification is required if the task title, description, acceptance criteria, design guidance, likely files, or notes mention or imply:

- Playwright or `playwright-cli`
- browser behavior
- UI-visible behavior
- auth flows
- routing/navigation
- rendering
- DOM-visible changes
- client-side interaction
- interactive validation

For UI, auth, or routing work, require browser verification unless the PRD explicitly says otherwise.

## Tool

Use one of:

- `playwright-cli` directly
- a repo command that explicitly runs `playwright-cli`

Do not accept unexecuted browser checks.

## Evidence

Record:

- exact command
- pass/fail result
- concise relevant output

Example:

```text
Browser verification:
  Required: yes
  Evidence: npx playwright-cli test tests/auth.spec.ts
  Result: PASS login redirects to dashboard
```

## Gate

If browser verification is required:

- Do not set `passes: true` unless Playwright evidence passed.
- If Playwright is unavailable, failing, not installed, cannot reach the app, or cannot complete the check, the task is blocked.
- Do not commit blocked work.
- Record the blocker in `progress_file`.
