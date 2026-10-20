# Repository workflow

- Published skills live in `skills/default/` and optional `skills/forest-service/`; `.agents/skills/` holds repository-local workflows.
- Canonical custom agents live in `agents/`. Canonical hook renderers live in `hooks/`; provider directories contain deployment artifacts.
- Keep README examples aligned with source and installer behavior. Exclude sibling `*-workspace/` benchmark output from source searches and commits.
- Brain notes hold durable current guidance. Task-specific status belongs in the active plan; retain ADRs as decisions, clearly marking superseded ones.
- Repository changes do not update installed copies. Install only when authorized; validate installers in disposable destinations.
- Check source versus installed versions before diagnosing runtime behavior.

Evidence: repository layout, `scripts/install.sh`, `scripts/install.ps1`, and `docs/adr/0004-generated-provider-hooks.md`, checked 2026-10-20. Recheck when ownership or installation changes.
