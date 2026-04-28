# Research Summary

Targeted research was performed with official or authoritative sources before finalizing recommendations. Sources below support the PRD implementation and testing decisions.

## Audit logging and security controls

1. **NIST SP 800-92: Guide to Computer Security Log Management**
   - Source: https://csrc.nist.gov/pubs/sp/800/92/final
   - Date/version context: Published September 2006.
   - Findings: NIST describes the need for sound log management infrastructure and robust log management processes across an enterprise.
   - Supports decisions: Treat audit-event write reliability, retention, review workflows, and operational handling as first-class requirements rather than incidental application logs.

2. **NIST SP 800-53 Rev. 5 / Audit and Accountability controls**
   - Source: https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final
   - Date/version context: September 2020 with updates; page notes later control catalog release updates.
   - Findings: Audit and Accountability controls cover event selection, event content, review, retention, protection, and system time synchronization.
   - Supports decisions: Define explicit event taxonomy, protect logs from tampering, restrict log access, retain records for a justified period, and use consistent timestamps.

3. **OWASP Logging Cheat Sheet**
   - Source: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
   - Date/version context: Living OWASP Cheat Sheet Series guidance.
   - Findings: Application logging should capture security and audit-trail events, support compliance and investigations, avoid sensitive data, protect logs from tampering, and verify logging behavior.
   - Supports decisions: Include role/billing/SSO changes and data exports, redact secrets, test log injection and authorization, and separate compliance audit data from generic operational logging.

## Event schema, actor semantics, filtering, and export

4. **AWS CloudTrail event record contents**
   - Source: https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html
   - Date/version context: Current CloudTrail event format shown as 1.11.
   - Findings: Event records include fields that help determine requested action, when and where it was made, UTC event time, event version, request context, and response details.
   - Supports decisions: Include UTC occurred-at time, action/category, request context, source IP/user agent where available, result, and version-compatible structured fields.

5. **AWS CloudTrail user identity reference**
   - Source: https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html
   - Findings: Audit records must represent different identity types, and usernames may not always be present.
   - Supports decisions: Model actor type and delegated/service/app/system actors, not only a human username.

6. **Microsoft Graph directoryAudit**
   - Source: https://learn.microsoft.com/en-us/graph/api/resources/directoryaudit?view=graph-rest-1.0
   - Date/version context: Microsoft Graph REST API v1.0.
   - Findings: Directory audit items include UTC activityDateTime, activityDisplayName, category, correlationId, id, initiatedBy user/app, loggedByService, operationType, result, resultReason, targetResources, and additionalDetails.
   - Supports decisions: Include actor/initiator, category, operation type, target resources, result, reason, correlation ID, and UTC timestamps.

7. **Okta System Log query guide**
   - Source: https://developer.okta.com/docs/reference/system-log-query/
   - Findings: Okta provides near-real-time, read-only system log access for org events, security/compliance, troubleshooting, and incident investigation; event types and expression filters are central to querying.
   - Supports decisions: Provide structured filters by event type/category, actor, target, result, and time range; keep the audit log read-only to admins.

8. **GitHub organization audit log documentation**
   - Source: https://docs.github.com/en/enterprise-cloud@latest/organizations/keeping-your-organization-secure/reviewing-the-audit-log-for-your-organization
   - Date/version context: GitHub Enterprise Cloud latest docs.
   - Findings: Organization audit logs show who performed an action, what action was performed, when it occurred, affected users/resources, SAML SSO and SCIM identity details, and support search/export workflows; GitHub documents 180-day visibility for org audit events in the UI.
   - Supports decisions: Provide actor/action/time/affected-target details, SSO/SCIM context, owner-level access controls, search filters, and CSV/JSON export.

9. **AWS CloudTrail event history**
   - Source: https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html
   - Findings: CloudTrail event history supports searching, viewing, and downloading event records for compliance/investigation workflows.
   - Supports decisions: Export should preserve filters, stable IDs, and structured fields; retention should be explicit because vendor defaults vary.

## Privacy, minimization, retention, and sensitive billing/SSO data

10. **ICO data minimisation guidance**
    - Source: https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/data-minimisation/
    - Findings: Personal data should be adequate, relevant, and limited to what is necessary for the specified purpose; organizations should only collect what they need and periodically delete what they do not need.
    - Supports decisions: Use allowlisted audit fields, redact unnecessary personal data, and document the compliance/accountability purpose.

11. **ICO storage limitation guidance**
    - Source: https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/storage-limitation/
    - Findings: Personal data should not be kept longer than needed; organizations should justify retention periods, define standard retention policies, and erase or anonymize data when no longer needed.
    - Supports decisions: Use a finite 365-day default retention, document exceptions, and test automated purge/anonymization behavior.

12. **Stripe API event and request ID documentation**
    - Sources: https://docs.stripe.com/api/events/object and https://docs.stripe.com/api/request_ids
    - Findings: Billing systems expose event IDs and request IDs for traceability, but sensitive payment details require careful handling.
    - Supports decisions: Include provider event IDs/request IDs where applicable, but store only safe billing metadata and redacted summaries.

## Accessibility and admin UI behavior

13. **WCAG 2.2**
    - Source: https://www.w3.org/TR/WCAG22/
    - Date/version context: W3C Recommendation; W3C advises using the most current WCAG version for future applicability.
    - Findings: WCAG success criteria are testable, technology-independent accessibility requirements.
    - Supports decisions: Require keyboard-operable controls, perceivable error states, accessible names/roles/values, focus visibility, and robust status messages.

14. **WAI Tables Tutorial**
    - Source: https://www.w3.org/WAI/tutorials/tables/
    - Findings: Accessible data tables need markup that identifies header cells and data cells and defines their relationships; complex tables may need scope, id, or headers associations.
    - Supports decisions: The audit log should be implemented as a semantic table or equivalent accessible data grid with clear header relationships.

15. **WCAG Status Messages understanding document**
    - Source: https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html
    - Findings: Status messages should be programmatically determinable so assistive technologies can present them without moving focus.
    - Supports decisions: Loading, no-results, export-ready, validation, and backend-failure states should be announced without disrupting the admin's workflow.

## Decisions supported by research

- Require structured audit events with actor, target, action, result, timestamp, source context, and correlation identifiers.
- Distinguish human, app, service, system, delegated, and affected-user semantics.
- Make log access read-only/append-only from product surfaces and record access/export events.
- Use structured filters and CSV/JSON export for compliance review.
- Redact secrets and minimize personal data.
- Define a finite retention period with purge/legal exception behavior.
- Test logging failure, authorization, redaction, filtering, export consistency, retention, immutability, and accessibility.
- Make the UI accessible for tables, filters, dialogs, errors, status messages, and keyboard workflows.
