# PRD: Saved Searches with Email Alerts

## Objective
Add a saved-search alert feature for signed-in users so they can save a search, choose an email-update cadence, and manage alert state from their account area. Success means users can create relevant alerts without confusion, receive updates only when new matching results appear, pause or remove alerts without support help, and stop emails easily from either the account area or the email itself.

## User Stories
1. As a signed-in user, I want to save my current search so I do not have to recreate it later.
2. As a signed-in user, I want to choose how often I receive updates so the product matches my urgency and inbox tolerance.
3. As a signed-in user, I want the product to email me only when there are new matching results so alerts stay useful.
4. As a signed-in user, I want to name an alert so I can distinguish similar searches in my account area.
5. As a signed-in user, I want to review all active and paused alerts in one place so I can manage them efficiently.
6. As a signed-in user, I want to pause an alert temporarily without deleting it so I can stop emails during low-interest periods.
7. As a signed-in user, I want to resume a paused alert so I can restart updates without rebuilding the search.
8. As a signed-in user, I want to delete an alert so I no longer receive those emails.
9. As a signed-in user, I want validation feedback if I try to save a duplicate or exceed the alert limit so I understand what to fix.
10. As a signed-in user, I want clear success and error messages when I create, update, pause, resume, or delete an alert.
11. As a screen-reader or keyboard-only user, I want the save and manage flows to be fully accessible so I can use the feature independently.
12. As a privacy-conscious user, I want only the minimum necessary search criteria stored so the product does not retain unnecessary personal data.
13. As a user opening an alert email, I want a direct way to manage preferences so I can change cadence without hunting through the product.
14. As a user opening an alert email, I want to unsubscribe even if I am not already logged in so stopping mail is easy.
15. As a support or operations team member, I want reliable state tracking for create/pause/resume/delete/unsubscribe events so issues can be diagnosed.
16. As a product team member, I want adoption, send, unsubscribe, and failure metrics so launch quality can be evaluated.
17. As a security reviewer, I want account-area alert changes protected by the normal authenticated session boundary so one user cannot alter another user's alerts.
18. As a compliance reviewer, I want email content and suppression behavior to respect unsubscribe and preference rules so the product avoids avoidable regulatory and deliverability risk.

## Implementation Decisions
- Limit launch scope to authenticated users managing their own alerts only. Citation: Official privacy/security guidance emphasizes explicit ownership, authenticated state changes, and auditable preference management, including NIST session guidance and ICO consent guidance ([NIST](https://pages.nist.gov/800-63-4/sp800-63b/session/), [ICO consent](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/consent/how-should-we-obtain-record-and-manage-consent/)). Reason: this keeps permissions and consent boundaries unambiguous for a first release.
- Provide two product entry points: create from search results and manage from the account area. Citation: Accepted product-scope decision from the discovery interview, supported by W3C form guidance for clearly labeled save flows and accessible settings forms ([W3C forms](https://www.w3.org/WAI/tutorials/forms/)). Reason: users need contextual creation plus centralized self-service management.
- Offer daily, weekly, and paused cadence options at launch; defer realtime alerts. Citation: Accepted discovery decision, supported by deliverability/compliance guidance that subscription mail should minimize avoidable volume and preserve clear preference control ([FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business), [Google sender guidelines](https://support.google.com/a/answer/81126?hl=en)). Reason: this provides meaningful choice without taking on immediate-alert complexity.
- Send an alert only when new matching results exist since the last successful send. Citation: ICO data-minimisation guidance ([ICO data minimisation](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/data-minimisation/)). Reason: the feature should deliver signal rather than repetitive no-change reminders, and should store only the metadata needed to detect new matches.
- Persist only the minimum alert data required to operate the feature: normalized search criteria, display name, cadence, state, ownership, delivery metadata, and preference/audit timestamps. Citation: ICO data minimisation and consent guidance ([ICO data minimisation](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/data-minimisation/), [ICO consent](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/consent/how-should-we-obtain-record-and-manage-consent/)). Reason: search criteria and email preferences can be personal data, so retention should stay intentionally narrow.
- Allow rename, pause, resume, and delete at launch, but handle criteria changes by creating a new alert rather than editing the original search definition in place. Citation: Existing codebase pattern in this environment treats explicit assumptions as first-class requirements inputs when target-app prior art is unavailable. Reason: this keeps first-release management useful while avoiding a more complex in-place alert editor while the real application's existing editing model is still unknown.
- Every email must include both a manage-preferences path and an unsubscribe path that does not require a fresh login. Citation: FTC guidance, Google sender requirements, RFC 2369, and RFC 8058 ([FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business), [Google sender guidelines](https://support.google.com/a/answer/81126?hl=en), [RFC 2369](https://www.rfc-editor.org/rfc/rfc2369), [RFC 8058](https://www.rfc-editor.org/rfc/rfc8058)). Reason: alert mail should be easy to stop and should be compatible with modern mailbox-provider expectations.
- Account-area save and manage actions must provide accessible labels, grouped controls, visible focus, and status messages that do not unexpectedly move focus. Citation: W3C WCAG 2.2 guidance for labels, focus order, focus visible, and status messages ([Labels or Instructions](https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html), [Focus Order](https://www.w3.org/WAI/WCAG22/Understanding/focus-order.html), [Focus Visible](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html), [Status Messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html)). Reason: the core user actions are form and settings interactions that must remain operable for keyboard and assistive-technology users.
- Protect authenticated management actions with the normal session boundary and CSRF defenses, while using opaque, purpose-limited tokens for email-link unsubscribe actions. Citation: NIST session guidance, OWASP CSRF guidance, and RFC 8058 ([NIST](https://pages.nist.gov/800-63-4/sp800-63b/session/), [OWASP CSRF](https://cheatsheetseries.owasp.org/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html), [RFC 8058](https://www.rfc-editor.org/rfc/rfc8058)). Reason: account actions and email-link actions have different trust models and should not share unsafe state assumptions.
- Cap active alerts at 25 per user and prevent exact duplicate alerts. Citation: Existing codebase pattern in this environment favors explicit, testable scope limits over implicit assumptions, and the PRD should keep operational guardrails reviewable when target-app evidence is missing. Reason: the launch should balance usefulness for engaged users with reasonable safeguards against duplicate mail and runaway subscription growth.
- Instrument creation, state changes, send outcomes, unsubscribe events, and delivery failures from day one. Citation: Existing codebase pattern in this environment favors explicit, testable success criteria and behavior-level validation over vague implementation detail. Reason: the feature spans UI, scheduling, and email delivery, so observability is required to evaluate launch quality.

## Tech Stack
- Assumed product shape: authenticated web application with a search results experience, an account/settings area, server-side alert evaluation, scheduled background work, and an email-delivery integration.
- Exact framework, database, queue/scheduler, and email provider are **to be confirmed in the real target application repository before implementation begins**.
- This PRD intentionally avoids inventing stack-specific prior art because the available repository is a Copilot skills repository rather than the target product.

## Commands
- Build: Confirm the real application build command in the target repository before implementation.
- Test: Confirm the real application test command in the target repository before implementation.
- Lint: Confirm the real application lint/format command in the target repository before implementation.
- Dev: Confirm the real application development/start command in the target repository before implementation.

## Project Structure
- Search experience: user-facing search and results surface where a user can create a saved alert from the current criteria.
- Account settings: user-facing management surface listing alert name, cadence, state, last-send status, and allowed actions.
- Alert persistence: application-owned model for alert criteria, cadence, ownership, and delivery metadata.
- Alert execution: scheduled evaluation flow that detects newly matching results and prepares outbound messages.
- Email delivery: message rendering, provider handoff, unsubscribe/header handling, and failure tracking.
- Analytics and support tooling: event tracking, operational dashboards, and support-visible state for diagnosing delivery or preference issues.

## Code Style
- Follow the existing naming, validation, error-shape, and state-management conventions of the real target application once that repository is confirmed.
- Prefer explicit labels, readable alert-state terminology, and user-facing copy that distinguishes active, paused, unsubscribed, and deleted states.
- Keep alert-management rules centralized so the UI, scheduling flow, and email pipeline do not drift on ownership, cadence, or unsubscribe behavior.

## Testing Decisions
- Good tests for this feature should verify external behavior and user-visible outcomes rather than internal implementation details. Prior art: existing codebase guidance in this environment prefers behavior-first testing and observable assertions. Reason: the feature crosses UI, background processing, and email delivery boundaries.
- Add UI/integration coverage for creating an alert from search results, including duplicate detection, alert-limit validation, success messaging, and accessible labels/focus behavior. Prior art: W3C WCAG 2.2 form and status-message guidance. Reason: the most failure-prone user entry point is the save flow.
- Add account-area behavior tests for list display, pause, resume, rename, delete, and empty/error states. Prior art: accepted launch scope and W3C focus/status guidance. Reason: users must be able to manage subscriptions without support intervention.
- Add scheduler/integration tests proving that emails send only when new matches exist, never for paused/deleted alerts, and respect per-user caps and duplicate rules. Prior art: ICO data-minimisation guidance plus accepted product decisions. Reason: alert quality depends on relevance and suppression behavior.
- Add email/content tests for manage-preferences links, unsubscribe links, standards-based unsubscribe headers where applicable, and correct handling of expired/invalid tokens. Prior art: FTC, Google, RFC 2369, and RFC 8058. Reason: compliance and deliverability failures are user-visible and high-risk.
- Add security tests for ownership enforcement, authenticated state changes, CSRF resistance, and opaque token behavior for email-link actions. Prior art: NIST and OWASP guidance. Reason: preference changes are state-changing operations that must resist cross-user or cross-site abuse.
- Add observability checks for creation, send, skip, bounce/failure, and unsubscribe event tracking so rollout quality can be measured. Prior art: explicit success-criteria pattern used in this environment. Reason: launch decisions need evidence, not anecdote.

## Boundaries
- Always: validate user input, require clear user-facing success/error feedback, protect state-changing account actions, include unsubscribe/manage links in alert mail, and run the target application's relevant tests before shipping.
- Ask first: database/schema changes, new scheduler or queue dependencies, new email vendors, regional legal/compliance requirements, and any expansion to shared or admin-managed alerts.
- Never: send alert emails with no unsubscribe path, expose raw search criteria or reusable secrets in URLs, let one user manage another user's alerts without authorization, or ship the feature without observable create/send/unsubscribe metrics.

## Success Criteria
- A signed-in user can save the current search as an alert with a name and cadence from the search experience.
- A signed-in user can view all alerts in the account area and can rename, pause, resume, or delete them without support help.
- The system sends email only when new matching results exist since the last successful send.
- Exact duplicate alerts are blocked and users receive clear recovery guidance.
- Users can stop email either from the account area or from the email itself without a confusing multi-step flow.
- Save/manage flows meet accessibility expectations for labels, keyboard navigation, focus visibility, and status messaging.
- State-changing account actions enforce authenticated ownership, and email-link actions use safe token-based flows.
- Product and operations teams can measure creation rate, active-alert count, send volume, send failures, unsubscribe rate, and alert-management actions.

## Out of Scope
Realtime or per-result alerts at launch.
Shared, team, workspace-level, or admin-managed alerts.
Channels other than email, including SMS, push, or chat.
In-place editing of the underlying search criteria for an existing alert.
Complex alert-rule builders beyond the existing search experience.
Recommendations, ranking changes, or search-quality improvements unrelated to alert delivery.
Native mobile experiences unless the real product team explicitly expands scope.

## Further Notes
- The available repository for this benchmark is a Copilot skills repository, not the actual target application. This PRD therefore uses official research plus explicit assumptions instead of inventing unavailable app-specific prior art.
- Accepted assumptions for this draft: individual user-owned alerts only; daily/weekly/paused cadences at launch; emails only when new results exist; create from search results; manage from account area; manage/unsubscribe links in every email; rename/pause/resume/delete at launch; criteria changes require creating a new alert; 25 active alerts max per user.
- Before implementation starts, the team should confirm the real application stack, repository commands, existing search architecture, email provider, scheduler model, and any region-specific legal requirements.
