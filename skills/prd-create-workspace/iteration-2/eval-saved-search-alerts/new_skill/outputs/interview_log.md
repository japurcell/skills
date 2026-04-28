# Interview Log

## Offline benchmark note

Live answers were unavailable, so this log records the exact one-question-at-a-time sequence I would have used, including why each question matters, options when useful, my recommendation, and the assumed accepted answer before moving to dependent questions.

## Assumptions surfaced immediately

ASSUMPTIONS I'M MAKING:

1. This is a web application with signed-in user accounts.
2. Users already have a search experience worth saving, even though that code is not present in the current repository.
3. The feature is for end users managing their own alerts, not for admins managing alerts for others.
4. We are targeting email alerts only for v1, not SMS or push.
5. The product can send transactional/subscription email and can add secure unsubscribe links.
6. We are targeting modern web accessibility expectations and responsive account-area UX.

→ Because this is offline benchmark mode, I proceeded with the following assumed accepted answers.

## Decision tree ordering

- Audience/scope first
- Then cadence and delivery model
- Then recipient and unsubscribe model
- Then management UX and duplicate handling
- Then rollout and privacy boundaries

## Q1

**Question:** Should v1 be limited to signed-in end users managing their own saved-search alerts?

**Why it matters:** This determines permissions, account-area requirements, and whether the PRD needs admin/team-management workflows.

**Recommendation:** Yes — start with signed-in end users managing their own alerts, because the prompt explicitly mentions management from the user’s account area and there is no target-app evidence for workspace-wide or admin-managed alert models.

**Options:**

1. User-only management in v1 — simplest permissions model and clearest account-area fit.
2. Workspace-scoped shared alerts — adds ownership, visibility, and collaboration complexity.
3. Admin-managed alerts for others — adds role-based permissions and support overhead.

**Later decisions that depend on this:** recipient rules, permissions stories, account-area UX, out-of-scope boundaries.

**Assumed accepted answer:** Option 1 — v1 is user-only.

## Q2

**Question:** Should a saved alert represent the exact current search/filter state rather than a broader “topic subscription” abstraction?

**Why it matters:** This determines how alerts are defined, deduplicated, deep-linked from email, and tested across reload/back-navigation.

**Recommendation:** Yes — use the exact current search/filter state as the saved-search definition, because official web guidance strongly supports durable query-state representation for shareable, restorable web searches.

**Options:**

1. Exact current search/filter state — durable deep links and predictable behavior.
2. Topic subscription only — simpler copy, but ambiguous matching rules.
3. Hybrid model — flexible, but adds complexity before the core flow is proven.

**Later decisions that depend on this:** duplicate handling, email deep links, persistence shape, test coverage.

**Assumed accepted answer:** Option 1 — save the exact canonical search state.

## Q3

**Question:** Should v1 offer daily and weekly digests only, instead of real-time or highly customized cadences?

**Why it matters:** Cadence choices drive scheduler complexity, user expectations, deliverability risk, and operational load.

**Recommendation:** Yes — start with daily and weekly digests only, because users still get meaningful control while the product avoids the complexity and higher alert volume of immediate notifications.

**Options:**

1. Daily and weekly only — clear and manageable for v1.
2. Immediate, daily, and weekly — broader flexibility, but more operational complexity.
3. Fully custom schedules — highest flexibility, highest complexity.

**Later decisions that depend on this:** email copy, scheduler behavior, account-area editing UI, success criteria, out-of-scope items.

**Assumed accepted answer:** Option 1 — daily and weekly digests only.

## Q4

**Question:** Should alerts send only when there are new matching results since the last successful delivery?

**Why it matters:** This determines the core value proposition, the definition of “useful alert,” and how often users may receive email.

**Recommendation:** Yes — send only when there is new matching content, because users generally want signal rather than repeated identical digests.

**Options:**

1. Send only when new matches exist — highest relevance, lowest noise.
2. Always send on schedule — easier to explain, but noisier.
3. Let users choose — flexible, but unnecessary complexity for v1.

**Later decisions that depend on this:** data needed for last-run/last-sent tracking, testing, email copy.

**Assumed accepted answer:** Option 1 — only send when new matches exist.

## Q5

**Question:** Should v1 send alerts only to the user’s primary verified account email address?

**Why it matters:** This affects consent, validation, recipient management, support complexity, and privacy risk.

**Recommendation:** Yes — use the primary verified account email only in v1, because it keeps consent and ownership clear while avoiding multi-recipient edge cases before the core workflow is proven.

**Options:**

1. Primary verified account email only — lowest ambiguity and support burden.
2. Let users enter any email address — more flexibility, more verification/abuse risk.
3. Multiple recipients — team workflow value, but much broader scope.

**Later decisions that depend on this:** form requirements, validation, privacy copy, out-of-scope items.

**Assumed accepted answer:** Option 1 — primary verified account email only.

## Q6

**Question:** Should users be able to manage alerts both at creation time and later from a dedicated account-area list?

**Why it matters:** This decides whether alert management is discoverable after the initial save and whether the account area needs edit/pause/delete flows.

**Recommendation:** Yes — allow creation from the search flow and ongoing management from the account area, because the prompt explicitly calls for account-area management and users should not have to rediscover the originating search page to make changes.

**Options:**

1. Create from search, manage later from account area — best balance of discoverability and control.
2. Manage only from search — weaker long-term discoverability.
3. Manage only from account area — slower initial activation.

**Later decisions that depend on this:** account-area information architecture, status messages, edit/pause/delete user stories.

**Assumed accepted answer:** Option 1 — create in search, manage in account area.

## Q7

**Question:** Should equivalent saved searches be deduplicated so users update an existing alert instead of creating duplicates for the same canonical search?

**Why it matters:** This affects user confusion, scheduler volume, email duplication, and how canonical search state is compared.

**Recommendation:** Yes — deduplicate equivalent searches and offer an update path, because duplicate alerts for the same search intent create unnecessary noise and operational waste.

**Options:**

1. Deduplicate equivalent searches and prompt to update — cleanest user experience.
2. Allow unlimited duplicates — simplest implementation, worst user experience.
3. Deduplicate only by name — easy to understand, but technically weak.

**Later decisions that depend on this:** persistence model, validation, account-area UX, testing.

**Assumed accepted answer:** Option 1 — deduplicate by canonical search definition.

## Q8

**Question:** Should every alert email include login-free one-click unsubscribe for that specific alert, in addition to account-area management?

**Why it matters:** This affects deliverability, compliance posture, and user trust.

**Recommendation:** Yes — require both account-area management and per-alert login-free unsubscribe from email, because official sender guidance and RFCs strongly support this model.

**Options:**

1. One-click unsubscribe plus account-area management — strongest user control.
2. Account-area management only — weaker deliverability/compliance posture.
3. Global unsubscribe only — too coarse for multiple saved alerts.

**Later decisions that depend on this:** email template requirements, suppression behavior, security constraints on unsubscribe tokens, success criteria.

**Assumed accepted answer:** Option 1 — include per-alert one-click unsubscribe.

## Q9

**Question:** Should paused alerts be retained and resumable, rather than forcing delete-and-recreate behavior?

**Why it matters:** This affects lifecycle state, account-area usability, and whether users can temporarily reduce email without losing configuration.

**Recommendation:** Yes — support pause/resume, because it gives users a reversible, low-friction control that is especially useful for digest-style notifications.

**Options:**

1. Pause/resume plus delete — best user control.
2. Delete only — simpler, but less forgiving.
3. Global mute only — too coarse.

**Later decisions that depend on this:** lifecycle fields, status messaging, testing, success criteria.

**Assumed accepted answer:** Option 1 — include pause/resume.

## Q10

**Question:** Should rollout be staged behind a feature flag or controlled enablement instead of instantly turning the feature on for all users?

**Why it matters:** This determines launch risk, observability requirements, and how the team reacts to deliverability or usability issues.

**Recommendation:** Yes — use staged rollout, because recurring email features carry sender-reputation and unsubscribe risks that are safer to monitor before broad release.

**Options:**

1. Controlled staged rollout — safest launch path.
2. Immediate full rollout — fastest launch, highest risk.
3. Private beta only — lowest risk, slower validation.

**Later decisions that depend on this:** observability stories, launch criteria, support readiness.

**Assumed accepted answer:** Option 1 — staged rollout.

## Final accepted assumptions carried into the PRD

- v1 is for signed-in users managing their own alerts.
- A saved alert is the exact canonical search/filter state.
- v1 cadence options are daily and weekly digests only.
- Emails send only when new matching results exist.
- The recipient is the user’s primary verified account email.
- Users can create from the search flow and manage later from the account area.
- Equivalent searches are deduplicated and updateable.
- Every alert email includes login-free one-click unsubscribe for that alert.
- Alerts can be paused/resumed or deleted.
- Release is staged and monitored.
