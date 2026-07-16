# Browser verification

Browser verification is mandatory when the selected task mentions or implies browser-visible behavior.

## Triggers

Require browser verification if the task title, description, acceptance criteria, design guidance, files likely touched, or related notes mention or imply:

- `playwright` or `playwright-cli`
- `browser`
- `interactive`
- `verify in browser`
- UI-visible behavior
- auth flow behavior
- routing or navigation
- page rendering
- client-side interaction
- visual or DOM-visible state changes

For UI, auth, or routing work, require browser verification by default unless the PRD explicitly says otherwise.

## Required tool

Use one of:

1. `playwright-cli` directly
2. an explicit `verify-interactive` step that runs `playwright-cli`

Do not accept “browser check listed but not executed.”

## Required evidence

Capture:

- exact command
- pass/fail result
- concise relevant output excerpt

Example:

```text
Browser verification:
  Required: yes
  Evidence: npx playwright-cli test tests/auth.spec.ts
  Result: PASS login redirects to dashboard
```

## Completion gate

If browser verification is required:

- Do not set `passes: true` unless Playwright evidence passed.
- If `playwright-cli` is unavailable, failing, not installed, cannot reach the app, or cannot complete the check, the task remains blocked/open.
- Do not commit blocked work.
- Record the blocker in `progress_file`.
