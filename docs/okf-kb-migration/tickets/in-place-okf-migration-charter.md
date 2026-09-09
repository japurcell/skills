# In-Place OKF Migration Charter

**Type:** grilling
**Status:** closed
**Blocked By:** none
**Research Dir:** N/A

## Question

What source-of-truth, loading, authoring, validation, and provider boundaries govern the corrected migration after rejecting the generated sidecar and prompt-time selector architecture?

---

<!-- Resolution will be appended here -->

## Resolution

The user corrected the migration charter after identifying a duplicate-context flaw in the closed sidecar design:

- Migrate the existing canonical documents under `.agents/instructions/` and `.agents/memory/` in place to OKF format. Do not generate a second `.agents/okf/` knowledge copy.
- Preserve the established agent loading flow: `AGENTS.md` directs every coding agent to `.agents/memory/INDEX.md`, which progressively routes to the relevant canonical documents.
- Do not add a prompt-time selector, context-injection extension, provider runtime, legacy/OKF fallback path, qualification state, or provider promotion ladder. Those mechanisms would load knowledge a second time after the normal `AGENTS.md` → `INDEX.md` path.
- Add a repository skill that teaches agents how to create and maintain an OKF document in the canonical tree.
- Add an OKF linter as a blocking validation hook for both GitHub Copilot CLI and Gemini CLI. The hook validates authored documents; it does not inject knowledge into prompts or replace the existing source-ingest workflow.
- Keep implementation outside this planning map. Re-establish the remaining frontier around the exact in-place document contract, authoring-skill contract, linter and hook contract, and dependency-ordered migration proof.

All earlier tickets in this map are obsolete because they were resolved under the rejected sidecar-and-selector charter. Their local and external research may be reused as evidence, but none of their recorded design decisions remains authoritative.
