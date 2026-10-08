# .NET 10 networking

**Researched**, **2026-09-23**; WPR-N10-NET-001 through 003. Four entries. [Index](index.md).

## MailAddress consecutive dots

**Applies.** Consecutive dots in local/domain parts throw FormatException before SMTP. Configured FromEmail and user-entered recipients affected; EmailAddress attribute is not identical parser validation. Emailer catches SmtpException only. Audit/test sender and recipient boundaries, reject actionably at an approved input seam rather than swallow delivery failures. Later owner preserved existing unwrapped FormatException contract.

Source: [MailAddress](https://learn.microsoft.com/en-us/dotnet/core/compatibility/networking/10.0/mailaddress-consecutive-dots).

## URI length and diagnostic boundaries

**Possibly applies.** The approximately 65k URI limit was removed; Origin/Referer TryCreate diagnostics may now parse longer values. ReturnUrl string policy is independent of the Uri limit. Actual server, proxy and header limits were unknown; no source Kestrel override was found. Test oversized headers and use explicit bounds when required, not Uri as a length validator.

Source: [URI limit](https://learn.microsoft.com/en-us/dotnet/core/compatibility/networking/10.0/uri-length-limits-removed).

## Trimmed HTTP3 and browser streaming

Original not-applicable cases: HttpClient HTTP3 disabled by default under PublishTrimmed/PublishAot (no such publish or HTTP3); browser HttpClient response streaming defaults (no WASM .NET client, Angular distinct). Reassess other publish/client types.

Sources: [HTTP3](https://learn.microsoft.com/en-us/dotnet/core/compatibility/networking/10.0/http3-disabled-with-publishtrimmed), [browser streaming](https://learn.microsoft.com/en-us/dotnet/core/compatibility/networking/10.0/default-http-streaming).
