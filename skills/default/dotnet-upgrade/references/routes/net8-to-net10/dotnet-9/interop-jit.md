# .NET 9 interop and JIT

**Researched**, date unspecified; WPR-N9-INTEROP-001 through 003. All three entries originally not applicable to managed Alpine source; reassess platform/dependencies. [Index](index.md).

## CET Windows apphosts

Windows apphost/singlefilehost CET-compatible by default, constraining native libraries changing thread context. No native/Windows apphost found in original container path. Reassess Windows/IIS independently; no Windows execution proved here.

Source: [CET](https://learn.microsoft.com/en-us/dotnet/core/compatibility/interop/9.0/cet-support).

## Saturating float to integer casts

Float/double casts to integers become saturating. No direct cast found. Fiscal-year Convert.ToInt32 and Excel decimal.TryParse/decimal are distinct. Keep boundary tests, no speculative fix.

Source: [floating-point conversions](https://learn.microsoft.com/en-us/dotnet/core/compatibility/jit/9.0/fp-to-integer).

## Removed SVE APIs

Some SVE intrinsics removed; none found. Build/test actual SDK and numeric boundaries, no CET/SVE configuration needed solely for original Linux target.

Source: [SVE](https://learn.microsoft.com/en-us/dotnet/core/compatibility/jit/9.0/sve-apis).
