# Risk-based code review for agent workflows

**Experiment closed on 2026-11-18.** General code review keeps its four-reviewer default. The proposed tiers below were evaluated in the [shadow pilot](2026-11-18-review-tiering-pilot.md).

## Starting point at 15:47

Joah Gerstenberg contrasts adding a test with changing a ledger contract. Slides 22 and 23 connect review depth to the cost of being wrong, including money movement, infrastructure, personal data and compliance. Block's public reviewer documents a uniform specialist panel, a coordinator that tries to disprove findings and a judge that revisits discarded findings. These are two distinct decisions a review workflow makes: how broadly to look and how much evidence a comment needs. [Recording at 15:47](https://youtu.be/f6OVURAlYXI?t=947) · [Speaker’s slides](https://joahg.dev/cut-the-noise/) · [Block’s implementation](https://github.com/block/review)

The talk cites Meta's RADAR. Its deployment combined eligibility rules, a risk model, semantic review and deterministic validation, with thresholds calibrated on Meta's own outcomes. The transferable practice here is testing eligibility against repository history before reducing review. [RADAR paper](https://arxiv.org/html/2605.30208v1)

## What prior work establishes

| First-party evidence | Implication for this repository |
| --- | --- |
| Anthropic's managed Code Review offers Quick, Standard, and Deep. An owner selects the organization default or a repository override. Review frequency is a separate setting. [Code Review setup](https://code.claude.com/docs/en/code-review-setup#set-the-default-review-level) | Three depths have a practical precedent. Per-change classification and the checks each tier owes are local design decisions. |
| Anthropic recommends routing when categories are distinguishable with adequate accuracy. It describes parallel reviewers for independent concerns and repeated assessments for different perspectives. [Building effective agents](https://www.anthropic.com/research/building-effective-agents) | Test whether reviewers agree on actual repository changes. Give each additional reviewer a question whose answer can change the outcome. |
| Anthropic's open-source review plugin describes independent instruction, bug, and history passes and filters individual findings by confidence. [Code Review plugin](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-review/README.md) | Use a second pass to challenge consequential findings. The plugin's confidence threshold measures individual reports and supplies no calibrated probability for an entire change. |
| OpenAI's Codex GitHub integration focuses comments on P0/P1 findings and reads scoped repository guidance. Its open-source rubric asks for a concrete affected scenario and records priority, confidence, and an overall verdict separately. [Codex GitHub documentation](https://learn.chatgpt.com/docs/third-party/github) · [Codex review rubric](https://github.com/openai/codex/blob/main/codex-rs/prompts/templates/review/rubric.md) | Select review depth before findings exist. Record urgency and supporting evidence once a defect is found. A quiet comment thread gives little information about which checks actually ran. |
| OpenAI's account of its agent-built repository ties autonomous review to a harness that can reproduce a failure, exercise the application, validate a fix, and surface decisions requiring human judgment. The authors explicitly qualify transfer to other repositories. [Harness engineering](https://openai.com/index/harness-engineering/) | For a changed installation path, ask for the observed result of the affected installation journey. Transferring merge authority would require a separate decision. |

## Where the decision belongs

- The published general review currently delegates correctness, security, tests and general quality unless the user explicitly requests lightweight review. Even lightweight review requires delegation. Above 1,000 changed lines or 15 files, the skill chunks the input. Its 80-point threshold filters individual findings after discovery. Automatic reductions would require changing the explicit four-reviewer rule and its checklist after the pilot. [General review](../../skills/default/code-review/SKILL.md) · [Large-change triage](../../skills/default/code-review/references/large-change-triage.md) · [Five-axis quality criteria](../../skills/default/addy-code-review-and-quality/SKILL.md)
- Put the coverage decision in general review after intake. Pass the resulting assignments to the existing model router, which already distinguishes mechanical, substantive and security work. Choosing a model for a reviewer and choosing which reviewers must participate answer different questions. [Model routing criteria](../../skills/default/subagent-model-router/reference/review-routing.md)
- An explicit biaxis review owes independent standards and spec reports, including its documented missing-spec handling. ExecPlan integration calls that workflow. An explicit adversarial review owes an independent challenge. Preserve those contracts. Use guidance review's literal walkthrough when Markdown changes what an agent will do. [Biaxis](../../skills/default/code-review-biaxis/SKILL.md) · [ExecPlan integration](../../skills/default/execplan-implement/SKILL.md) · [Adversarial review](../../skills/default/adversarial-review/SKILL.md) · [Guidance review](../../skills/default/guidance-review/SKILL.md)

## Proposed review tiers

For every eligible review, capture the base and target or local snapshot, inspect all hunks, identify consumers and state the most consequential plausible failure. Record the tier, decisive hunk, reason, reviewers and evidence gaps. Retain applicable PR intake, scope, standards, spec and finding-verification rules at every tier.

| Depth | Entry criterion and repository example | Required checks |
| --- | --- | --- |
| Mechanical | Positive evidence that commands, instructions, public names and generated behavior are equivalent. Example: spelling in explanatory README prose. | One independent reviewer checks equivalence in context, including readers of changed names or links. Record what establishes equivalence. |
| Behavioral | Changes an observable result with bounded, reversible consequences. Example: a reporting skill changes how it formats a currency amount. | Independent correctness and test reviews trace the normal entry point, a boundary case and relevant assertions against the requirement. Add a specialist for any concern those assignments cannot cover. |
| Elevated | Changes authority, destructive or persistent writes, a shared compatibility contract with broad impact, or the ability of a gate to detect failure. Example: a one-line change allowing an installer to overwrite an existing provider configuration. | Use the existing four roles. Trace affected callers and failure or recovery paths. Challenge the most consequential assumption using independent evidence, such as the installed result from a disposable upgrade with existing configuration. |

Mixed changes take the highest applicable tier. Paths can raise scrutiny. A Markdown suffix, small diff or green CI cannot establish equivalence. An unresolved consumer moves mechanical work to behavioral review. If the remaining uncertainty could conceal an elevated consequence, apply elevated review. Reclassify when new hunks, consumers or evidence change the rationale. If a required reviewer or observation is missing, report the uncovered question and partial coverage. Preserve the current rule on executing checks only when requested. Review existing evidence and distinguish a static inference from an observed failure.

## Three approaches and Astra's critique

A fresh GPT-6.2 Astra reviewer graded each design from 1 to 5 on consequential-defect coverage (40%), reproducibility (20%), fit with the repository (20%) and proportionality (20%). The table retains its scores in that order. Grades express design judgments before evaluation.

| Rank | Design | Scores | Grade | Principal failure and correction |
| --- | --- | --- | --- | --- |
| 1 | Read the diff and classify by behavioral consequence | 4 / 3 / 4 / 5 | 80/100 | A rename looks mechanical until a dynamic consumer tries the old name. Require cited evidence of equivalence and escalate unresolved consumers. |
| 2 | Always dispatch the full panel, then deepen elevated reviews | 5 / 4 / 5 / 1 | 80/100 | Four reviewers can share a mistaken assumption about generated output. Give the deeper pass a falsifiable question and independent evidence. Use as the pilot control. |
| 3 | Choose reviewer sets by path rules, with full review for unknown paths | 2 / 5 / 3 / 3 | 60/100 | Weakening an approval instruction in a familiar Markdown path evades the fallback. Use path matches only to raise the minimum depth. |

Astra broke the tie in favor of behavioral classification because it can give demonstrably routine changes a smaller review. The full-panel approach fits today's contract immediately and provides the fallback if reviewers disagree about risk.

## Adoption decision

The subsequent five-case [shadow pilot](2026-11-18-review-tiering-pilot.md) tested these proposed gates.

Run both approaches independently against identical pinned revisions. Include confirmed historical defects, harmless edits, mixed changes, and plausible low-risk locations containing consequential changes. Have two classifiers assign tiers independently. Have a reviewer unaware of which approach produced a finding adjudicate the union against the evidence, including defects both missed from the historical answer key.

Astra proposed three pilot gates: detect every confirmed consequential defect in the sample, reach at least 90% exact tier agreement, and reduce reviewer effort by at least 25%. Measure agreement over dual-classified changes and effort as total reviewer agent-minutes per matched cohort, including classification and verification. Report counts, false findings and disagreements by tier alongside the percentages. A cohort without confirmed consequential defects cannot establish coverage. The pilot evaluated these criteria.
