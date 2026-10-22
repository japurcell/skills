# FSDP Routing and Core Rules

Read this first. Then load the smallest set of references needed.

## Core rules

- Meet Section 508 and WCAG 2.2 AA.
- Build accessibility into the design from the start.
- Use user research, approved mockups, product-owner input, subject-matter input, and compliance needs to guide decisions.
- Do not make arbitrary visual or layout changes after UX approval.
- Developer review should improve feasibility, not bypass approved user-centered decisions.
- Prefer FSDP and USWDS patterns before inventing new ones.
- When public-facing branding deviates from FSDP, flag approval need.

## Surface routing

Load exactly one:

- Public web/app: `references/surface-public-web.md`
- Internal web/app: `references/surface-internal-web.md`
- Non-web artifact: `references/surface-non-web.md`

If a task spans multiple surfaces, handle each separately.

## Concern routing

Load only what applies:

- Brand, color, type, spacing, icons, imagery, hierarchy: `references/visual-foundations.md`
- Forms, buttons, validation, dialogs, alerts, snackbars, uploads, progress: `references/forms-actions-feedback.md`
- Header, footer, banner, navigation, search, tabs, accordion, cards, collections, tables, charts, tags, badges: `references/navigation-content-data.md`

## Universal accessibility checks

- Clear page or artifact title.
- Logical reading and heading order.
- Meaning does not rely on color alone.
- Adequate contrast.
- Descriptive labels and link text.
- Keyboard access and visible focus for interactive web controls.
- Plain-language feedback for errors, status, and destructive actions.
