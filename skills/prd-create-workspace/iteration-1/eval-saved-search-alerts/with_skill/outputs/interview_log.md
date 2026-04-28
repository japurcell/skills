# Interview Log: Saved Searches With Email Alerts PRD

Because this eval cannot pause for live responses, each question is recorded in the order the skill would ask it. The assumed answer accepts the recommendation before moving to dependent questions.

## 1. V1 ownership model

**Question:** Should v1 saved searches and email alerts be personal per-user resources rather than team/workspace-shared alerts?

**Why it matters:** Ownership affects permissions, account-area IA, schema shape, sharing rules, and authorization tests.

**Options:**
1. Personal per-user alerts only - simpler ownership and lower privacy risk.
2. Team/workspace-shared alerts - useful for collaboration but requires roles, sharing, and admin controls.
3. Both in v1 - broadest scope and highest complexity.

**Recommended answer:** Personal per-user alerts only, because the request says users manage existing alerts from their account area and official authorization guidance favors least privilege for user-owned resources.

**Assumed answer used for eval:** Accepted recommendation: v1 is per-user only.

## 2. Saveable search scope

**Question:** Should users be able to save the current query plus supported filters from the primary search results experience?

**Why it matters:** This defines what data is stored and whether the feature needs to support every possible transient UI state.

**Options:**
1. Save canonical query and supported filters - testable and safer.
2. Save full URLs/client state - faster to design but brittle and harder to validate.
3. Save only keyword searches - simplest but may not meet user expectations if filters matter.

**Recommended answer:** Save canonical query and supported filters, because server-side validation and bounded schemas reduce injection, malformed state, and future compatibility risk.

**Assumed answer used for eval:** Accepted recommendation: save canonical search parameters and supported filters.

## 3. Alert trigger semantics

**Question:** Should alert emails include only new matching results since the last successful alert rather than repeating all current matches?

**Why it matters:** This affects result-diffing, stored delivery state, email value, and sender reputation.

**Options:**
1. Only new matching results since the previous successful alert.
2. Full current result set every time.
3. New and changed results.

**Recommended answer:** Only new matching results for v1, because repeated unchanged emails are noisy and major mailbox providers emphasize user-valued, expected mail.

**Assumed answer used for eval:** Accepted recommendation: v1 alerts send only when new matching results exist.

## 4. Frequency choices

**Question:** Should v1 support instant, daily, weekly, paused, and off rather than custom schedules?

**Why it matters:** Frequency choices drive scheduler complexity, user expectations, email volume, and testing.

**Options:**
1. Instant, daily, weekly, paused, and off.
2. Daily and weekly only.
3. Fully custom schedules/timezones.

**Recommended answer:** Instant, daily, weekly, paused, and off, because this gives users meaningful control while keeping delivery volume and scheduler complexity bounded.

**Assumed answer used for eval:** Accepted recommendation: support instant, daily, weekly, paused, and off.

## 5. Account-area controls

**Question:** Should the account area include list, edit frequency, pause/resume, delete, and unsubscribe-all controls for saved-search alerts?

**Why it matters:** This determines the management surface, account navigation requirements, and user-support outcomes.

**Options:**
1. Full management controls in account area.
2. Basic list/delete only.
3. Manage only from each alert email.

**Recommended answer:** Full account-area management, because the feature request explicitly asks users to manage alerts from their account area and email regulations/provider guidance expect easy preference management.

**Assumed answer used for eval:** Accepted recommendation: account area provides full management controls.

## 6. Email unsubscribe behavior

**Question:** Should every alert email include visible unsubscribe, manage-alerts, and standards-based one-click unsubscribe support that works without login?

**Why it matters:** This affects compliance, email templates, token design, and suppression tests.

**Options:**
1. Visible unsubscribe plus one-click unsubscribe and manage-alerts links.
2. Visible unsubscribe only.
3. Account-area unsubscribe only after login.

**Recommended answer:** Visible unsubscribe plus one-click unsubscribe and manage-alerts links, because FTC, Gmail/Yahoo, and RFC 8058 guidance all favor low-friction unsubscribe for recurring subscription email.

**Assumed answer used for eval:** Accepted recommendation: every alert email includes all three controls, and unsubscribe does not require login.

## 7. Suppression and compliance SLA

**Question:** Should opt-outs suppress future alert email within a 48-hour product target even if legal requirements allow longer in some contexts?

**Why it matters:** This affects job scheduling, cache invalidation, suppression storage, and customer trust.

**Options:**
1. 48-hour product target with faster best effort.
2. Legal minimum only.
3. Immediate synchronous guarantee for every system.

**Recommended answer:** 48-hour product target with faster best effort, because major mailbox providers recommend prompt unsubscribe handling and legal minimums are not sufficient for user trust.

**Assumed answer used for eval:** Accepted recommendation: target suppression within 48 hours.

## 8. Privacy and retention

**Question:** Should saved search criteria be treated as potentially sensitive user data with deletion on alert deletion/account closure and redaction from logs by default?

**Why it matters:** Search terms can reveal user intent, interests, or location, and logs can become a secondary privacy risk.

**Options:**
1. Treat criteria as sensitive user-owned data.
2. Treat criteria as ordinary preference metadata.
3. Decide later during implementation.

**Recommended answer:** Treat criteria as sensitive user-owned data, because FTC/NIST privacy guidance recommends minimizing and protecting personal information and stored searches can be revealing.

**Assumed answer used for eval:** Accepted recommendation: sensitive-data handling is required.

## 9. Delivery operations

**Question:** Should broad rollout wait until sender authentication, provider suppression handling, bounce/complaint processing, and delivery metrics are ready?

**Why it matters:** Recurring alerts can damage sender reputation or violate provider requirements if launched without operational controls.

**Options:**
1. Require deliverability readiness before broad rollout.
2. Launch first and add operations controls later.
3. Send only manual test alerts in v1.

**Recommended answer:** Require deliverability readiness before broad rollout, because Gmail/Yahoo and provider documentation emphasize authentication, complaint rates, suppression, and quota management.

**Assumed answer used for eval:** Accepted recommendation: rollout depends on delivery readiness.

## 10. Scope exclusions

**Question:** Should v1 explicitly exclude shared alerts, admin-created alerts, SMS/push/webhook delivery, custom schedules, promotional campaigns, and historical backfill?

**Why it matters:** Explicit non-goals prevent the PRD from becoming too broad and keep implementation planning focused.

**Options:**
1. Exclude these from v1.
2. Include some of them now.
3. Leave them ambiguous.

**Recommended answer:** Exclude these from v1, because the core request is saved searches with email alerts managed from account settings.

**Assumed answer used for eval:** Accepted recommendation: exclusions are documented in Out of Scope.
