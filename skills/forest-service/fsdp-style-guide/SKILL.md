---
name: fsdp-style-guide
description: Mandatory for all UI/UX design, implementation, review, audit, or visual regression tasks. Always use for any work that affects user-facing appearance, behavior, accessibility, branding, layout, navigation, forms, dialogs, alerts, tables, or visual design.
---

# FSDP Guidelines

Apply Forest Service Digital Playbook standards to designs, reviews, mockups, documents, slides, and interfaces.

## Load order

1. Read `references/fsdp-ux-guidelines.md`.
2. Load exactly one surface reference:
   - Public web/app: `references/surface-public-web.md`
   - Internal web/app: `references/surface-internal-web.md`
   - Non-web artifact: `references/surface-non-web.md`
3. Load only needed concern references:
   - Visual/brand: `references/visual-foundations.md`
   - Forms/actions/feedback: `references/forms-actions-feedback.md`
   - Navigation/content/data: `references/navigation-content-data.md`

Do not load all references by default.

## Workflow

1. Classify the surface and ask if unclear.
2. Identify non-negotiables: accessibility, brand, approvals, hierarchy, behavior.
3. Prefer FSDP and USWDS patterns over custom patterns.
4. Preserve approved UX decisions unless requirements, accessibility, or compliance require change.
5. If guidance conflicts, use this order:
   1. Law/accessibility/compliance
   2. Surface-specific reference
   3. Concern reference
   4. General design advice
6. For non-web artifacts, translate FSDP intent instead of copying web-only mechanics.

## Response format

- **Surface:** public web, internal web, or non-web
- **Non-negotiables:** must-follow rules
- **Recommendations:** practical design moves
- **Risks/approvals:** compliance, accessibility, or Communications issues
- **Open issues:** unresolved FSDP mismatches or assumptions

## Red flags

- Public branding, header, logo order, or footer changes without approval.
- Accessibility postponed until after design.
- Missing labels, headings, focus states, or confirmations.
- Important meaning shown by color or icon alone.
- Custom behavior replacing standard FSDP/USWDS behavior without a reason.
- Web-only rules copied into slides, documents, or mockups where they do not fit.
