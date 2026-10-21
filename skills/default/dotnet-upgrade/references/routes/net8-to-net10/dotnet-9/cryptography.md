# .NET 9 cryptography

**Researched**, date unspecified; WPR-N9-CRYPTO-001 through 004. All four entries originally not applicable to direct source. RandomNumberGenerator/FixedTimeEquals and OpenIddict development certificates existed, but are not these changed calls. Reassess other targets/dependencies. [Index](index.md).

## Pkcs netstandard API removal

Removed System.Security.Cryptography.Pkcs netstandard2.0 APIs concern a library running on .NET Framework. Seven net8 C# projects had no PKCS reference/call.

Source: [PKCS APIs](https://learn.microsoft.com/en-us/dotnet/core/compatibility/cryptography/9.0/api-removed-pkcs).

## OpenSSL key handle duplication

SafeEvpPKeyHandle.DuplicateHandle now up-refs the handle. No safe handle/raw key/RSAOpenSsl/ECDsaOpenSsl calls found; reassess native ownership/lifetime.

Source: [EVP key handle](https://learn.microsoft.com/en-us/dotnet/core/compatibility/cryptography/9.0/evp-pkey-handle).

## X509 constructor obsoletions

Some X509Certificate/X509Certificate2 constructors/imports obsolete with SYSLIB0057. No direct affected construction; development-certificate helper usage is not equivalent. Check actual compiler diagnostics and auth startup, not blanket suppression.

Source: [X509 constructors](https://learn.microsoft.com/en-us/dotnet/core/compatibility/cryptography/9.0/x509-certificates).

## Windows private key lifetime

PKCS12/PFX private-key ownership on Windows simplified. Original Alpine path/no direct PFX collection import did not match. Known IIS deployment must independently reassess; Linux source assessment is not Windows runtime evidence.

Source: [private key lifetime](https://learn.microsoft.com/en-us/dotnet/core/compatibility/cryptography/9.0/private-key-lifetime). Compile for new diagnostics and exercise auth under the actual host. No cryptographic runtime proof from this research.
