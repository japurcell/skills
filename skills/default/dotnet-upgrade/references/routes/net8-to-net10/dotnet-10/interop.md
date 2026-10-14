# .NET 10 interop

**Researched**, **2026-09-23**; WPR-N10-INTEROP-001. All three entries, originally not applicable to managed multifile Linux publish. [Index](index.md).

## COM and native library loading

- IDispatchEx COM object cast to IReflect fails; no COM/activation/interfaces. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/interop/10.0/idispatchex-ireflect-cast).
- Single-file apps no longer search executable directory for native libraries by default; no PublishSingleFile/NativeAOT/native loader configuration. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/interop/10.0/native-library-search).
- DllImportSearchPath.AssemblyDirectory only searches assembly directory; no DllImport/LibraryImport/DefaultDllImportSearchPaths/NativeLibrary. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/interop/10.0/search-assembly-directory).

Reassess each platform/native dependency. Direct source absence does not certify transitive native loading.
