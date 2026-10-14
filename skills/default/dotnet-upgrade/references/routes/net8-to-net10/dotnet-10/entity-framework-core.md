# EF Core 10 and Microsoft.Data.Sqlite

**Researched**, **2026-09-23**; WPR-N10-EF-001 through 007. Ten EF and three Sqlite entries. [Catalog](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes), [index](index.md). The original EF 8 baseline also requires [EF 9 review](../dotnet-9/ef-core.md).

## Runtime provider tools and source discrepancy

**Applies.** EF 10 requires SDK/runtime 10, not earlier targets. Align actual providers, Design, Tools, diagnostics, both CLI manifests and OpenIddict groups. No UseOracle was found: choose removal or EF 10 provider 10.23.26301 with driver 23.26.301+. The direct report ADO.NET driver is independent.

Original EF 10 research narrated AuthServer 8.0.4/API 8.0.18 tools, reversing inventory/matrix's AuthServer 8.0.18/API 8.0.4. Preserve this source discrepancy and use actual manifests for future execution; no runtime reconciliation was performed here. Both eventually used matching stage tools.

Sources: [EF10 requirements](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/whatsnew), [providers](https://learn.microsoft.com/en-us/ef/core/providers/), [Oracle](https://www.nuget.org/packages/Oracle.EntityFrameworkCore/10.23.26301).

## SQL application name and pools

**Possibly applies.** Missing Application Name gets anonymous EF/SqlClient version value. Mixed EF/nonEF same database within TransactionScope may separate pools/escalate. No TransactionScope/nonEF scheduler access or explicit name in source. Inspect deployment/integrations; stable explicit name only if needed, test enlistment/pool telemetry.

Source: [Application Name](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes#application-name-is-now-injected-into-the-connection-string).

## Parameterized collection translation

**Possibly applies.** Multiple parameters default changes plans/performance. No owned EF Contains, but third-party OpenIddict scope/resource manager queries may be affected. Inspect actual SQLite SQL for one/multiple scopes and representative auth/load; no guessed SQL override or claimed library-internal proof.

Source: [collections](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes#parameterized-collections-now-use-multiple-parameters-by-default).

## Offset bearing SQLite DateTime

**Possibly applies.** GetDateTime with textual offset now UTC/KindUtc, previously KindLocal even for nonhost offset. OpenIddict creation/expiry/redemption DateTime? TEXT mapping relevant; deployed strings unknown. Inspect representative data and test independently specified instants/status under UTC/nonUTC, not just model shape.

Source: [GetDateTime](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes#using-getdatetime-with-an-offset-now-returns-value-in-utc).

## Multitarget JSON updates and complex types

Original not-applicable assessments:

- Tools require framework for multi-target projects; inherited single TFM, reassess if changed. [Source](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes#ef-tools-now-require-framework-to-be-specified-for-multi-targeted-projects).
- SQL json default on Azure SQL/compatibility170; no UseAzureSql/ToJson/primitive collection. JobData string converter is not EF JSON mapping. [Source](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes#sql-server-json-data-type-used-by-default-on-azure-sql-and-compatibility-level-170).
- ExecuteUpdateAsync regular non-expression lambda; no call/setter expression. [Source](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes#executeupdateasync-now-accepts-a-regular-non-expression-lambda).
- Complex column names uniquified; no mapping. [Source](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes#complex-type-column-names-are-now-uniquified).
- Nested complex column names full path; no mapping. [Source](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes#nested-complex-type-properties-use-full-path-in-column-names).

## Conventions logging and parameter names

IDiscriminatorPropertySetConvention signature changes, IRelationalCommandDiagnosticsLogger adds logCommandText, SQL parameter names simplified. No custom implementation/interceptor/parser/exact SQL assertion found; external SQL snapshots remain unknown.

Sources: [convention](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes#idiscriminatorpropertysetconvention-signature-changed), [logger](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes#irelationalcommanddiagnosticslogger-methods-add-logcommandtext-parameter), [parameters](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes#sql-parameter-names-are-now-simplified).

## SQLite DateTimeOffset and provider gates

GetDateTimeOffset without textual offset assumes UTC; writing DateTimeOffset to REAL writes UTC. Original DateTime? TEXT model does not match; controller DateTimeOffset is not store mapping. Reassess both elsewhere.

Sources: [read](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes#using-getdatetimeoffset-without-an-offset-now-assumes-utc), [REAL write](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes#writing-datetimeoffset-into-real-column-now-writes-in-utc).

Proposed gates: both crossed catalogs, actual restore/build/tools, reviewed scripts before disposable application, app/scope/token persistence, code/refresh flows, timezones and SQL pooling. Historical code-exchange evidence is not proof of refresh-token behavior. No shared database approval from research. [Observed lessons](../../../lessons.md#sqlite-offset-instants-and-redemption).
