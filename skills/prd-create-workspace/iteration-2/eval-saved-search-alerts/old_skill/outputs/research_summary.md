# Research Summary

## Scope
Because the current repository is not the target application, official external sources were used to shape requirements for accessibility, email compliance/deliverability, and privacy/security.

## Accessibility findings
1. **Use explicit labels and grouped controls for frequency selection.**
   - Source: W3C WAI Forms Tutorial — https://www.w3.org/WAI/tutorials/forms/
   - Source: W3C WAI Grouping Controls — https://www.w3.org/WAI/tutorials/forms/grouping/
   - Source: WCAG 2.2 Labels or Instructions — https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html
   - PRD impact: saved-search forms should use clearly labeled native controls; frequency choices should be grouped and understandable to screen-reader and keyboard users.

2. **Save/update/delete actions need accessible status messaging.**
   - Source: WCAG 2.2 Status Messages — https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html
   - Source: W3C WAI Form Notifications — https://www.w3.org/WAI/tutorials/forms/notifications/
   - Source: MDN `aria-live` reference — https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-live
   - PRD impact: account-area management and save flows should announce success and error states without unexpectedly moving focus.

3. **Keyboard order and modal behavior must remain predictable.**
   - Source: WCAG 2.2 Focus Order — https://www.w3.org/WAI/WCAG22/Understanding/focus-order.html
   - Source: WCAG 2.2 Focus Visible — https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html
   - Source: WAI-ARIA APG Modal Dialog Pattern — https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/
   - PRD impact: if edit/delete confirmation dialogs are used, they must trap focus correctly, expose visible focus states, and return focus when closed.

## Email compliance and deliverability findings
4. **Treat alert emails as subscribed/commercial by default unless legal review proves otherwise.**
   - Source: FTC CAN-SPAM Compliance Guide (edited Jan 2024) — https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
   - PRD impact: every email should include sender identification, a clear unsubscribe path, and preference-management language.

5. **Unsubscribe must be simple and durable.**
   - Source: FTC CAN-SPAM Compliance Guide — https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
   - PRD impact: users must be able to stop alerts without completing a complicated multi-step flow; suppression handling and testing need explicit requirements.

6. **Plan for one-click unsubscribe and sender-authentication expectations early.**
   - Source: Google Email Sender Guidelines — https://support.google.com/a/answer/81126?hl=en
   - Source: Google FAQ on sender requirements — https://support.google.com/a/answer/14229414?hl=en
   - Source: RFC 2369 — https://www.rfc-editor.org/rfc/rfc2369
   - Source: RFC 8058 — https://www.rfc-editor.org/rfc/rfc8058
   - PRD impact: the feature should support standards-based unsubscribe headers, opaque unsubscribe tokens, and email infrastructure that can satisfy major mailbox-provider requirements if volume grows.

## Privacy and security findings
7. **Store only the alert data necessary to operate the feature.**
   - Source: ICO Data Minimisation guidance (2025-09-09) — https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/data-minimisation/
   - PRD impact: persist normalized search criteria, cadence, state, and delivery metadata only; avoid unnecessary result snapshots or verbose query-history retention.

8. **Consent/preferences should be explicit, auditable, and easy to withdraw.**
   - Source: ICO consent guidance (2026-04-17) — https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/consent/how-should-we-obtain-record-and-manage-consent/
   - Source: ICO electronic mail marketing guidance — https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guide-to-pecr/electronic-and-telephone-marketing/electronic-mail-marketing/
   - PRD impact: the system should record alert preference state changes and support easy withdrawal from account settings or email links.

9. **State-changing account actions need strong session and CSRF protections, while unsubscribe links should use opaque tokens instead of logged-in session context.**
   - Source: NIST SP 800-63B Session guidance — https://pages.nist.gov/800-63-4/sp800-63b/session/
   - Source: OWASP CSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
   - Source: OWASP query-string information exposure note — https://owasp.org/www-community/vulnerabilities/Information_exposure_through_query_strings_in_url
   - PRD impact: authenticated management actions should require secure state-changing requests; unsubscribe/manage links should avoid leaking raw search criteria or reusable secrets in URLs.

## How research changed the PRD
- Accessibility requirements became explicit, not implied.
- Email-management flows include both preference management and unsubscribe.
- The PRD uses a minimal stored-alert model and explicit consent/preference recording.
- Security requirements distinguish authenticated account changes from tokenized email-link actions.
- Success criteria include behavioral, compliance, and observability outcomes rather than only UI completion.
