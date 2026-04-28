# Interview Log

Because this is an offline benchmark run, the normal one-question-at-a-time interview was simulated. Each question is listed in dependency order with the recommended answer and the assumed answer used for this eval.

## Question 1

**Question:** Should v1 include all three requested event categories: user role changes, billing settings changes, and SSO configuration changes?

**Why it matters:** This parent scope decision determines event taxonomy, permissions, redaction, testing, and rollout. Narrowing the scope would change almost every downstream requirement.

**Options:**
1. Include all three categories in v1 - highest compliance value and matches the stated need.
2. Start with role changes only - fastest path but leaves billing and SSO audit gaps.
3. Start with security-sensitive roles and SSO only - reduces billing complexity but does not satisfy billing compliance review.

**Recommendation:** Include all three in v1 because the user explicitly named them and the skill evaluation expects admin, billing, auth/SSO, compliance, permissions, retention, and testing coverage.

**Assumed answer used:** Accepted the recommendation.

## Question 2

**Question:** Should v1 log both successful changes and failed or denied attempts for the covered event categories?

**Why it matters:** Failed attempts affect event volume, UI filters, security review, and tests, but they are important for investigation and compliance evidence.

**Options:**
1. Log successful changes only - simpler but misses suspicious or misconfigured attempts.
2. Log successful changes plus failed/denied attempts - stronger accountability and security review.
3. Log failed attempts only for SSO and roles - narrower but inconsistent across categories.

**Recommendation:** Log successful changes plus failed/denied attempts for all covered categories, with clear result status and failure reason where safe.

**Assumed answer used:** Accepted the recommendation.

## Question 3

**Question:** Who should be allowed to view the audit log in v1?

**Why it matters:** Audit logs expose identity, billing, and security metadata. The access model drives permissions, UI visibility, export behavior, and authorization tests.

**Options:**
1. Team owners only - safest but too restrictive for compliance workflows.
2. Team owners plus explicit compliance/security admins - supports delegated review while preserving least privilege.
3. All team admins - easiest but risks exposing billing and SSO metadata too broadly.

**Recommendation:** Allow team owners and explicit compliance/security admins; require billing-level permission for detailed billing events.

**Assumed answer used:** Accepted the recommendation.

## Question 4

**Question:** How much before/after detail should events show?

**Why it matters:** Compliance reviewers need meaningful change details, but raw billing and SSO payloads can contain secrets, payment data, certificates, tokens, and PII.

**Options:**
1. Show full raw before/after payloads - maximum detail but unacceptable security/privacy risk.
2. Show allowlisted field summaries with redaction - useful and safer.
3. Show only generic event names - safest but often insufficient for audits.

**Recommendation:** Show allowlisted before/after summaries for non-sensitive fields, redact or summarize sensitive values, and never store raw secrets or payment credentials.

**Assumed answer used:** Accepted the recommendation.

## Question 5

**Question:** What default retention period should v1 use?

**Why it matters:** Retention affects compliance usefulness, storage cost, privacy obligations, purge jobs, and customer expectations.

**Options:**
1. 90 days - aligns with some vendor audit-log defaults but may be too short for annual reviews.
2. 180 days - stronger than many defaults but may still miss annual audit windows.
3. 365 days - practical default for annual compliance review while still finite and justifiable.
4. Indefinite - convenient but conflicts with storage-limitation principles unless legally required.

**Recommendation:** Use 365 days by default, with automated purge after retention unless legal hold or contractual retention applies; defer customer-configurable retention.

**Assumed answer used:** Accepted the recommendation.

## Question 6

**Question:** Should v1 include export, and if so which formats?

**Why it matters:** Compliance review often requires evidence outside the product. Export scope affects permissions, redaction, rate limits, async processing, and auditability.

**Options:**
1. No export in v1 - simpler but weak for compliance evidence.
2. CSV only - human-review friendly but less machine-readable.
3. CSV and JSON - useful for spreadsheet review and downstream evidence systems.
4. CSV, JSON, and SIEM streaming - powerful but larger v1 scope.

**Recommendation:** Include CSV and JSON export in v1, preserving active filters and stable event IDs; defer SIEM streaming/API access.

**Assumed answer used:** Accepted the recommendation.

## Question 7

**Question:** Should viewing or exporting audit logs create audit events?

**Why it matters:** Audit-log data is sensitive. Tracking access and export creates accountability but increases event volume.

**Options:**
1. Do not audit audit-log access - lower volume but weaker evidence control.
2. Audit exports only - captures high-risk access but misses sensitive viewing.
3. Audit both views and exports - strongest accountability.

**Recommendation:** Audit both views and exports, with lower-detail view events and detailed export events.

**Assumed answer used:** Accepted the recommendation.

## Question 8

**Question:** Should v1 backfill historical admin changes?

**Why it matters:** Backfill can help audits immediately, but unreliable historical sources may be incomplete, unattributable, or unsafe to expose.

**Options:**
1. No backfill; launch-forward only - clear and reliable.
2. Backfill only from reliable, attributable sources - useful if high-quality data exists.
3. Broad best-effort backfill - more data but risks misleading evidence.

**Recommendation:** Launch forward by default and only backfill from existing reliable, attributable, redaction-safe sources if implementation exploration proves quality.

**Assumed answer used:** Accepted the recommendation.

## Question 9

**Question:** Should v1 include customer-configurable retention, data residency controls, or legal hold management?

**Why it matters:** These can be important for enterprise compliance but significantly expand storage, policy, and admin UX scope.

**Options:**
1. Include all controls in v1 - enterprise-complete but large scope.
2. Document 365-day default and legal/contract exceptions; defer self-service controls - balanced v1.
3. Ignore residency/legal hold until requested - simpler but may create compliance gaps.

**Recommendation:** Document the 365-day default, legal/contract exceptions, and privacy review needs; defer self-service retention, residency, and legal hold management.

**Assumed answer used:** Accepted the recommendation.

## Question 10

**Question:** What should happen if the system cannot write an audit event for a covered admin change?

**Why it matters:** Silent audit-write failure undermines the feature, but blocking admin changes can affect operations during outages.

**Options:**
1. Apply the change and log best-effort later - high operational continuity but weak compliance.
2. Block covered changes unless the audit event is durably recorded - strongest compliance guarantee.
3. Allow a documented emergency degraded mode - balanced but requires governance.

**Recommendation:** Block covered changes unless the audit event is durably recorded, unless a formally approved degraded-mode policy exists.

**Assumed answer used:** Accepted the recommendation.

## Question 11

**Question:** Should the audit-log UI be required to meet WCAG 2.2 AA expectations for tables, filters, dialogs, status messages, and keyboard operation?

**Why it matters:** Audit review is an admin workflow with complex tables, filters, validation, exports, and async statuses. Accessibility affects usability and testing.

**Options:**
1. Require WCAG 2.2 AA-oriented behavior - clear and testable.
2. Require only basic keyboard access - insufficient for complex review workflows.
3. Defer accessibility requirements - high risk and inconsistent with product quality.

**Recommendation:** Require WCAG 2.2 AA-oriented behavior for the audit log table, filters, detail views, export controls, validation errors, and statuses.

**Assumed answer used:** Accepted the recommendation.

## Question 12

**Question:** Should alerts, approvals, SIEM streaming, and public audit-log APIs be included in v1?

**Why it matters:** These are common adjacent enterprise features but can distract from the core compliance-review log.

**Options:**
1. Include them all in v1 - high enterprise value but much larger scope.
2. Include only alerts - useful but not required to see historical evidence.
3. Defer all adjacent automation/integration features - focused PRD and faster validation.

**Recommendation:** Defer alerts, approvals, SIEM streaming, webhooks, and public API access; keep v1 focused on capture, review, filtering, export, redaction, retention, and permissions.

**Assumed answer used:** Accepted the recommendation.
