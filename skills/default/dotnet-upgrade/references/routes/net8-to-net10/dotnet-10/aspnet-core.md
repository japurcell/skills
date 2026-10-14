# ASP.NET Core 10

**Researched**, **2026-09-23**; WPR-N10-ASP-001 through 005. MVC/Razor hosts, Angular not Blazor; baseline net8. [Index](index.md), [migration guide](https://learn.microsoft.com/en-us/aspnet/core/migration/90-to-100?view=aspnetcore-10.0&tabs=visual-studio-code), [complete catalog](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/overview?view=aspnetcore-10.0).

## Known IP networks rename

**Applies.** KnownNetworks/old IPNetwork obsolete, use KnownIPNetworks/System.Net.IPNetwork for explicit ranges. KnownProxies remains valid. API rename does not authorize broadening trust. Original lists empty; later accepted spoofing risk is [case-specific](../../../case-studies/workplan-reports.md#accepted-forwarded-header-risk).

Source: [obsoletion](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/ipnetwork-knownnetworks-obsolete?view=aspnetcore-10.0).

## Cookie API versus browser redirects

**Possibly applies.** Cookie handler challenge/forbid on known API metadata, including ApiController, returns 401/403 instead of redirect. Original default challenge OIDC/custom AJAX makes this scheme-conditional, notably cookie forbid. Assert status/Location for OIDC/local APIs and separate intended browser/callback/logout redirects. No global IgnoreRedirectMetadata unless approved product need.

Source: [cookie API endpoints](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/cookie-authentication-api-endpoints?view=aspnetcore-10.0).

## OpenAPI diagnostics and accessor obsoletions

Original absent uses:

- WithOpenApi deprecated; Swashbuckle does not imply it. [Source](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/withopenapi-deprecated?view=aspnetcore-10.0).
- IExceptionHandler.TryHandleAsync true suppresses diagnostics; path UseExceptionHandler("/Error") is different. [Source](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/exception-handler-diagnostics-suppressed?view=aspnetcore-10.0).
- IActionContextAccessor/ActionContextAccessor obsolete. [Source](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/iactioncontextaccessor-obsolete?view=aspnetcore-10.0).
- IncludeOpenAPIAnalyzers/MVC API analyzers deprecated; package presence alone does not enable property. [Source](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/openapi-analyzers-deprecated?view=aspnetcore-10.0).
- ApiDescription.Client/OpenApiReference/dotnet openapi deprecated; none found. [Source](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/apidescription-client-deprecated?view=aspnetcore-10.0).

## Hosting Razor and Blazor assessments

Razor runtime compilation obsolete, no package/AddRazorRuntimeCompilation. WebHostBuilder/IWebHost/WebHost obsolete; production WebApplication and test ConfigureWebHostDefaults are different. Blazor WASM environment/boot/cache, state persistence, passkeys and navigation changes do not apply merely because a Razor host shell serves Angular.

Sources: [Razor](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/razor-runtime-compilation-obsolete?view=aspnetcore-10.0), [WebHost](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/webhostbuilder-deprecated?view=aspnetcore-10.0), migration guide above.

## Swagger and authentication migration gates

AddSwaggerGen/UseSwagger/UI coexisted with direct OpenAPI package, no AddOpenApi/MapOpenApi/WithOpenApi. Built-in document generation is not mandatory replacement. Operation customization uses IOperationFilter when required. Preserve document/UI, test Development/Local/path base and relative `./v1/swagger.json`, including JS loader. Framework/auth/EF/Extensions/System.Net.Http.Json updates must use actual graph; test challenge/callback/PKCE/cookie/return URL/logout/API flows. Compilation alone later missed a host TypeLoadException.

Source: [OpenAPI generation](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/aspnetcore-openapi?view=aspnetcore-10.0). These research checks are not proof of runtime flows or upstream support for Swashbuckle.
