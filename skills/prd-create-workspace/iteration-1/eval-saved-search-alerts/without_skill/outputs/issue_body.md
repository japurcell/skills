## PRD: Saved searches with email alerts

### Summary
Add saved searches so users can persist useful search queries, subscribe to recurring email updates, and manage those alerts from their account area. This feature should help users avoid repeating manual searches and stay informed when new or updated results match criteria they care about.

### Problem
Users currently need to manually re-run searches to discover new matching items. This creates repeated effort, increases the chance that users miss important updates, and provides no centralized way to track or adjust searches they care about.

### Goals
- Allow an authenticated user to save a search from the search results experience.
- Let users choose an email alert frequency for each saved search.
- Send email updates when new or materially changed results match a saved search.
- Provide an account-area management interface for viewing, editing, pausing/resuming, and deleting saved search alerts.
- Give users clear control over email delivery and unsubscribe preferences.

### Non-goals
- Building a new search engine or changing core search relevance ranking.
- Supporting anonymous saved searches.
- Supporting non-email notification channels in the initial release.
- Supporting complex boolean alert rules beyond the existing search/filter model.
- Sending duplicate notifications for the same result unless it has materially changed.

### Target users
- Authenticated users who regularly search for similar criteria.
- Power users who monitor new matching content over time.
- Returning users who want alerts without manually visiting the application.

### User stories
1. As an authenticated user, I can save my current search so I can return to it later.
2. As an authenticated user, I can name a saved search so I can recognize it in my account area.
3. As an authenticated user, I can choose how often to receive email updates for a saved search.
4. As an authenticated user, I can view all existing saved searches and alerts from my account area.
5. As an authenticated user, I can edit a saved search name, criteria, and alert frequency.
6. As an authenticated user, I can pause or resume an alert without deleting the saved search.
7. As an authenticated user, I can delete a saved search and stop future alerts.
8. As an email recipient, I can unsubscribe from a specific alert or all saved-search alerts.

### Functional requirements

#### Saving a search
- Add a clear “Save search” action to the search results page for authenticated users.
- If the user is unauthenticated, prompt them to sign in or create an account before saving.
- Saving should capture the active query text, filters, sort order if relevant, and any other parameters needed to reproduce the search.
- Users should be able to provide or edit a saved search name before confirming.
- Default name should be generated from the query and/or primary filters when possible.
- Prevent accidental duplicate saved searches by warning when the same user already has a saved search with identical criteria.

#### Alert frequency
- Users should be able to select one of the supported frequencies when saving or editing a search:
  - Never / saved only
  - Daily
  - Weekly
  - Monthly
- Default frequency should be Weekly unless product analytics or existing notification defaults suggest otherwise.
- The system should store alert status separately from the saved search so users can pause alerts while keeping the search.

#### Email alerts
- Email alerts should include a concise summary of new matching results since the last successful alert send.
- Email alerts should include a link to view the full saved search results in the application.
- Email alerts should include a link to manage the alert in the account area.
- Email alerts must include unsubscribe controls compliant with applicable email requirements.
- If there are no new or materially changed matching results for a scheduled period, the system should not send an email by default.
- The system should avoid notifying users repeatedly about the same unchanged result.
- Alert jobs should handle transient email failures with retries and record delivery status for observability.

#### Account management
- Add a saved searches or alerts section to the account area.
- The management page should list each saved search with:
  - Name
  - Search criteria summary
  - Alert frequency
  - Alert status
  - Last sent date, if any
  - Created date
- Users should be able to:
  - Open/run the saved search
  - Rename the saved search
  - Edit alert frequency
  - Pause/resume alerts
  - Delete the saved search
- Deleting a saved search should require confirmation and permanently stop associated alerts.

#### Permissions and privacy
- Users may only view and manage their own saved searches.
- Saved search criteria should not expose private data to other users.
- Email alert links should require authentication unless the application already supports secure signed links.
- Unsubscribe links may use secure, time-bound or revocable tokens to support one-click unsubscribe without exposing account access.

#### Administration and operations
- The system should provide enough logging/metrics to monitor alert job success, email send failures, and unsubscribe activity.
- Consider rate limits or maximum saved searches per user to prevent abuse and accidental high-volume email sends.
- Email content should use existing application email templates and branding where available.

### UX requirements
- The save action should be discoverable but not disruptive on search results pages.
- Confirmation should make it clear whether the search was saved only or saved with email alerts enabled.
- Frequency controls should use plain language, e.g. “Send me daily updates when new results match.”
- Account management should be accessible from the user account area and work on mobile and desktop.
- Empty state should explain that saved searches let users quickly rerun searches and optionally receive email alerts.
- Destructive actions such as delete should include a confirmation step.

### Data model considerations
Potential entities/fields:
- SavedSearch
  - id
  - user_id
  - name
  - query text and serialized filter criteria
  - created_at
  - updated_at
- SavedSearchAlert
  - id
  - saved_search_id
  - frequency
  - status: active, paused, disabled
  - last_evaluated_at
  - last_sent_at
  - created_at
  - updated_at
- SavedSearchNotificationState
  - saved_search_id
  - result identifier
  - first_notified_at
  - last_notified_at
  - result version/hash if needed to detect material changes

Exact schema should follow the application’s existing persistence and notification patterns.

### API/backend requirements
- Endpoint or action to create a saved search.
- Endpoint or action to list saved searches for the current user.
- Endpoint or action to update saved search metadata and alert settings.
- Endpoint or action to pause/resume alerts.
- Endpoint or action to delete a saved search.
- Scheduled worker/job to evaluate saved searches by frequency.
- Email delivery integration using existing mail infrastructure.
- Tests verifying authorization boundaries so users cannot access or mutate another user’s saved searches.

### Acceptance criteria
- Given I am signed in and viewing search results, when I save the search with a name and weekly alerts, then the saved search appears in my account area with weekly alert frequency.
- Given I am not signed in, when I try to save a search, then I am prompted to sign in before the search is saved.
- Given I have an active daily alert and new matching results exist since the last alert, when the daily alert job runs, then I receive one email summarizing the new results.
- Given no new matching results exist for my scheduled alert period, when the alert job runs, then no email is sent.
- Given I pause an alert, when the scheduled alert job runs, then no email is sent for that saved search.
- Given I delete a saved search, when I return to the saved searches account page, then it no longer appears and future alert jobs do not evaluate it.
- Given I use an unsubscribe link from an alert email, then future emails for that alert stop and the account area reflects the disabled or paused state.
- Given another user attempts to access my saved search by ID, then access is denied.

### Analytics and success metrics
- Number of saved searches created per week.
- Percentage of saved searches with email alerts enabled.
- Email open and click-through rates for saved-search alerts.
- Alert unsubscribe and pause rates.
- Return visits generated from saved-search alert emails.
- Reduction in repeated manual searches for the same criteria, if measurable.

### Rollout plan
1. Implement saved search persistence and account management without email sending if needed behind a feature flag.
2. Add configurable alert settings and scheduled evaluation.
3. Add email templates, unsubscribe handling, and delivery observability.
4. Enable for internal/test users, then a small user cohort, then all authenticated users.

### Risks and mitigations
- Risk: Alert jobs become expensive if many saved searches are evaluated frequently.
  - Mitigation: Batch jobs by frequency, index stored criteria where possible, cap saved searches per user, and monitor job duration.
- Risk: Users receive too many emails or duplicate results.
  - Mitigation: Default to weekly, suppress emails with no new results, and track notification history.
- Risk: Saved search criteria become stale as search filters evolve.
  - Mitigation: Version serialized criteria and provide graceful fallback or migration for deprecated filters.
- Risk: Privacy issues from email content or links.
  - Mitigation: Keep email summaries concise, avoid sensitive hidden fields, and require auth for full results.

### Open questions
- What search surfaces and result types should be supported in the first release?
- Does the application already have account-area navigation and email infrastructure to reuse?
- Should “instant” alerts be supported, or only daily/weekly/monthly for launch?
- What is the maximum number of saved searches allowed per user?
- Should users be able to share saved searches with others in a later release?
- What qualifies as a “materially changed” result for alerting?
