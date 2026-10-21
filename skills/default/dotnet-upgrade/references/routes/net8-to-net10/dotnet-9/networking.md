# .NET 9 networking

**Researched**, date unspecified; WPR-N9-NET-001 through 003. All six entries. [Index](index.md).

## Factory versus YARP networking

YARP 2.3 creates SocketsHttpHandler/HttpMessageInvoker directly, not IHttpClientFactory. Application had no AddHttpClient/factory, test WebApplicationFactory clients are different. Three factory-specific changes originally did not apply: default header-value redaction, SocketsHttpHandler primary handler, factory-log URI query redaction. HttpListenerRequest.UserAgent nullable also absent in ASP.NET source. Reassess actual client construction.

Sources: [YARP implementation](https://github.com/microsoft/reverse-proxy/blob/v2.3.0/src/ReverseProxy/Forwarder/ForwarderHttpClientFactory.cs#L29-L57), [configuration](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/yarp/http-client-config?view=aspnetcore-9.0), [header redaction](https://learn.microsoft.com/en-us/dotnet/core/compatibility/networking/9.0/redact-headers), [default handler](https://learn.microsoft.com/en-us/dotnet/core/compatibility/networking/9.0/default-handler), [factory logs](https://learn.microsoft.com/en-us/dotnet/core/compatibility/networking/9.0/query-redaction-logs), [UserAgent](https://learn.microsoft.com/en-us/dotnet/core/compatibility/networking/9.0/useragent-nullable).

## Server port metric tags

**Possibly applies.** HttpClient metrics always include server.port, including 80/443. YARP handler emits http.client instruments. No local collector/query found; external filters/cardinality may change. Verify proxy route and actual telemetry owners.

Source: [server.port](https://learn.microsoft.com/en-us/dotnet/core/compatibility/networking/9.0/server-port-attribute).

## EventSource query redaction

**Possibly applies.** System.Net.Http EventSource query becomes `*`, user-info/fragment removed, independently of factory logs. No listener/override in source. Check external diagnostics; retain redaction unless required and safe. External consumers were uninspected, not runtime-tested.

Source: [EventSource redaction](https://learn.microsoft.com/en-us/dotnet/core/compatibility/networking/9.0/query-redaction-events).
