# Interview Log

No live questions were asked because this is an offline benchmark run. The following are questions I would normally ask, followed by assumptions used to proceed.

## Questions I Would Ask
1. Which product tiers and admin roles should have access to the audit log?
2. What retention period is required for compliance review?
3. Should billing audit events be visible to all team admins or only billing owners?
4. Which exact billing settings are in scope for the first release?
5. Which SSO protocols and related settings are supported today, such as SAML, OIDC, SCIM, domain verification, and group mappings?
6. Are failed administrative change attempts in scope, or only successful changes?
7. Is export required in CSV, JSON, both, or another compliance format?
8. Should audit log viewing/exporting itself generate an audit event?
9. Are there regional privacy restrictions or customer-specific data residency requirements?
10. Is historical backfill required for events before launch?

## Assumptions Made
- The initial release covers successful changes to user roles, billing settings, and SSO configuration.
- Authorized team admins can view non-billing audit events; billing details may require billing-owner permission if such a permission exists.
- Compliance reviewers need at least 1 year of retention unless legal requirements specify otherwise.
- Before/after values should be captured, but sensitive values must be redacted or summarized.
- CSV and JSON exports are acceptable compliance review formats.
- Historical backfill is out of scope for the first release.
- The PRD should be filed as a GitHub issue, but no real issue should be created during this eval.
