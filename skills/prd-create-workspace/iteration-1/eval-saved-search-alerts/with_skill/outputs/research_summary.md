# Targeted Web Research Summary

## Research target: Email compliance, unsubscribe, and preference management

**Sources:**
- FTC CAN-SPAM Act compliance guide: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- RFC 8058 one-click unsubscribe: https://www.rfc-editor.org/rfc/rfc8058
- RFC 2369 list unsubscribe header fields: https://www.rfc-editor.org/rfc/rfc2369
- Google sender guidelines: https://support.google.com/a/answer/81126
- Google sender FAQ: https://support.google.com/a/answer/14229414
- Yahoo sender best practices: https://senders.yahooinc.com/best-practices/

**Findings and supported decisions:**
- Recurring saved-search alerts should be treated as subscribed email with clear expectations, opt-in frequency, and easy opt-out. Supports PRD decisions for explicit frequency selection and account-area preference management.
- Every alert should include a clear unsubscribe action and manage-alerts link. Supports account-area controls, email-template requirements, and unsubscribe tests.
- One-click unsubscribe should use `List-Unsubscribe` and `List-Unsubscribe-Post: List-Unsubscribe=One-Click`, with a no-login POST flow. Supports email header requirements and endpoint testing.
- Opt-outs should be honored promptly. FTC requires honoring opt-outs within 10 business days, while Google/Yahoo guidance points toward faster handling such as 48 hours/2 days. Supports the PRD’s 48-hour suppression target.
- Alert email should avoid deceptive subjects, misleading sender identity, or promotional mixing unless commercial-email requirements are satisfied. Supports template review and legal/compliance review.

## Research target: Deliverability, authentication, suppression, and provider testing

**Sources:**
- Google sender guidelines: https://support.google.com/a/answer/81126
- Yahoo sender best practices: https://senders.yahooinc.com/best-practices/
- SPF RFC 7208: https://datatracker.ietf.org/doc/html/rfc7208
- DKIM RFC 6376: https://datatracker.ietf.org/doc/html/rfc6376
- DMARC RFC 7489: https://datatracker.ietf.org/doc/html/rfc7489
- AWS SES sending quotas: https://docs.aws.amazon.com/ses/latest/dg/manage-sending-quotas.html
- AWS SES suppression list: https://docs.aws.amazon.com/ses/latest/dg/sending-email-suppression-list.html
- AWS SES mailbox simulator: https://docs.aws.amazon.com/ses/latest/dg/send-an-email-from-console.html#send-email-simulator
- Twilio SendGrid suppressions: https://www.twilio.com/docs/sendgrid/ui/sending-email/index-suppressions
- Twilio SendGrid sandbox mode: https://www.twilio.com/docs/sendgrid/for-developers/sending-email/sandbox-mode

**Findings and supported decisions:**
- Sender authentication with SPF, DKIM, DMARC, aligned identity, TLS, and RFC-compliant formatting is a launch prerequisite. Supports deliverability readiness requirements and rollout gates.
- Providers impose sending quotas and rate limits. Supports throttling, digesting, idempotency, and scheduler observability requirements.
- Suppression, bounce, and complaint handling must be first-class product behavior. Supports suppression state, disabled-alert messaging, webhook processing, and operational metrics.
- Provider simulators/sandbox modes should be used for tests without contacting real users. Supports testing requirements for email delivery, bounce, complaint, and suppression scenarios.
- Provider sandbox modes have limitations. Supports separate webhook-fixture tests and template/content validation outside sandbox delivery.

## Research target: Accessibility for search-saving and account alert management

**Sources:**
- W3C WAI Forms Labels: https://www.w3.org/WAI/tutorials/forms/labels/
- W3C WAI Forms Grouping: https://www.w3.org/WAI/tutorials/forms/grouping/
- W3C WAI Forms Instructions: https://www.w3.org/WAI/tutorials/forms/instructions/
- WCAG 2.2 Status Messages: https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html
- WCAG 2.2 Error Identification: https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html
- WCAG 2.2 Error Suggestion: https://www.w3.org/WAI/WCAG22/Understanding/error-suggestion.html
- WCAG 2.2 Focus Order: https://www.w3.org/WAI/WCAG22/Understanding/focus-order.html
- WCAG 2.2 Name, Role, Value: https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html
- WCAG 2.2 Target Size Minimum: https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- WCAG 2.2 Re-authenticating: https://www.w3.org/WAI/WCAG22/Understanding/re-authenticating.html
- WAI-ARIA search role: https://www.w3.org/TR/wai-aria-1.2/#search

**Findings and supported decisions:**
- Search, saved-search name, frequency controls, and submit actions need visible labels and programmatic names. Supports UI acceptance criteria and component tests.
- Frequency choices should be grouped with fieldset/legend or equivalent semantics, with associated instructions. Supports account-area form requirements.
- Save/update/delete/loading/no-results statuses must be announced without unnecessary focus theft. Supports live-region/status-message requirements.
- Errors must be identified in text and provide safe suggestions. Supports validation-error UI requirements.
- Edit, pause/resume, delete, and frequency controls must be keyboard-operable with predictable focus and adequate target sizes. Supports accessibility testing and native-control preference.
- Re-authentication should preserve alert-management work where feasible. Supports session-timeout requirements.

## Research target: Security, privacy, and data lifecycle

**Sources:**
- OWASP Authorization Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- OWASP Input Validation Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
- OWASP Application Security Verification Standard: https://owasp.org/www-project-application-security-verification-standard/
- FTC Protecting Personal Information guide: https://www.ftc.gov/business-guidance/resources/protecting-personal-information-guide-business
- NIST SP 800-122: https://csrc.nist.gov/publications/detail/sp/800-122/final
- NIST SP 800-53 Rev. 5: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final

**Findings and supported decisions:**
- Saved search criteria may reveal sensitive user intent and should be minimized, protected, deleted when no longer needed, and redacted from logs by default. Supports privacy and retention requirements.
- Every saved-search operation must enforce object ownership and least privilege at the server side. Supports per-user v1 scope and authorization tests.
- Search queries, filters, names, frequency values, pagination, and schedule inputs need explicit server-side validation. Supports validation schemas and malicious-input tests.
- Email-provider credentials and workers should use least privilege and auditable integrations. Supports operational and security requirements for delivery infrastructure.
- Logs, URLs, caches, emails, and support tools should avoid unnecessary exposure of raw query/filter values. Supports privacy acceptance criteria and logging tests.
