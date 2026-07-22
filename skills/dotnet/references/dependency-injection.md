# Dependency Injection and Composition

Use for service registration, constructor design, object lifetime, and test seams.

## Core Rules

- Required dependencies must be constructor parameters.
- Do not create production collaborators with `new` inside controllers, services, filters, or handlers.
- Do not use fallback construction such as `dep ?? new RealDependency()`.
- Do not make required dependencies optional with `= null`.
- Keep object graph assembly in the composition root.

## Composition Root

Concrete production construction is allowed in:

- `Program.cs`
- `Startup.cs`
- DI registration extension methods
- Explicit factory/composition code

## Optional Dependencies

If behavior is optional, model it explicitly using one of:

- Default implementation registered in DI
- Null-object implementation
- Factory/provider
- `IEnumerable<T>` for zero-or-more implementations
- Options/configuration object

## Lifetimes

- Do not inject scoped services into singletons.
- Use `IServiceScopeFactory` when singleton/background code needs scoped services.
- Prefer stateless services where possible.
- Dispose resources through DI when DI creates them.

## Constructors

- Keep constructors simple.
- Store injected dependencies only.
- Avoid work, I/O, validation requiring external systems, or object graph assembly in constructors.
- Primary constructors are acceptable when supported and readable.

## Tests

- Tests may directly create the system under test.
- Tests should provide explicit fakes, stubs, mocks, or DI-wired dependencies.
- Do not rely on production constructors secretly creating missing dependencies.
