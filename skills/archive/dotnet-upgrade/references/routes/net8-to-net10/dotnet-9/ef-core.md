# EF Core 9

**Researched**, date unspecified; WPR-N9-EF-001 through 007. All 12 general/10 Cosmos changes. [EF 9 catalog](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/breaking-changes), [index](index.md).

## Provider and tool alignment

SchedulerDbContext SQL Server and ApplicationDbContext SQLite/OpenIddict had migrations/snapshots, no automatic Migrate calls. Align runtime/providers/Design/Tools/diagnostics and both CLI manifests. Providers generally cannot cross majors. Oracle EF references existed; later removal based on no UseOracle is project-specific.

Sources: [providers](https://learn.microsoft.com/en-us/ef/core/providers/), [migration guide](https://learn.microsoft.com/en-us/aspnet/core/migration/80-to-90?view=aspnetcore-10.0&tabs=visual-studio-code).

## Pending model rejection

**Applies.** EF 9 throws when applying migrations with model/snapshot drift. has-pending-model-changes exists since EF 8. Select the correct context, target and startup, review the real model delta/migration and test disposable SQL/SQLite stores. Never suppress PendingModelChangesWarning.

Sources: [pending model](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/breaking-changes#exception-is-thrown-when-applying-migrations-if-there-are-pending-model-changes), [CLI](https://learn.microsoft.com/en-us/ef/core/cli/dotnet#dotnet-ef-migrations-has-pending-model-changes).

## Migration transaction boundaries

**Applies.** All pending migrations share one locked transaction/rollback, rather than the previous per-migration transactions. EF 10 reverted it. No custom wrapper/suppressTransaction was found. Review SQL and test applicable failure/rollback on disposable stores; no failed rollback was observed in research.

Sources: [transaction change](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/breaking-changes#all-pending-migrations-are-applied-in-a-single-transaction), [application](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/applying).

## Private design assets tooling

**Possibly applies.** SDK 9.0.200+ may fail loading private Design with usual IncludeAssets; AuthServer matched. Reproduce actual tooling before using the Publish=true workaround, which copies the Design DLL into output/publish. Inspect side effects; do not apply a speculative workaround.

Source: [Design not found](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/breaking-changes#microsoftentityframeworkcoredesign-not-found-when-using-ef-tools).

## Transactions converters and query translation

Original negative direct-source assessments:

- Explicit transaction around Migrate throws: no wrapper. [Source](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/breaking-changes#exception-is-thrown-when-applying-migrations-in-an-explicit-transaction).
- Unhex returns nullable byte[]: no call. [Source](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/breaking-changes#ef-functions-unhex-now-returns-byte).
- Compiled models reference converter methods directly: JobRequest converter existed, no compiled model/optimize output. [Source](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/breaking-changes#compiled-models-now-reference-value-converter-methods-directly).
- SqlFunctionExpression validates nullability arity: no custom provider/expression. [Source](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/breaking-changes#sqlfunctionexpressions-nullability-arguments-arity-validated).
- Translated nullable ToString returns empty: calls ordinary C#, not EF projections. [Source](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/breaking-changes#tostring-method-now-returns-empty-string-for-null-instances).

## Framework and compiled query restrictions

- Shared framework dependencies 9.x affect a net8 + EF 9 intermediate, not final net9. [Source](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/breaking-changes#shared-framework-dependencies-were-updated-to-90x).
- Tools drop .NET Framework; all projects net8. [Source](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/breaking-changes#ef-tools-no-longer-support-net-framework-projects).
- EF.Constant/Parameter unsupported in compiled queries; none. [Source](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/breaking-changes#efconstant-and-efparameter-no-longer-work-inside-compiled-queries).
- Some JSON collection identity-resolution queries prohibited; no such mappings/tracking. [Source](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/breaking-changes#some-notrackingwithidentityresolution-queries-are-now-prohibited-for-json-collections).

## Cosmos provider catalog

No Cosmos package/UseCosmos/client, originally all ten not applicable. Preserve discriminator->$type; id no discriminator by default; JSON id maps EF key; sync I/O unsupported; SQL projections return JSON directly; undefined results filtered; incorrect translations throw; HasIndex throws; IncludeRootDiscriminatorInJsonId->HasRootDiscriminatorInJsonId; Newtonsoft 10.0.2->13.0.1. SQLite indexes/direct Newtonsoft are unrelated.

Sources: [Cosmos catalog](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/breaking-changes#azure-cosmos-db-breaking-changes), [HasIndex](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/breaking-changes#hasindex-now-throws-instead-of-being-ignored), [rename](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/breaking-changes#includerootdiscriminatorinjsonid-was-renamed-to-hasrootdiscriminatorinjsonid-after-900-rc2), [Newtonsoft](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/breaking-changes#the-referenced-newtonsoftjson-version-was-updated-from-1002-to-1301).

Verify actual tools/context/snapshots, reviewed SQL and disposable execution/persistence. Research is not shared-schema approval or runtime evidence.
