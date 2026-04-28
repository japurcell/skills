# Interview Log

## Initial assumptions surfaced before questioning
1. This is a web application with authenticated user accounts.
2. The current repository is not the target application, so product decisions must rely on explicit assumptions plus official guidance.
3. Email is the only outbound channel in scope.
4. The feature is for end users, not internal operators.

---

## Question 1
**Question:** Should launch be limited to signed-in end users managing their own saved-search alerts, rather than shared, team, or admin-managed alerts?

**Why it matters:** This sets the permissions model, data ownership rules, account-area UX, and support burden. It also determines whether the PRD needs collaboration and delegated-administration workflows.

**Options:**
1. Individual user alerts only — simplest ownership and lowest launch complexity.
2. Workspace/shared alerts — broader collaboration value but significantly more permission complexity.
3. Admin-managed alerts for other users — adds support/compliance complexity immediately.

**Recommendation:** Option 1, because the prompt already anchors management in the user's account area and there is no target-app prior art proving shared-alert permissions.

**Later decisions that depend on this:** limits per user, account-area management model, unsubscribe semantics, audit requirements.

**Assumed accepted answer:** Launch with individual user-owned alerts only.

---

## Question 2
**Question:** Should launch support daily and weekly email cadences plus pause, while deferring immediate/realtime alerts?

**Why it matters:** Frequency options affect scheduler complexity, volume, deliverability risk, user fatigue, and the shape of the save/manage UI.

**Options:**
1. Daily + weekly + paused — balanced launch scope.
2. Realtime + daily + weekly + paused — higher value but higher delivery and abuse risk.
3. Single digest cadence only — simplest, but weaker user control.

**Recommendation:** Option 1, because it gives meaningful user choice while limiting operational and deliverability risk for a first release.

**Later decisions that depend on this:** scheduler design, email copy, alert limits, success metrics.

**Assumed accepted answer:** Launch with daily, weekly, and paused states; defer realtime alerts.

---

## Question 3
**Question:** Should an alert email send only when there are new matching results since the last successful send?

**Why it matters:** This determines whether the product behaves like a useful signal or a repetitive reminder. It also affects storage needs, deduplication, and user trust.

**Options:**
1. Send only when new matches exist — higher relevance, less noise.
2. Send on every scheduled run even with no changes — easier implementation but noisy.
3. Let users choose between both behaviors — more flexibility, more product complexity.

**Recommendation:** Option 1, because it minimizes noise and aligns with data-minimization and trust goals.

**Later decisions that depend on this:** what metadata must be stored, email template content, observability metrics.

**Assumed accepted answer:** Only send when there are new results since the last successful send.

---

## Question 4
**Question:** Should users create alerts from the search results page and manage them from the account area, with every email also linking to manage preferences and unsubscribe?

**Why it matters:** This defines the core entry points and recovery paths for the feature. It also sets expectations for support, accessibility, and compliance.

**Options:**
1. Create from search results; manage from account area; include manage/unsubscribe links in email.
2. Manage only from account area — simpler navigation but weaker discoverability.
3. Create and manage only inline on results pages — weaker central oversight.

**Recommendation:** Option 1, because it matches the prompt and gives users both contextual creation and centralized management.

**Later decisions that depend on this:** account-area table design, email footer requirements, user-story coverage.

**Assumed accepted answer:** Use search results for creation and account settings for management; include manage and unsubscribe links in every email.

---

## Question 5
**Question:** At launch, should users be able to rename, pause, resume, and delete existing alerts, but change search criteria by creating a new alert instead of editing the original search definition in place?

**Why it matters:** Editing criteria in place raises more UX, persistence, and audit questions than managing alert state. This choice materially changes the first-release scope.

**Options:**
1. Manage alert metadata/state only; create a new alert to change criteria.
2. Full in-place editing of criteria and cadence.
3. Read-only management with delete-and-recreate only.

**Recommendation:** Option 1, because it preserves useful self-service controls without forcing a more complex first-version editor.

**Later decisions that depend on this:** account-area actions, migration behavior, testing scope.

**Assumed accepted answer:** Launch with rename/pause/resume/delete, but use new-alert creation for criteria changes.

---

## Question 6
**Question:** Should the product cap the number of active alerts per user and prevent exact duplicates?

**Why it matters:** This is a product and operational safeguard against abuse, accidental over-subscription, and noisy duplicate mail.

**Options:**
1. Cap active alerts at 25 per user and block exact duplicates.
2. No cap at launch — simplest but risky.
3. Low cap (for example 5–10) — safer but may frustrate power users.

**Recommendation:** Option 1, because it protects system load while still accommodating active search users.

**Later decisions that depend on this:** validation messages, support policy, analytics thresholds.

**Assumed accepted answer:** Cap active alerts at 25 per user and prevent exact duplicate alerts.

---

## Question 7
**Question:** Should we treat saved-search alerts as subscribed/commercial email for compliance purposes and therefore require an unsubscribe path that works without forcing users to log in again?

**Why it matters:** This changes email content requirements, unsubscribe behavior, tracking obligations, and the boundary between account management and email-link actions.

**Options:**
1. Yes — follow the stricter compliance posture.
2. No — treat them as purely transactional.
3. Decide later after legal review — leaves a major PRD gap.

**Recommendation:** Option 1, because official guidance suggests a user-requested alert can still be treated as subscribed/commercial email depending on content and purpose, so designing for the stricter case is safer.

**Later decisions that depend on this:** email footer requirements, token design, suppression logic, success criteria.

**Assumed accepted answer:** Yes; require unsubscribe without fresh login and keep a manage-preferences path in the account area.

---

## Accepted decisions summary
- Individual, user-owned alerts only at launch.
- Daily, weekly, and paused cadence options at launch.
- Emails send only for new matching results.
- Create from search results; manage from account area; manage/unsubscribe from email.
- Rename/pause/resume/delete at launch; criteria changes handled by creating a new alert.
- Cap at 25 active alerts per user and block exact duplicates.
- Treat alert emails with the stricter subscribed/compliance posture.
