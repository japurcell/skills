# .NET 10 core libraries

**Researched**, **2026-09-23**; WPR-N10-CORE-001 through 006. All 17 core entries, including Reflection duplicate. Negative assessments are original direct-source only. [Index](index.md).

## AsyncEnumerable extension collision

**Possibly applies.** System.Linq.AsyncEnumerable becomes platform LINQ; ToListAsync returns ValueTask<List<T>> with optional cancellation. Two AuthServer calls could collide with custom extension under implicit usings. Compile actual reference assemblies, make binding unambiguous and verify one enumeration/order/cancellation. Separate unused Services helper and indirect System.Linq.Async references need independent review.

Sources: [AsyncEnumerable](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/asyncenumerable), [API](https://learn.microsoft.com/en-us/dotnet/api/system.linq.asyncenumerable.tolistasync?view=net-10.0).

## W3C trace propagation

**Possibly applies.** Default propagation W3C, outgoing baggage not Correlation-Context, only W3C parent IDs accepted. YARP/no owned propagator does not rule out downstream legacy telemetry. Verify cross-boundary correlation before legacy override. External consumers unverified.

Source: [propagator](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/default-trace-context-propagator).

## Obsoletions sampling intrinsics and streams

- Custom-ID obsolete APIs: SslStream algorithm properties, SystemEvents.EventsThreadShutdown, Rfc2898DeriveBytes constructors, old Queryable.MaxBy/MinBy comparer overloads, XsltSettings.EnableScript. No direct use. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/obsolete-apis).
- ActivitySource CreateActivity/StartActivity PropagationData sampling changes sampled-child flags; no ActivitySource/listener/custom sampler. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/activity-sampling).
- Arm64 SVE nonfaulting loads require mask; no intrinsics. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/sve-nonfaulting-loads-mask-parameter).
- BufferedStream.WriteByte no implicit flush; no usage. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/bufferedstream-writebyte-flush).

## Span overloads math filesystems and trimming

- C# 14 span binding changes concern interpreted expression trees. Latest language and nonce Span existed, but no Expression/Compile(preferInterpretation:true). Compile with actual C# 14. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/csharp-overload-resolution).
- Generic-math shift consistency; no IShiftOperators. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/generic-math).
- Linux DriveInfo.DriveFormat returns filesystem types; no usage. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/driveinfo-driveformat-linux).
- DefaultValueAttribute(Type,string) trimming annotation removed; no affected constructor/trimming. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/defaultvalueattribute-dynamically-accessed-members).

## Inline arrays globbing tar LDAP and MacCatalyst

- InlineArray explicit Size disallowed; no declaration. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/inlinearray-explicit-size-disallowed).
- FilePatternMatch.Stem nonnullable; no API. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/filepatternmatch-stem-nonnullable).
- GnuTar/PaxTar omit atime/ctime by default; no Tar API. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/tar-atime-ctime-default).
- LDAP DirectoryControl parsing stricter; no LDAP, OIDC uses HTTP. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/ldap-directorycontrol-parsing).
- MacCatalyst version normalization; no mobile target/version checks. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/maccatalyst-version-normalization).

## SIGTERM host lifetime and reflection validation

Runtime default SIGTERM termination handler removed. Typical ASP.NET host lifetime needs no second low-level handler. Original ApplicationStopping delay/HostOptions shutdown still requires real signal/grace-period verification.

MakeGenericSignatureType now validates generic type definition; no call. Same catalog entry retained in [Reflection](reflection.md#trimming-annotations-and-signature-validation), not lost as duplicate.

Sources: [SIGTERM](https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/sigterm-signal-handler), [signature validation](https://learn.microsoft.com/en-us/dotnet/core/compatibility/reflection/10/makegeneric-signaturetype-validation). Proposed build/tracing/shutdown checks are not observed outcomes.
