# Browser verification

Use only when the selected task mentions or implies browser-visible behavior.

## Required when mentioned or implied

Browser verification is required if task title, description, acceptance criteria, design guidance, likely files, or notes mention or imply:

- Playwright or `playwright-cli`
- browser, UI, rendering, DOM, or client-side behavior
- auth flows
- routing/navigation
- interactive validation

For UI, auth, or routing work, require browser verification unless the PRD explicitly says otherwise.

## Accepted tools

Use one of:

- `playwright-cli` directly
- a repo command that explicitly runs `playwright-cli`

Do not accept unexecuted browser checks.

## Evidence to record

Record in `progress_file`:

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
- If Playwright is unavailable, failing, not installed, cannot reach the app, or cannot complete the check, block.
- Do not commit blocked work.
- Record the blocker and any browser command/tool failure or timeout in `progress_file`.
