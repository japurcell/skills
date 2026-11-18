# .NET 10 globalization

**Researched**, **2026-09-23**; WPR-N10-GLOB-001. One entry. [Index](index.md).

## ICU override and runtime culture

**Possibly applies.** CLR_ICU_VERSION_OVERRIDE renamed DOTNET_ICU_VERSION_OVERRIDE. Neither checked in; orchestrator/hosting/secret injection unknown. Rename only an actually used old setting. Image ICU/invariant=false still requires locale-sensitive parsing/formatting tests. Absence of override is not culture proof; ICU does not imply timezone files.

Source: [override](https://learn.microsoft.com/en-us/dotnet/core/compatibility/globalization/10.0/version-override), [timezone lesson](../../../lessons.md#icu-is-not-timezone-data).
