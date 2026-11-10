# Report Writing

## Weekly report

- **Fields:** Use `Reporting Period` (`MM/DD-MM/DD`), `Summary Of Work Completed`, and `Work In Progress`. No visible field limits were identified. Omit the submitter's personal name from report content.
- **Example:** Use [example-report.md](../../assets/example-report.md) as a style illustration only. It demonstrates STAR, but is neither evidence for accomplishments nor an exhaustive scope or accomplishment inventory. This note governs grouping and headline format.
- **Voice and length:** Write first-person, plain-English bullets. Each accomplishment contains 40-70 whitespace-separated words, including its bold action headline and excluding Markdown list/bold markers, parent application labels, and its terminal reader-facing citation parentheses. Count the narrative and headline as written; do not count a citation such as `(PR #13)` toward the word range.
- **Headlines and grouping:** A standalone application bullet uses `**<application name> - <Action>.**`; within a group, use `**<Action>.**` without repeating the application name. Use action-only headlines for non-application accomplishments. Within each report section, group multiple accomplishments for the same primary application under `- **<application name>**` with accomplishment sub-bullets. Keep singleton and non-application accomplishments as ordinary bullets. For multi-application work, choose one primary application for grouping, retain the other names in the paragraph, and never duplicate the accomplishment.
- **Action and STAR:** An `<Action>` headline is required in `Summary Of Work Completed`, but may be omitted in `Work In Progress` if the action is not yet fully defined or implemented. Follow the headline with STAR: situation, task, action, result. Lead with the customer or operational problem, then the objective, the employee's intervention, and the outcome.
- **Application identity:** Identify the application through its group label or standalone headline. A report name, feature name, or acronym is not a substitute for the application name.
- **Substance and evidence:** Preserve technical substance and meaningful metrics while compressing. Explain complexity through the intervention, not self-praise. Keep caveats about evidence quality or availability, and coverage gaps, out of the narrative. Label estimates and distinguish them from measured outcomes or realized budget savings; keep calculation details out of the narrative.
- **Reader-facing references:** Put a relevant pull request, issue, or commit reference in parentheses immediately after the narrative paragraph it supports, inside the copy-ready field text, for example `... triage. (PR #13)`, `... practices. (commits 16b1cf93 and 40747416)`, or `... set. (PR #542)`. Give each paragraph its own terminal citation; do not put reader-facing references in a separate list, grouped block, or field footer.
- **Internal provenance:** Keep session IDs, local paths, full source proofs, and evidence caveats outside copy-ready field text, such as in the separate source/provenance record. A reader-facing PR, issue, or commit reference is not a substitute for internal claim-to-source attribution.
- **Review validation:** Determine copy-field membership from the actual opening and closing Markdown fence state, not line appearance or position alone.

### Weekly report example

```markdown
# Weekly Status Report 10/29/2026 - 11/05/2026

## Reporting Period

10/29-11/05

## Summary Of Work Completed

- **WorkPlan Reports - Retired the stale service-worker shell path.** A cached Angular service worker could bypass the server-rendered `_Host.cshtml` and serve an unprocessed shell. I removed that worker while retaining the report-export Web Worker, and the session records 132 passing targeted tests on the implementation branch. Deployment, CSP behavior, and authenticated real-host end-to-end results were not verified. (commit d89f4d9)
- **R6TEA - Prepared Release 1.0.9 changes.** The release branch needed updates across registration, layout, delete-label behavior, tests, and archived planning. I committed the changes across ten files and opened the release pull request. The session did not rerun tests or formatting; its commit message reports 221 passing tests, so I treat that result as previously reported rather than newly verified. (PR #210)
- **National BMP Program - Added a Windows-compatible frontend test launcher.** Frontend tests needed to handle Windows namespace-prefixed paths without losing Node runtime arguments. I added path normalization, fallback handling, signal forwarding, and test-script wiring, plus focused documentation. The recorded session reports all checks and tests passing; wider CI or deployment outcomes were not established. (commits 53572b72 and 826522c8)
- **notify-app - Pushed a WSLg validation and Preview-layout fix.** The feature branch needed a Preview layout adjustment alongside continued WSLg validation. I pushed commit a06fe4a to the branch and recorded a clean working tree, making the change available for subsequent checks. Desktop interaction and sound-quality verification remained incomplete, so I did not describe the change as fully validated. (commit a06fe4a)
- **weekly-report - Added repeatable offline evidence tooling.** Report preparation needed an auditable way to inventory inputs and reconcile date-scoped evidence. I committed inventory and reconciliation tooling and hardened checkpoint and evidence handling, supporting repeatable offline collection without editing the frozen source exports. These are tooling changes, not evidence that any particular report was submitted. (commits f62997ed and 3547dd9)
- **Agent tooling - Added backlog-management skills.** The agent workspace needed a consistent way to maintain actionable backlog entries. I committed reusable todo-management and todo-refinement skills for adding, completing, and clarifying backlog items. This records delivery of the tooling change; no usage metrics or operational impact were available. (commit 3bb86613)

## Work In Progress

- **WorkPlan Reports**
  - **Complete acceptance of the .NET 10 upgrade.** The upgrade pull request remained open at the cutoff. The session reports both SonarQube findings fixed, but three end-to-end failures remained because Oracle test data or access was unavailable; Jenkins/Sonar permissions and an authorized verifier were also still needed. Full acceptance was therefore not established. (PR #181)
  - **Verify the service-worker change on the real host.** The implementation session reported 132 targeted tests passing, but authenticated real-host end-to-end behavior and CSP effects were not verified. I left deployment and those checks open rather than treating the implementation-branch result as production validation. (commit d89f4d9)
- **R6TEA - Verify the release and scanner configuration.** Release 1.0.9 remained open for review, and its latest session did not rerun tests or formatting. Separately, a Gemini session left `.betterleaksignore` untracked and listed CI verification as its next step; no later validation was retained. Neither outcome was confirmed complete by the cutoff. (PR #210)
- **National BMP Program - Finish Sonar/Jenkins remediation verification.** The remediation plans were archived with verification gaps preserved and commit 3e84688c was created locally, but the session says the changes were not pushed. I left external validation and closure of those gaps in progress rather than reporting the local commit as a delivered fix. (commit 3e84688c)
- **notify-app - Complete remaining desktop behavior checks.** The last reviewed record reported keyboard, stack/Undo, empty-state, and normal-window focus checks as passing. Pending-alert idle behavior, audible silence, and an unexplained playback-count increase were unverified; output-device checks were skipped, and no later completion evidence was retained.
- **Symbols - Diagnose monthly category-report totals.** The category report appeared to include the full order instead of only items in the selected category, so I opened an issue to track investigation. The issue remained open; no code fix was evidenced, and the parallel Smokey category case could not be verified. (issue #543)
- **Agent tooling - Resolve qualification-package prerequisites.** The last reviewed package-check record showed only 97 of 99 available inputs matching, with required session B missing and a package-size mismatch. No verification, checksums, or archive were produced in that record; no later completion evidence was retained, so qualification was not reported complete.

Source and coverage notes are in [sources.md](sources.md).
```

## Performance report

- Start with `# FY2026 Accomplishments`, followed by official element and criterion headings.
- Write first-person, plain-English bullets. Each contains **40-70 words including its bold action headline and trailing unique, stable ID**. Count whitespace-separated words, excluding Markdown list/bold markers and parent application labels; use the same ID in both documents.
- For standalone application accomplishments, use `**<application name> - <Action>.**`. Within an application group, use `**<Action>.**` without repeating the application name. Use action-only headlines for non-application accomplishments too. Put the stable ID after the paragraph as `(A1)`, not in the headline.
- Within each official criterion, group multiple accomplishments for the same primary application under `- **<application name>**` with accomplishment sub-bullets. Treat Mission Results Oriented's unlettered section as one criterion. Keep singleton and non-application accomplishments as ordinary bullets. For multi-application work, choose one primary application for grouping, retain the other names in the paragraph, and never duplicate the accomplishment.
- Follow the headline with **STAR: situation, task, action, result**. Lead with the customer or operational problem, then the objective, the employee's intervention, and the outcome.
- Identify the application through its group label or standalone headline. A report name, feature name, or acronym is not a substitute for the application name.
- Preserve technical substance, meaningful metrics, and concrete criterion-relevant actions while compressing. Explain complexity through the intervention, not self-praise.
- Let actions and results manifest the criteria. Omit explicit alignment declarations such as "This supports the criterion."
- Keep event dates, citations, source/evidence commentary, caveats about evidence quality or availability, and coverage gaps in the matrix, not the narrative.
- Attribute the employee's actual role separately from team outcomes. Credit collaborators where relevant; do not imply sole ownership of collaborative work.
- Label estimates and distinguish them from measured outcomes or realized budget savings; keep calculation details in the matrix.

### Performance report examples

```markdown
- **WorkPlan Reports - Made email failures visible while protecting personal information.** Scheduled-report email failures needed reliable retry handling without exposing personal information in scheduler dashboards. I updated SMTP configuration and relay settings, propagated failures to Hangfire, replaced sensitive dashboard messages, and added privacy tests while retaining backend diagnostic logging. Failed deliveries now reach scheduler retry handling, and dashboard error messages protect personal information rather than storing sensitive exception details. (A3)

- **Symbols.gov**
  - **Modernized the platform and eliminated critical package vulnerabilities.** Symbols.gov needed a supported, secure platform for public wildfire-prevention orders and payments. I directed an AI-assisted .NET 10 migration across 21 projects, resolved framework and database compatibility issues, and hardened dependencies. The upgrade eliminated five critical transitive vulnerabilities and expanded passing tests to 1,655. Completion in five hours avoided an estimated 87 engineering hours. (A6)

  - **Converted scan findings into targeted security work.** Public ordering and payment services needed concrete checks of their security controls. I used production and staging scans of Symbols.gov to identify HSTS header and input-restriction issues, then pursued follow-up work including Pay.gov acceptance checks and access-control hardening. The findings focused remediation on transaction integrity and exposed control weaknesses rather than relying on assumed protection. (A15)

  - **Integrated security safeguards into shared carts.** Cart sharing needed to protect tokens and prevent repeated-send abuse or lost uses during failed restoration. I implemented hashed tokens, database reservations, throttle leases, compensation, cleanup, and guest controls with tests. Integrating those safeguards established a controlled sharing lifecycle that protects access to cart snapshots and handles failures explicitly. (A24)

- **Enterprise CIAO and Quarters - Strengthened dependency and pipeline controls.** Vulnerable dependencies and missing pipeline checks required targeted maintenance across government applications. I integrated container and JavaScript-package updates for Enterprise CIAO, added Quarters security scanning and corrected its build pinning, and consolidated GP Huckleberry dependency fixes. These changes placed concrete remediation and verification controls into the affected code and build workflows. (A29)
```
