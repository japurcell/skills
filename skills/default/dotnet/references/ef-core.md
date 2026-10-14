# EF Core

Use for EF Core querying, modeling, updates, and DbContext lifetime.

## Querying

- Use async query APIs: `ToListAsync`, `ToArrayAsync`, `SingleAsync`, `AnyAsync`.
- Use `AsNoTracking()` for read-only queries.
- Project only needed columns with `Select`.
- Avoid loading whole entities when DTOs are enough.
- Limit result sets with `Take` or pagination.
- Prefer keyset pagination for large/scrolling datasets.
- Avoid lazy loading; it often causes N+1 queries.
- Use eager loading or projection intentionally.
- Use `AsSplitQuery()` when multiple collection includes would cause cartesian explosion.
- Ensure frequent filters and joins are backed by suitable indexes.

## Buffering and Streaming

- Use `ToListAsync()` or `ToArrayAsync()` for bounded results.
- Use `AsAsyncEnumerable()` for large streamed results.
- Do not stream if the DbContext may be disposed before enumeration completes.

## Updates

- Use `SaveChangesAsync()` for normal unit-of-work updates.
- For bulk updates/deletes, prefer:
  - `ExecuteUpdateAsync`
  - `ExecuteDeleteAsync`
- Do not load many rows just to update/delete them in memory.

## DbContext Lifetime

- Treat `DbContext` as scoped and short-lived.
- Do not share a `DbContext` across threads.
- Do not store `DbContext` in singletons.
- Use `IDbContextFactory<T>` or scoped services for background work.
- Use DbContext pooling only when context state is safe to reset.

## Modeling

- Prefer simple mappings.
- Use computed columns, persisted columns, or denormalized read models when they remove expensive repeated calculations.
- Prefer TPH inheritance by default.
- Avoid TPT for performance-sensitive queries unless justified.

## Advanced Optimization

Use only after measurement:

- Compiled queries for very hot repeated queries.
- Compiled models for very large models.
- Batch size tuning.
- Provider-specific indexes and query hints.
