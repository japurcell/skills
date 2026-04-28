# Research Summary

## Scope

Because the benchmark repository is not the target application, research focused on authoritative guidance for administrative audit logs rather than framework-specific implementation details.

## Primary sources consulted

### Security, logging, and tamper resistance

1. OWASP Logging Cheat Sheet  
   https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
2. Google Cloud Audit Logs overview  
   https://cloud.google.com/logging/docs/audit
3. Google Cloud audit logging best practices  
   https://cloud.google.com/logging/docs/audit/best-practices
4. Microsoft Entra audit logs concepts  
   https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-audit-logs
5. Microsoft Entra audit activities reference  
   https://learn.microsoft.com/en-us/entra/identity/monitoring-health/reference-audit-activities
6. RFC 5848 Signed Syslog Messages  
   https://www.rfc-editor.org/rfc/rfc5848
7. Okta System Log query guide  
   https://developer.okta.com/docs/reference/system-log-query/

### Compliance and access-control guidance

8. NIST SP 800-53 Rev. 5, AU-2 / AU-3 / AU-6 / AU-9 / AU-11  
   https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final
9. NIST SP 800-92 Guide to Computer Security Log Management  
   https://csrc.nist.gov/pubs/sp/800/92/final
10. NIST SP 800-63B / 800-63-4 digital identity guidance  
    https://pages.nist.gov/800-63-4/sp800-63b.html
11. GitHub Enterprise Cloud audit log export/API docs (supplemental product precedent)  
    https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/exporting-audit-log-activity-for-your-enterprise  
    https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/using-the-audit-log-api-for-your-enterprise

### Accessibility and UX

12. WAI Tables Tutorial  
    https://www.w3.org/WAI/tutorials/tables/
13. WAI-ARIA APG Table Pattern  
    https://www.w3.org/WAI/ARIA/apg/patterns/table/
14. WAI Forms Instructions  
    https://www.w3.org/WAI/tutorials/forms/instructions/
15. WCAG 2.2 Understanding: On Input  
    https://www.w3.org/WAI/WCAG22/Understanding/on-input.html
16. WCAG 2.2 Understanding: Status Messages  
    https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html
17. WAI-ARIA 1.2 `status` and `alert` roles  
    https://www.w3.org/TR/wai-aria-1.2/#status  
    https://www.w3.org/TR/wai-aria-1.2/#alert
18. WCAG 2.2 Understanding: Error Identification / Error Suggestion / Use of Color / Contrast  
    https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html  
    https://www.w3.org/WAI/WCAG22/Understanding/error-suggestion.html  
    https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html  
    https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
19. WAI-ARIA 1.2 `aria-current`  
    https://www.w3.org/TR/wai-aria-1.2/#aria-current
20. USWDS pagination guidance (supplemental UI precedent)  
    https://designsystem.digital.gov/components/pagination/

## Findings that changed the PRD

### 1. Audit more than successful writes

The PRD includes both successful and denied privileged actions for user roles, billing settings, and SSO configuration. OWASP, NIST, Google Cloud, and Microsoft Entra all support logging security-relevant administrative activity, not just successful changes.

### 2. Capture compliance-grade event detail

The PRD requires actor, target resource, action category, timestamp, source/context, result, correlation identifier, and redacted before/after values. This came directly from OWASP event attributes, NIST AU-3, and Microsoft Entra audit record guidance.

### 3. Redact secrets and high-risk sensitive fields

The PRD explicitly avoids storing passwords, access tokens, raw payment credentials, secret keys, or unredacted SSO secrets in event detail or exports. This was driven by OWASP and Google logging best practices.

### 4. Treat the log as append-only and tamper-evident

The PRD requires system-generated, non-editable audit records plus protection against deletion/tampering and logging of audit-log access/export activity. This came from NIST AU-9, OWASP guidance, RFC 5848, and Microsoft Entra's immutable-event model.

### 5. Require filterability and export for reviewability

The PRD includes date, actor, event family, target, and result filters plus CSV/JSON export. This is supported by NIST AU-6 and vendor examples from Microsoft Entra and GitHub Enterprise Cloud.

### 6. Plan for lag, ordering, and deduplication

The PRD assumes audit events may arrive out of order or with processing delay. It therefore requires immutable event IDs and correlation identifiers, influenced by Okta and Microsoft guidance.

### 7. Accessibility must be explicit

The PRD includes labeled filters, semantic tables, keyboard operation, status announcements, accessible pagination, and perceivable error states. This came from W3C/WAI and WCAG 2.2 guidance.

## Key risks and caveats

- The target application's real stack is unknown, so research was kept stack-agnostic.
- Vendor documentation was used only as supplemental product precedent, not as the sole basis for major decisions.
- Retention duration is policy-driven; the PRD uses an assumption and calls out the need to align with actual compliance commitments.
- No official target-app documentation was available, so accepted assumptions are recorded separately in the interview log and Further Notes.
