# .NET 10 cryptography

**Researched**, **2026-09-23**; WPR-N10-CRYPTO-001 through 004. All eight entries. Original hashes/nonces/local comparisons and Linux deployment are not all certificate/native paths. [Index](index.md).

## Unix OpenSSL minimum

**Applies.** OpenSSL 1.1.1+ is required on Unix; older libraries can prevent startup. SHA256.HashData/FixedTimeEquals/RandomNumberGenerator and image startup/auth require actual checks. Verify the selected image and noncontainer hosts, not SDK presence alone.

Source: [minimum](https://learn.microsoft.com/en-us/dotnet/core/compatibility/cryptography/10.0/openssl-version-requirement).

## X509 null parameters and OpenSSL override

**Possibly applies.** X509/PublicKey absent algorithm parameters now null, previously empty array. No direct call but OIDC/IdentityModel signing metadata path possible. Test actual relevant discovery/callback/token certificates, not assume every key affected.

CLR_OPENSSL_VERSION_OVERRIDE renamed DOTNET_OPENSSL_VERSION_OVERRIDE. Neither in repository; injected settings unknown. Rename only actual old values.

Sources: [null parameters](https://learn.microsoft.com/en-us/dotnet/core/compatibility/cryptography/10.0/x509-publickey-null), [override](https://learn.microsoft.com/en-us/dotnet/core/compatibility/cryptography/10.0/version-override).

## Postquantum and COSE API changes

Original absent uses: CompositeMLDsa draft07->08; CoseSigner.Key nullable; MLDsa/SlhDsa SecretKey members renamed PrivateKey. Reassess actual postquantum/COSE consumers, not ordinary hash/nonce usage.

Sources: [CompositeMLDsa](https://learn.microsoft.com/en-us/dotnet/core/compatibility/cryptography/10.0/composite-mldsa-draft-08), [COSE](https://learn.microsoft.com/en-us/dotnet/core/compatibility/cryptography/10.0/cosesigner-key-null), [rename](https://learn.microsoft.com/en-us/dotnet/core/compatibility/cryptography/10.0/mldsa-slhdsa-secretkey-to-privatekey).

## MacOS primitives and distinguished names

OpenSSL-backed primitives unsupported on macOS. Original Linux/platform-neutral factories, no RSAOpenSsl/AesCcm usage. X500DistinguishedName string validation stricter, no construction found. Reassess platform/custom certificates, retain OIDC checks. Neither macOS nor real identity provider tested here.

Sources: [macOS](https://learn.microsoft.com/en-us/dotnet/core/compatibility/cryptography/10.0/openssl-macos-unsupported), [X500](https://learn.microsoft.com/en-us/dotnet/core/compatibility/cryptography/10.0/x500distinguishedname-validation).
