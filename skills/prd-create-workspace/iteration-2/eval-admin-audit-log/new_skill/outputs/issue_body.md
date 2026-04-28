# PRD: Team admin audit log for role, billing, and SSO changes

## Objective

Build a team admin audit log for organization owners and authorized compliance reviewers so they can review who changed user roles, billing settings, and SSO configuration, understand what changed and when, and export evidence for compliance review without exposing secrets or requiring full administrative access. Success means every in-scope privileged change is recorded with enough context to reconstruct the change, the log is searchable and exportable for authorized viewers, sensitive values stay redacted, and the experience is accessible and behaviorally well-tested.

## User Stories

1. As an organization owner, I want to see role changes in one audit log, so that I can confirm who granted or removed privileged access.
2. As a compliance reviewer, I want read-only access to the audit log, so that I can perform reviews without receiving full admin permissions.
3. As a billing administrator with audit permissions, I want to review billing-setting changes, so that I can confirm account and payment-related settings changed as expected.
4. As a security administrator, I want to review SSO configuration changes, so that I can verify identity settings were changed intentionally.
5. As an authorized reviewer, I want each entry to show the actor, target, timestamp, action, and outcome, so that I can quickly understand what happened.
6. As an authorized reviewer, I want field-level before/after summaries for changed settings, so that I can assess impact without opening raw configuration payloads.
7. As an authorized reviewer, I want sensitive values such as secrets, tokens, keys, and payment details to be redacted, so that the audit log does not become a secondary source of sensitive data exposure.
8. As an authorized reviewer, I want to see both successful and denied attempts for in-scope privileged changes, so that compliance and security reviews can distinguish completed changes from blocked actions.
9. As an authorized reviewer, I want to filter the log by actor, target, event family, date range, and outcome, so that I can answer specific review questions quickly.
10. As an authorized reviewer, I want timestamps to be unambiguous across time zones, so that exported evidence and in-product review agree on event ordering.
11. As an authorized reviewer, I want to inspect request or correlation identifiers when available, so that I can reconcile an audit entry with other operational evidence.
12. As an authorized reviewer, I want to export the currently filtered result set, so that I can share evidence with auditors without manual transcription.
13. As an authorized reviewer, I want exported data to preserve the same redaction rules as the UI, so that exports remain safe to circulate internally.
14. As an authorized reviewer using assistive technology, I want the log table, filters, sorting, and validation states to be accessible, so that I can perform the same review workflow without barriers.
15. As an organization owner, I want unauthorized users to be denied access to the log and its exports, so that privileged operational history is not broadly exposed.
16. As an organization owner, I want audit entries to remain immutable once recorded, so that the log can be trusted during compliance review.
17. As an operator, I want in-scope admin changes initiated from any supported surface to appear in the same audit log, so that reviewers do not have to check separate systems for roles, billing, and SSO changes.
18. As an authorized reviewer, I want clear empty, loading, and error states, so that I know whether no events matched my filters or the system failed to retrieve data.
19. As an organization owner, I want at least one year of searchable audit history in product, so that routine compliance reviews do not depend on short vendor-style default retention windows.
20. As a future product team, I want the event model to tolerate new event types without redesigning the entire viewer, so that the audit log can expand safely beyond the initial MVP.

## Implementation Decisions

- Treat role changes, billing-setting changes, and SSO-configuration changes as separate first-class audit event families, and include denied attempts for those same families. Citation: OWASP Logging Cheat Sheet, https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html ; GitHub audit-log event catalogs, https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/audit-log-events-for-your-organization . Reason: administrative actions, privilege changes, and configuration changes are explicitly audit-worthy and should be queryable by category.
- Record a structured event schema that includes actor, target resource, action family, outcome, timestamp, request or correlation identifier when available, source IP/client context when available, and field-level old/new value summaries for the changed setting. Citation: OWASP Logging Cheat Sheet, https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html ; Microsoft Entra audit logs, https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-audit-logs . Reason: reviewers need enough context to reconstruct what changed, by whom, and under which request flow.
- Represent sensitive diffs using masked or derived values rather than raw payloads, and never expose tokens, secrets, keys, or payment data in the audit log UI or exports. Citation: OWASP Logging Cheat Sheet, https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html ; ICO data minimisation guidance, https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/data-minimisation/ . Reason: compliance review requires detail, but the log must not become a secondary leak of highly sensitive configuration data.
- Restrict audit-log access to organization owners and a dedicated read-only audit/compliance reviewer role, and apply the same authorization boundary to exports. Citation: Microsoft Entra least-privileged log access guidance, https://learn.microsoft.com/en-us/entra/identity/monitoring-health/howto-customize-filter-logs ; Atlassian audit-log access guidance, https://support.atlassian.com/security-and-access-policies/docs/accessing-audit-log-activities/ . Reason: least-privilege access supports compliance review without granting full admin powers.
- Provide structured filters for actor, target, event family, date range, and outcome, and allow authorized viewers to export the currently filtered result set in a portable format. Citation: GitHub audit-log search and export guidance, https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/searching-the-audit-log-for-your-enterprise and https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/exporting-audit-log-activity-for-your-enterprise ; Okta System Log filters, https://help.okta.com/en-us/content/topics/reports/syslog-filters.htm . Reason: compliance reviewers need reproducible, portable evidence rather than manual screen-by-screen review.
- Store and export timestamps in a timezone-safe format with explicit offset, while allowing localized display in the product UI. Citation: RFC 3339, https://www.rfc-editor.org/rfc/rfc3339 . Reason: audit evidence must remain sortable, comparable, and unambiguous across systems and reviewers.
- Treat audit records as immutable once written and commit to at least one year of searchable in-product retention, with exportable records available for longer-term archival outside this MVP when required. Citation: NIST SP 800-92, https://csrc.nist.gov/pubs/sp/800/92/final ; Microsoft Entra audit logs, https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-audit-logs ; Azure retention guidance, https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-retention-archive . Reason: retention promises must be explicit because vendor defaults vary widely and compliance review depends on trust in the record.
- Render the audit log as an accessible tabular review experience with explicit filter labels, clear validation and error messaging, and keyboard/screen-reader support for sorting and navigation. Citation: WAI Tables Tutorial, https://www.w3.org/WAI/tutorials/tables/ ; WAI Forms guidance, https://www.w3.org/WAI/tutorials/forms/labels/ and https://www.w3.org/WAI/tutorials/forms/notifications/ ; WCAG 2.2 Error Identification, https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html . Reason: compliance review is a core workflow and must remain usable for assistive-technology users.
- Design the event model so new admin-change event types can be added without breaking the viewer, filters, or exports. Citation: Microsoft Entra audit activity reference, https://learn.microsoft.com/en-us/entra/identity/monitoring-health/reference-audit-activities ; Okta event-type catalog, https://developer.okta.com/docs/reference/api/event-types/ . Reason: admin event catalogs evolve over time, so the MVP should not assume the initial three families are the permanent boundary.

## Testing Decisions

- Good tests should verify external behavior and user-visible outcomes rather than implementation details. Prior art: Existing codebase testing pattern favors behavior-first verification for user-visible outcomes. Reason: audit-log quality depends on what authorized reviewers can observe and export, not on internal storage details.
- Verify that each in-scope mutation path produces exactly one visible audit entry with the expected actor, target, action family, outcome, timestamp, and change summary. Prior art: OWASP Logging Cheat Sheet, https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html . Reason: the core behavior is trustworthy capture of privileged changes.
- Verify that unauthorized users cannot access the audit log or exports, while organization owners and audit/compliance reviewers can. Prior art: Microsoft Entra least-privileged log access guidance, https://learn.microsoft.com/en-us/entra/identity/monitoring-health/howto-customize-filter-logs . Reason: authorization is a first-order correctness and security requirement.
- Verify that sensitive values remain redacted in list view, detail view, and exported output for billing and SSO changes. Prior art: OWASP Logging Cheat Sheet, https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html . Reason: redaction failures would turn the audit feature into a data-exposure risk.
- Verify that filter results, visible row counts, detail views, and exported datasets stay consistent for the same query. Prior art: GitHub audit-log search/export guidance, https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/exporting-audit-log-activity-for-your-enterprise . Reason: compliance reviewers need reproducible evidence, not conflicting representations of the same events.
- Verify accessible behavior for table semantics, filter labels, sort announcements, keyboard navigation, and validation/error messaging. Prior art: WAI Tables Tutorial, https://www.w3.org/WAI/tutorials/tables/ ; WCAG 2.2 Error Identification, https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html . Reason: audit review must remain complete and understandable for assistive-technology users.
- Verify retention and immutability behavior at the product boundary, including that records in scope remain queryable for the promised retention window and cannot be modified through normal product workflows. Prior art: NIST SP 800-92, https://csrc.nist.gov/pubs/sp/800/92/final ; Microsoft Entra audit logs, https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-audit-logs . Reason: compliance trust depends on the record remaining present and unaltered.

## Success Criteria

- Every successful and denied role, billing-setting, and SSO-configuration change from supported product surfaces appears in the audit log within the product’s normal event-processing window.
- Each audit entry exposes actor, target, action family, outcome, timestamp with timezone context, and a field-level change summary suitable for human review.
- Sensitive values remain redacted in the list view, detail view, and exported output.
- Authorized viewers can filter by actor, target, event family, date range, and outcome, and can export the filtered result set without losing redaction or field meaning.
- Organization owners and read-only audit/compliance reviewers can access the log; unauthorized users cannot.
- Searchable in-product audit history is available for at least one year for in-scope events.
- Audit records are immutable through normal product workflows.
- The audit-log screen, filters, sorting, and validation states are accessible to keyboard and assistive-technology users.
- Empty, loading, and error states clearly distinguish “no matching events” from retrieval failure.

## Out of Scope

- Real-time alerting, paging, or anomaly detection for privileged changes.
- A full SIEM replacement, cross-system forensics platform, or generalized security analytics product.
- Audit coverage for every read-only admin action or every end-user activity outside role, billing, and SSO change flows.
- Customer-configurable retention policies beyond the baseline retention promise in this PRD.
- Historical backfill for changes that were never previously captured by a trustworthy event source.
- Third-party streaming integrations, scheduled reports, or custom dashboards beyond filtered export.

## Further Notes

- This PRD is based on official research and explicit accepted assumptions because the available repository is a skills/evals repository, not the target product application.
- Accepted assumptions: authorized viewers are organization owners plus read-only audit/compliance reviewers; v1 captures successful and denied in-scope changes; sensitive values use masked field-level diffs; filtered export is in scope; searchable in-product retention is at least one year; real-time alerting is deferred.
- Before implementation starts, the product team should confirm the actual source systems for role changes, billing settings, and SSO configuration, and verify whether any existing event pipeline can supply the required actor, target, and before/after fields.
- If some source systems cannot provide full before/after values safely, the minimum acceptable fallback is to record the changed field names, actor, time, target, and outcome without exposing raw secrets.
