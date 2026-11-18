# Shadow pilot of risk-based code review

**Experiment closed on 2026-11-18. General code review retains the four-reviewer default.** The candidate found both known consequential defects. Tier agreement was 80% and the candidate consumed 6.90 reviewer agent-minutes against 2.95 for the control. Two of the three adoption criteria failed.

## Cases and scoring

Both arms received the same complete tree-to-tree diffs, changed target files, target path manifest and access to additional files at the pinned target. Reviewers worked in fresh contexts with instructions to avoid history, current source and other reviewers' results. Blinding relied on instructions within a shared workspace. Each review role handled its assigned cases as a batch. Reviewers recorded UTC start and end times around their work.

| Case | Base | Target | Change under review |
| --- | --- | --- | --- |
| A | `97c22ecd` | `2829cf14` | One prose edit in the Windows notification run guide. |
| B | `9f60f446` | `82a45ef6` | One-line regression replay in PRD skill metadata. The original defect occurred during a larger forward change. Reversing its one-line correction reproduces the actual defective tree while isolating the edit. |
| C | `0359ab63` | `af277102` | Wage-input handling in a reporting skill, README and evaluation. |
| D | `211b113e` | `49a4ee2d` | Scheduler preflight event handling and associated tests. |
| E | `378f49c4` | `bc1e6596` | Three edits to investigation scope and references in the backlog. |

The consequential answer key was fixed before collecting findings. B causes the repository's YAML parser to reject the skill metadata. Parsing the historical introduction's parent and its correction succeeded. D accepts setup after EOF discards buffered trailing notification bytes following a valid reply. Historical correction `2470dac6` records the public preflight regression and adds a test. An additional bounded defect in E is a newly required context link whose destination is absent from the pinned tree. Cases A and C have no preselected consequential defect. The pilot makes no claim that the answer key exhausts the defects.

The agreed thresholds were full detection of the known consequential defects, at least 90% exact agreement between two classifiers and at least 25% lower total reviewer agent-minutes. Each case contributes one agreement vote. Disagreement routes to the higher tier. Agent time includes classification and finding verification. The comparison excludes queue delays, coordinator setup and the shared outcome adjudication. Cohort selection deliberately includes known defects and provides no estimate of their frequency in normal work.

## Routing observations

| Case | Classifier 1 | Classifier 2 | Route used | Decisive evidence |
| --- | --- | --- | --- | --- |
| A | Mechanical | Mechanical | Mechanical | Spacing typo in prose, identical commands and timing. |
| B | Elevated | Behavioral | Elevated | Both recognized broken metadata. One escalated because host isolation was unverified. The other bounded the effect to the edited skill. |
| C | Behavioral | Behavioral | Behavioral | A wage-only follow-up changes report generation at closeout. |
| D | Elevated | Elevated | Elevated | Stream acceptance determines preflight readiness. |
| E | Behavioral | Behavioral | Behavioral | Instructions change the scope and dependencies of future investigations. |

Agreement was 4/5 (80%). Each disagreement moves this small sample by 20 percentage points. Both classifications for B excluded mechanical review. Distinguishing a single rejected skill from a failure of catalog discovery requires evidence about the consuming loader.

The control assigned correctness, security, tests and general quality to all five cases. The candidate assigned correctness/equivalence to A-E, tests to B-E, and security and general quality to B and D. Neither classifier's findings were forwarded. The four-role control ran as a local-diff review, batched by role under the host's concurrency limit. Fresh verifier assignments checked each arm's deduplicated candidates against the pinned source and finding threshold before common adjudication. The prompts reproduced role responsibilities in a controlled experiment. This was a comparison of review coverage in the shared agent host, without exercising the published skill's invocation, model router or PR integration end to end.

## Findings after blinded adjudication

| Case | Control | Tiered | Confirmed findings |
| --- | ---: | ---: | --- |
| A | 0 | 0 | Both verifiers dropped the real but inconsequential spacing typo. |
| B | 1 | 1 | The changed description fails YAML parsing and the installer copies it unchanged. Both arms found the isolated replay defect. |
| C | 1 | 1 | The evaluation explicitly asks for a report, so a broken automatic-closeout trigger could pass it. |
| D | 6 | 5 | Both found the preflight false pass at EOF, timing-dependent handling of trailing rows, receipt drift from optional notices, timestamp overflow bypassing the failure receipt, and loss of recorded observations after invalid JSON. The control also found that failure in just one of two cells satisfies the negative test. |
| E | 1 | 1 | The newly required source cannot be retrieved at the target revision. |

An adjudicator blinded to review-arm identity validated all nine distinct reportable findings and rejected the typo as immaterial. By selected tier, mechanical yielded 0/0 reportable findings (control/candidate), behavioral 2/2, and elevated 7/6. Neither arm retained any false finding. The separate D test assertion can still pass if one cell wrongly accepts the duplicate. Detecting the stream issue alone earns no credit for detecting that assertion weakness. Both arms found the consequential defect on the forward D commit and the consequential B replay. This is 2/2 on the prespecified key, with one confirmed consequential forward case.

## Measured reviewer effort

Each entry gives elapsed seconds between the assignment's first and last clock observations. Overlapping assignments count separately. The common adjudication is excluded from both arms.

| Assignment | Control seconds | Tiered seconds |
| --- | ---: | ---: |
| Independent classifiers | 0 | 40 + 37 |
| Correctness and equivalence | 43 | 89 |
| Security | 22 | 60 |
| Tests | 39 | 94 |
| General quality | 47 | 66 |
| Finding verification | 26 | 28 |
| **Total** | **177** | **414** |

The candidate used 237 additional seconds, or 134% more reviewer time. Removing both classifier times as a sensitivity check still leaves 337 seconds. Reviewer-case assignments fell from 20 to 13, but fewer assignments did not translate to less effort. Candidate reviewers spent longer on the elevated cases, including a subprocess check of D. Per-case duration was unavailable because assignments were batched. These are agent-minutes from one run, not token costs or predicted production latency.

**Decision.** Keep the full panel. The one consequential defect both routes found on an actual forward change and the isolated replay support further study of detection. They do not establish general recall. If the policy is revisited, define the evidence that establishes a loader failure's scope and compare matched verification work on a larger held-out cohort, timed per case. Counting assignments alone would have reversed the effort conclusion here.
