# .NET 10 reflection

**Researched**, **2026-09-23**; WPR-N10-REF-001. Two entries originally not applicable; no trimmed build tested. [Index](index.md).

## Trimming annotations and signature validation

InvokeMember/FindMembers/DeclaredMembers annotations more restrictive; no IReflect implementation/TypeInfo derivation/affected call. Test-only GetMethod and no trimming/AOT are different.

MakeGenericSignatureType validates generic type definition; no calls. Same retained item appears in [core](core-libraries.md#sigterm-host-lifetime-and-reflection-validation), WPR-N10-CORE-006; duplicate navigation does not discard semantics.

Sources: [annotations](https://learn.microsoft.com/en-us/dotnet/core/compatibility/reflection/10/ireflect-damt-annotations), [signature](https://learn.microsoft.com/en-us/dotnet/core/compatibility/reflection/10/makegeneric-signaturetype-validation).
