# Maintenance and evaluation

The companion's canonical source is `../maintain-verification-skill/`. Keep it as a separate bundle; generation copies the available complete bundle into the recipient project, including provider metadata. Preserve manual-only invocation controls when changing setup guidance.

Use `evals/evals.json` for fresh setup, existing-setup reconciliation, and missing-companion cases. Run each case in a disposable recipient project, with the generator and companion staged outside that project. For the missing-source case expose only the generator. Compare revisions against an immutable old-skill snapshot and retain transcripts and generated files separately.

For a minimal CLI fixture, provide an executable greeting command with a default name, a README describing usage, and an AGENTS.md instruction to preserve greeting compatibility. Inspect the generated skill and run its journey through cleanup. Compare every copied companion file with its source, read back the root rule, and confirm the original instruction survives. Repeat generation to check rule deduplication and unchanged identical companion files. For local customizations, verify reconciliation preserves their obligations.

Run the repository skill-source validator. Distinguish manual procedure checks from live agent evaluations; neither source validation nor a successful copy alone proves the generator follows its instructions.
