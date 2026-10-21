# Contributing

Use pnpm from the repository root for JavaScript work. Do not connect to production systems during development or validation.

For changes under apps/web, run `pnpm --filter web test` and `pnpm --filter web lint` from the root. Web controls must support keyboard navigation and retain visible focus. Use the existing accessible-control examples when the source checkout is available.

For changes under services/api, run `python3 -m pytest tests` from services/api. Run the service tests before completing service changes. Do not apply migrations to shared environments as a local test.

For changes to shared public API contracts or their consumers, follow [API contract](docs/api-contract.md). For service schema or migration changes, follow [Database changes](docs/database-changes.md).
