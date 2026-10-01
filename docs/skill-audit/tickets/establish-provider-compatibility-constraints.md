# Establish Provider Compatibility Constraints

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** research/provider-compatibility

## Question

Which current, documented Codex, GitHub Copilot, and Gemini skill contracts constrain adapting Claude's skill-authoring recommendations to this repository?

Use official documentation and first-party source where needed. Compare discovery and installation paths, frontmatter and invocation controls, description and body loading, reference navigation, scripts and resources, interaction and permissions, and available skill evaluation mechanisms. Separate client behavior from model behavior. Distinguish Copilot surfaces where contracts differ. Identify whether OpenAI-only behavioral evaluation covers each surface. Mark unverified behavior and do not invent OpenAI support inside a client that does not document it.

Include retrieval dates, version or surface qualifications, direct citations, and concrete incompatibilities or adaptation considerations. Do not select the human's model matrix, scope, or adoption policy. The requested model set is 5.6, 6, and 6.1 Sol; 5.6 and 6 Luna; Astra; and Terra. Verify exact IDs and support where evidence permits, and mark gaps rather than substituting models. Inspect available local OpenAI documentation or configured capabilities where applicable, then verify unresolved Codex claims against official OpenAI documentation.

Write one findings file in the assigned research directory. Summarize constraints and gaps in this ticket's Resolution before closing it. The parent maintains the map index.

---

## Resolution

- **Constraints:** Core metadata can be shared, but invocation, permission, discovery precedence, and resource-loading behavior are provider/client-specific. Use conservative names and descriptions, explicit resource links, and validate each target surface independently. Codex behavioral evals cover Codex runs only; they do not substitute for Copilot or Gemini validation.
- **Gaps:** No local Copilot/Gemini runtime was available. Gemini Code Assist IDE skill support was not established. Exact Codex CLI aliases/account availability remain unverified for GPT-5.6 Sol, GPT-5.6 Luna, and Terra; no GPT-6 Terra model was established. Do not infer native Codex filesystem-skill behavior from Responses API Skills support. No runtime behavior or cross-provider model behavior is claimed.
- **Findings:** [Provider skill compatibility findings](../research/provider-compatibility/findings.md), retrieved 2026-10-01.

The documented-contract comparison is complete to the evidence gathered. Surface and model gaps are recorded above and in the findings; they are not claims of support.
