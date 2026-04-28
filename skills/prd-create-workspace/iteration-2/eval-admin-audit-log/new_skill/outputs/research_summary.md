# Research Summary

Accessed: 2026-04-28

## Standards and security guidance

### 1. Audit the in-scope admin changes explicitly
- Privilege changes, administrative actions, and configuration changes are audit-worthy security events.
- This supports making **role changes**, **billing-setting changes**, and **SSO-configuration changes** first-class event families in the PRD.
- Sources:
  - OWASP Logging Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
  - Microsoft Entra audit activity reference — https://learn.microsoft.com/en-us/entra/identity/monitoring-health/reference-audit-activities
  - GitHub organization audit log events — https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/audit-log-events-for-your-organization

### 2. Capture enough context to reconstruct who changed what
- Official guidance consistently points to recording when, where, who, and what changed, plus correlation identifiers and before/after values where available.
- This supports event fields for actor, target, timestamp, action, outcome, request/correlation ID, source IP/client, and field-level old/new values.
- Sources:
  - OWASP Logging Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
  - Microsoft Entra audit logs — https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-audit-logs
  - AWS CloudTrail event record contents (event format 1.11) — https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html

### 3. Redact secrets and sensitive values
- Audit logs should not expose raw secrets, tokens, or other sensitive payloads.
- This supports masked diffs for billing and SSO settings, with changed field names shown but secret values omitted.
- Sources:
  - OWASP Logging Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
  - ICO UK GDPR data minimisation guidance — https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/data-minimisation/
  - Google Cloud audit logging best practices — https://cloud.google.com/logging/docs/audit/best-practices

### 4. Make retention and immutability explicit
- Official guidance and vendor precedents show that default retention windows vary widely, so the product must state its own retention promise.
- This supports an explicit PRD decision for immutable audit records, minimum searchable retention, and export/archive support.
- Sources:
  - NIST SP 800-92 — https://csrc.nist.gov/pubs/sp/800/92/final
  - Microsoft Entra audit logs (entries are system-generated and not user-editable) — https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-audit-logs
  - Azure Monitor retention guidance — https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-retention-archive
  - Okta System Log retention/filter guidance — https://help.okta.com/en-us/content/topics/reports/syslog-filters.htm

## Reviewer workflow and product precedents

### 5. Filtering must be structured
- Official audit-log products emphasize structured filters such as actor, action, date range, target, IP/source, and outcome.
- This supports a filter-first reviewer workflow instead of relying on free-text search alone.
- Sources:
  - GitHub audit-log search qualifiers — https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/searching-the-audit-log-for-your-enterprise
  - Microsoft Entra log filtering — https://learn.microsoft.com/en-us/entra/identity/monitoring-health/howto-customize-filter-logs
  - Okta System Log filters — https://help.okta.com/en-us/content/topics/reports/syslog-filters.htm

### 6. Export is part of compliance review
- Vendor products support CSV/JSON export or API access because reviewers often need portable evidence outside the application.
- This supports including filtered export in scope for v1.
- Sources:
  - GitHub audit-log export — https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/exporting-audit-log-activity-for-your-enterprise
  - Okta System Log query/reference — https://developer.okta.com/docs/reference/system-log-query/

### 7. Access should follow least privilege
- Official admin-log systems distinguish read-only reviewer access from full administrative control.
- This supports a dedicated audit/compliance viewer role rather than granting all admins full access by default.
- Sources:
  - Microsoft Entra least-privileged log access (Reports Reader) — https://learn.microsoft.com/en-us/entra/identity/monitoring-health/howto-customize-filter-logs
  - Atlassian audit-log access guidance — https://support.atlassian.com/security-and-access-policies/docs/accessing-audit-log-activities/

## Accessibility and usability guidance

### 8. Use accessible table patterns and explicit filter validation
- W3C guidance favors semantic tables for tabular data, explicit labels for filters, and clear error identification/notifications.
- This supports an accessible audit-log table, keyboard-friendly filters, and user-visible validation states.
- Sources:
  - WAI Tables Tutorial — https://www.w3.org/WAI/tutorials/tables/
  - WAI Forms: Labels — https://www.w3.org/WAI/tutorials/forms/labels/
  - WAI Forms: Instructions — https://www.w3.org/WAI/tutorials/forms/instructions/
  - WAI Forms: Notifications — https://www.w3.org/WAI/tutorials/forms/notifications/
  - WCAG 2.2 Error Identification — https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html

### 9. Use timezone-safe timestamps
- Audit logs need timestamps that are sortable, exportable, and unambiguous across reviewers and systems.
- This supports storing/exporting timestamps in RFC 3339 format with explicit timezone context.
- Source:
  - RFC 3339 — https://www.rfc-editor.org/rfc/rfc3339

## Research-driven recommendations carried into the PRD

- Cover successful and denied changes for roles, billing settings, and SSO configuration.
- Record actor, target, action, outcome, time, request/correlation ID, and field-level before/after summaries.
- Redact secrets and highly sensitive values in UI and exports.
- Provide structured filters and filtered export for compliance review.
- Restrict access with a read-only audit-review role.
- Define explicit retention and immutability requirements instead of relying on vendor defaults.
