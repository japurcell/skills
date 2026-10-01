# Extract the Complete Authoring Checklist

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** research/authoring-checklist

## Question

What complete set of audit checks follows from the current official Claude skill authoring best-practices document, including recommendations not singled out in the inbox idea?

Read the full primary document at https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices and follow relevant first-party links when a recommendation requires clarification. Record each distinct recommendation, its source section, conditional applicability, evidence an auditor would inspect, and whether it describes general authoring practice or a Claude-specific mechanism. Capture the retrieval date and distinguish advisory heuristics from requirements. Include descriptions, concision, degrees of freedom, progressive disclosure, reference navigation, workflows, feedback loops, conditional workflows, model testing, and executable-resource guidance where present. Do not decide provider compatibility or impose recommendations on repository skills in this ticket.

Write one findings file in the assigned research directory. Summarize the complete checklist and source gaps in this ticket's Resolution before closing it. The parent maintains the map index.

---

## Resolution

Reviewed the full Claude Platform best-practices page and the linked Skills overview and API code-execution documentation on 2026-10-01. The complete, evidence-oriented checklist is in [findings](../research/authoring-checklist/findings.md).

The source covers concise instructions, appropriate degrees of freedom, intended-model testing, SKILL.md metadata and discovery, naming/descriptions, progressive disclosure and reference navigation, complex and conditional workflows, validation loops, time-sensitive facts and terminology, templates/examples, evaluation-first authoring, real-use and team feedback, navigation observations, file paths/options, executable script errors/constants/utilities/visual analysis/intermediate validation, dependency/runtime assumptions, and MCP tool naming. The closing source checklist repeats earlier sections and does not add separate recommendations.

Qualifications: only the required `SKILL.md` metadata fields and their stated field constraints are format requirements. The 500-line target, three evaluation scenarios, writing conventions, workflow patterns, and testing examples are advice. Most content is conditional on the Skill's task, files, models, or runtime. Claude frontmatter rules, activation/navigation behavior, model names, MCP qualification syntax, and package/runtime behavior are Claude-specific; this research makes no provider-compatibility finding.

Source gaps: the retrieved pages provide no version/update timestamp; no built-in evaluation runner, effectiveness threshold, or standard evaluation harness is specified. Package behavior is surface-dependent: the linked code-execution page clarifies the API sandbox but does not independently verify claude.ai package installation behavior. The findings file records the retrieval date and these limits.
