---
name: dotnet
description: Mandatory for all C#/.NET work. DO NOT use when delegating C#/.NET work to a subagent, but you MUST explicitly instruct the subagent to activate the dotnet skill in it's prompt. Always use for any work that touches, creates, modifies, reviews, or is likely to touch `.cs`, `.fs`, `.vb`, `.csproj`, `.fsproj`, `.vbproj`, `.sln`, `Directory.Build.props`, `Directory.Build.targets`, NuGet/package config, ASP.NET Core controllers/APIs, xUnit/NUnit/MSTest tests, EF Core, dependency injection, async/performance code, or any `dotnet` CLI command such as `dotnet build`, `dotnet test`, `dotnet run`, `dotnet restore`, or `dotnet format`. This skill takes precedence over workflow skills such as `code-review`; load `dotnet` first, then run the workflow skill inside the .NET context.
---

# .NET engineering

Inspect project files, framework, language version, nullable settings, analyzers, `.editorconfig` and existing style. Follow conventions unless unsafe or clearly wrong. Apply relevant sections using only supported language and framework features.

## C# defaults

- Use Allman braces and four-space indentation. Prefer file-scoped namespaces. Sort file-top usings with `System.*` first. Remove unused code and imports.
- Explicit visibility first. Name private/internal instance fields `_camelCase`, static fields `s_camelCase`, and thread-static fields `t_camelCase`. Use PascalCase for types, methods, properties, constants and public members, camelCase for parameters and locals.
- Prefer C# keywords, `nameof` for member names, explicit types where `var` obscures meaning.
- Prefer immutable models (`record`, `init`, `required`, `readonly`), positional records for simple DTOs, named records/classes for domain data. Seal internal/private types or make them static unless inheritance is required.
- Reserve interfaces for boundaries, multiple implementations, external dependencies or test seams. Require clear benefit for wrappers.
- Use collection expressions, patterns, switch expressions, ranges, obvious target-typed `new()`, and readable primary constructors matching project style.

## Validation and failures

Enable nullable references where supported. Resolve warnings without blanket `!`. Test with `is null` / `is not null`. Guard public inputs early with `ArgumentNullException.ThrowIfNull`, `ArgumentException.ThrowIfNullOrWhiteSpace`, or `ArgumentOutOfRangeException.ThrowIfNegativeOrZero` for positive inputs.

Throw specific exceptions. Catch `Exception` only where a boundary requires it. Never swallow errors. Rethrow with `throw;`.

## Async and performance

- Suffix async methods with `Async`. Await tasks or queue the work for a background service. Avoid blocking waits (`.Result`, `.Wait()`). Reserve `async void` for event handlers. Use `await using` for async disposal.
- Propagate cancellation through calls and delays. Check `ct.ThrowIfCancellationRequested()` in long loops. Use `Task.WhenAll` for independent concurrent work and `ConfigureAwait(false)` where appropriate in libraries.
- Prefer `Task`. Use `ValueTask` only with measured benefit, frequent synchronous completion and callers that follow its consumption rules.
- Stream large results with `IAsyncEnumerable<T>` and `[EnumeratorCancellation] CancellationToken` unless materialization is required. Stream large HTTP JSON with `GetAsync(..., HttpCompletionOption.ResponseHeadersRead, ct)`, `ReadAsStreamAsync(ct)`, then `JsonSerializer.DeserializeAsync<T>(stream, cancellationToken: ct)`.
- Use `StringBuilder` for repeated appends. Favor readability unless performance is measured or clearly important. On hot paths avoid allocations, costly LINQ and exceptions for normal control flow. Slice transient memory with `Span<T>` or `ReadOnlySpan<T>`. Reuse large buffers/objects with `ArrayPool<T>` or `ObjectPool<T>`. Keep logging structured and quiet.
- Choose arrays for fixed sizes, `List<T>` for appends, `Dictionary<TKey,TValue>` for keyed lookups, `HashSet<T>` for membership, `string.Contains` for substrings and `.Chunk(size)` for simple batching.

## Dependency injection

- Inject required collaborators through mandatory constructor parameters. Constructors only store dependencies. Keep production construction and graph assembly in `Program.cs`, `Startup.cs`, registration extensions, or explicit factories/composition code. Avoid optional null defaults and fallback construction.
- Both high- and low-level modules depend on abstractions. Details implement those contracts. Put contracts and options in the consuming lower-level project. The composition root references it to bind configuration.
- Model optional behavior with registered defaults, null objects, factories/providers, `IEnumerable<T>`, or options.
- Prefer stateless services. Let DI dispose what it creates. Singletons and background workers resolve scoped services inside an `IServiceScopeFactory` scope.
- Tests may construct the subject directly. Supply explicit fakes, stubs, mocks, or DI dependencies.

## ASP.NET Core

- Keep controllers and minimal handlers thin. Put business logic in services. Use async request I/O, including body reads. Avoid wrapping synchronous work in `Task.Run`.
- Set status and headers before the response starts. Return after middleware completes a response.
- Page large collections server-side. Materialize bounded results with `ToListAsync()` or stream `IAsyncEnumerable<T>` to avoid synchronous lazy serialization. Stream large bodies in both directions.
- Read `HttpContext` per request through `IHttpContextAccessor` if needed. Never store the context in fields, access it from parallel threads, or use it after request completion. Copy required values before queuing work.
- Move long CPU-bound or blocking work to a queue, `BackgroundService`, or external worker.
- Prefer `IHttpClientFactory` for outbound calls. Avoid per-request client construction and disposal.
- Use framework binding and validation. Enforce request size limits, explicitly handling `ContentLength is null` when size matters.

## EF Core

- Use async queries. For read-only queries, use `AsNoTracking()` and project needed columns with `Select`. Choose projection or eager loading to avoid lazy N+1 queries. Use `AsSplitQuery()` for collection includes that multiply rows. Index frequent filters and joins.
- Bound results with `Take` or pagination, preferring keyset pagination for large or scrolling datasets. Buffer bounded results with `ToListAsync()` or `ToArrayAsync()`. Stream large results with `AsAsyncEnumerable()` only while the context remains alive.
- Use `SaveChangesAsync()` for unit-of-work updates and `ExecuteUpdateAsync` or `ExecuteDeleteAsync` for bulk changes without loading rows.
- Keep contexts scoped, short-lived, and confined to one concurrent operation. Never store them in singletons. Use scoped services or `IDbContextFactory<T>` for background work. Pool contexts only if their state resets safely.
- Prefer simple mappings and TPH inheritance. Justify TPT on performance-sensitive queries. Consider computed or persisted columns or denormalized read models to avoid repeated expensive calculations.
- Measure before compiling hot repeated queries or very large models, tuning batch sizes, or using provider-specific indexes or query hints.

## Review

Check changes against the applicable sections. Avoid database/network calls in loops. Check for N+1 calls and large results that need paging or streaming.
