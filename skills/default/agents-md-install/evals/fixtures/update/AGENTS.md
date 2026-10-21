# Orchard instructions

Orchard combines a web application and a Python service.

The focused web check is `npm run check-web` from the root. The command spelling may be outdated; package.json owns current script names. Running the focused check does not by itself satisfy the completion requirement below.

Before completing any change, run `npm run verify:all` from the root. The only exception is a change confined to web presentation, as defined in apps/web/AGENTS.md. Web behavior changes, service changes, and shared API contract changes still require the full check, even when only files under apps/web are edited.

Releases require explicit maintainer approval.

Never edit an applied migration. Add a new migration. Use a disposable local database. These service-only rules also appear in docs/database-changes.md.

For public API or consumer changes, follow [API contract](docs/api-contract.md).

For service changes run `python3 -m pytest tests` from services/api. For changes to the public schema, edit schemas/public.json first and then run `npm run generate:client` from the root. Never edit generated/client directly.

Use clear variable names. Write clean code.
