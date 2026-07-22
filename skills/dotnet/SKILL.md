---
name: dotnet
description: Use for writing, refactoring, or reviewing C#/.NET code, including ASP.NET Core, EF Core, DI, async, and performance-sensitive code.
---

# .NET / C# Engineering

Write clear, safe, idiomatic C# that matches the project’s target framework and style.

## First Steps

1. Check `.csproj`, `.editorconfig`, analyzers, nullable settings, and existing style.
2. Follow project conventions unless they are unsafe or clearly wrong.
3. Do not introduce preview/new language features unless the project already supports them.
4. Prefer simple code over clever code.
5. Read only the extra references relevant to the task.

## Extra References

- ASP.NET Core web apps/APIs: `references/aspnet-core.md`
- EF Core queries/models/updates: `references/ef-core.md`
- DI, constructors, composition root, test seams: `references/dependency-injection.md`
- Async, streaming, hot paths, allocation concerns: `references/async-performance.md`

## Core C# Rules

### Formatting and Naming

Use these defaults when the project has no stronger convention:

- Use Allman braces and 4 spaces.
- Put `using` directives at file top, sorted with `System.*` first.
- Prefer file-scoped namespaces.
- Make visibility explicit and first: `public sealed class Foo`.
- Use `_camelCase` for private/internal instance fields.
- Use `s_camelCase` for static fields and `t_camelCase` for thread-static fields.
- Use `PascalCase` for types, methods, properties, constants, and public members.
- Use `camelCase` for parameters and locals.
- Prefer C# keywords: `string`, `int`, `bool`.
- Use `nameof(...)` instead of hard-coded member names.
- Remove unused code and unused `using` directives.

### Types and Design

- Prefer immutable models: `record`, `init`, `required`, `readonly` where useful.
- Use positional records for simple DTOs.
- Use `record`/class with named members instead of domain tuples.
- Mark internal/private types `sealed` or `static` unless inheritance is required.
- Add interfaces only for real boundaries, multiple implementations, external dependencies, or useful test seams.
- Do not wrap an existing abstraction without a clear benefit.
- Prefer explicit types when `var` would hide meaning.

### Modern C#

Use modern syntax only when supported by the project:

- Collection expressions: `[]`
- Pattern matching and switch expressions
- Target-typed `new()` when the left-side type is obvious
- Range/slice syntax: `text[..^4]`
- Primary constructors when they improve clarity and match project style

### Nulls, Validation, and Exceptions

- Enable and respect nullable reference types when available.
- Do not use blanket null-forgiving `!`.
- Use `is null` / `is not null`.
- Validate public inputs early:
  - `ArgumentNullException.ThrowIfNull(value)`
  - `ArgumentException.ThrowIfNullOrWhiteSpace(text)`
  - `ArgumentOutOfRangeException.ThrowIfNegativeOrZero(number)` when positive is required
- Throw precise exceptions.
- Do not catch base `Exception` unless required at a boundary.
- Do not swallow errors.
- Rethrow with `throw;`, not `throw ex;`.

### Async Basics

- Async methods end with `Async`.
- Prefer `Task` over `ValueTask` unless a measured hot path often completes synchronously.
- Await tasks unless intentionally handing work to a safe background mechanism.
- Avoid `.Result`, `.Wait()`, and sync-over-async.
- Pass `CancellationToken` through async calls.
- Use `await using` for async disposables.

### General Performance

- Avoid database/network calls inside loops.
- Do not concatenate strings in loops; use `StringBuilder`.
- Stream large payloads instead of buffering into `string` or `byte[]`.
- Avoid LINQ in measured hot paths when allocations matter.
- Prefer readable code unless performance is measured or clearly important.

## Review Checklist

- [ ] Code matches project target framework, language version, and style.
- [ ] Nullable warnings are handled correctly.
- [ ] Async code is awaited, cancellable, and named `Async`.
- [ ] No `.Result`, `.Wait()`, `async void` except event handlers, or unsafe fire-and-forget.
- [ ] Exceptions preserve context with `throw;`.
- [ ] DTOs/domain data are named immutable types where appropriate.
- [ ] No unnecessary interfaces, wrappers, or abstractions.
- [ ] No N+1 database/service calls.
- [ ] Large payloads/results are paged or streamed.
