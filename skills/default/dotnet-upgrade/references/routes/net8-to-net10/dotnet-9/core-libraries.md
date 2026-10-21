# .NET 9 core libraries

**Researched**, date unspecified; WPR-N9-CORE-001 through 007. All 20 catalog entries retained. "Absent" means historical direct-source search, not generic exemption or dependency certification. [Index](index.md).

## Excel ZIP metadata

**Possibly applies.** CompressionLevel changes ZIP central-directory flags for CreateEntry/System.IO.Packaging. SpreadCheetah/Sylvan workbook paths, including SmallestSize, may use them; no owned CreateEntry/CreatePart found. Verify XLSX/XLSB opening, worksheets/styles/values and ZIP validity before changing compression.

Source: [compression flags](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/compressionlevel-bits).

## Out of band transitive packages

**Possibly applies.** Some OOB packages change versions/TFMs. No listed direct IDs; Microsoft.Data.SqlClient is not System.Data.SqlClient. Inspect restored transitives; do not add/update packages merely because the catalog lists them.

Source: [OOB packages](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/oob-packages).

## Source binding and obsoletions

- UnsafeAccessor non-open-generic support altered; no use. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/unsafeaccessor-generics).
- Custom-ID obsoletions: AuthenticationManager, ServicePointManager, Thread.VolatileRead/Write, listed AdvSimd, hash-algorithm Assembly.LoadFrom and X509 constructors. None directly called; ASP.NET OIDC is not AuthenticationManager. No blanket suppression. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/obsolete-apis-with-custom-diagnostics).
- StringValues overload ambiguity in Join/Concat, Path.Combine/Join, StringBuilder.AppendJoin. FormCollection used StringValues but not affected expanded params calls. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/ambiguous-overload).
- C# 13 params-span preference: existing calls used collections/enumerables, no affected expression-tree call. Actual compilation is definitive. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/params-overloads).

## Numeric reader reflection and inline array changes

- BigInteger maximum length changes; no usage. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/biginteger-limit).
- BinaryReader.ReadString malformed-sequence result changes; no BinaryReader (Excel uses StreamReader/XML). [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/binaryreader).
- Array Type creation for System.Void changes; no void MakeArrayType. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/type-instance).
- InlineArray default Equals/GetHashCode changes; no declaration. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/inlinearrayattribute).
- Inline-array struct size limit changes; no declaration. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/inlinearray-size).
- EnumConverter validates registered types; no usage. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/enumconverter).

## DI counters globbing and language specific changes

- FromKeyedServices no longer injects unkeyed services; no keyed registrations/attributes. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/non-keyed-params).
- IncrementingPollingCounter initial callback asynchronous; no counter/listener. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/async-callback).
- InMemoryDirectoryInfo prepends rootDir; no Matcher/globbing use. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/inmemorydirinfo-prepends-rootdir).
- Integer TimeSpan.From overload ambiguity is F#-specific; all projects C#. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/timespan-from-overloads).
- RuntimeHelpers.GetSubArray returns source runtime array type; no direct/covariant slicing, ranges were strings. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/getsubarray-return).

## Strings environment and ZIP encoding

- Trim params ReadOnlySpan overloads removed. Single-character BOM TrimStart still binds char[] in GA; no span args. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/string-trim).
- Empty environment-variable semantics change SetEnvironmentVariable/ProcessStartInfo.Environment; none used. Distinct from runtime precedence. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/empty-env-variable).
- ZipArchiveEntry names/comments honor UTF8 flag. Default encoding/standard OpenXML names, no conflicting entryNameEncoding. Reassess legacy archives. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/9.0/ziparchiveentry-encoding).

## Globalization and area verification

No separate .NET 9 Globalization category. Alpine ICU/invariant=false and environment precedence are [deployment checks](containers-deployment.md); business parsing used InvariantCulture. Compile all projects under latest language, test workbooks, inspect OOB transitives and actual image culture. Proposed checks are not results.
