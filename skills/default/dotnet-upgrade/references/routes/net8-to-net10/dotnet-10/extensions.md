# Microsoft.Extensions 10

**Researched**, **2026-09-23**; WPR-N10-EXT-001 through 003. All six entries. [Index](index.md).

## Explicit null configuration binding

**Possibly applies.** JSON provider/binder preserves explicit null as a value, not missing key. Original auth/proxy/lifetime bindings, no checked JSON nulls; deployment files unknown. Inspect/test exact nullable/default/array option keys if present. Repository absence is not all-host configuration proof.

Source: [null values](https://learn.microsoft.com/en-us/dotnet/core/compatibility/extensions/10.0/configuration-null-values-preserved).

## Hosted services keyed DI and console JSON

Original not-applicable uses: BackgroundService.ExecuteAsync entirely on background thread (source directly implements IHostedService, not subclass); GetKeyedService(s) AnyKey behavior (no keyed lookup); Console JSON stops duplicate Message (Serilog ExpressionTemplate, not AddJsonConsole/State.Message parser).

Sources: [BackgroundService](https://learn.microsoft.com/en-us/dotnet/core/compatibility/extensions/10.0/backgroundservice-executeasync-task), [AnyKey](https://learn.microsoft.com/en-us/dotnet/core/compatibility/extensions/10.0/getkeyedservice-anykey), [console JSON](https://learn.microsoft.com/en-us/dotnet/core/compatibility/extensions/10.0/console-json-logging-duplicate-messages).

## Logging alias and configuration trimming

ProviderAliasAttribute moves Logging.Abstractions with forwarding; no custom alias. Trim-unsafe configuration annotations removed; no trim/AOT or affected Type-based overload, generic Get/Bind only. Reassess actual packaging, trimming and custom logger consumers.

Sources: [alias](https://learn.microsoft.com/en-us/dotnet/core/compatibility/extensions/10.0/provideraliasattribute-moved-assembly), [binder annotations](https://learn.microsoft.com/en-us/dotnet/core/compatibility/extensions/10.0/dynamically-accessed-members-configuration).
