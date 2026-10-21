# ASP.NET Core

Use for ASP.NET Core apps, APIs, middleware, controllers, filters, and background work.

## Request Pipeline

- Keep controllers/minimal API handlers thin.
- Put business logic in services.
- Use async I/O throughout request handling.
- Do not call `.Result`, `.Wait()`, or sync APIs for request body reads.
- Do not use `Task.Run` just to make synchronous work appear async.
- Do not modify headers/status after the response has started.
- In middleware, do not call `next()` after writing a complete response.

## Results and Payloads

- Do not return huge collections.
- Use server-side pagination for large result sets.
- Do not return lazy `IEnumerable<T>` when it may serialize synchronously.
- Prefer `ToListAsync()` for bounded results or `IAsyncEnumerable<T>` for streaming.
- Stream large request/response bodies.
- Avoid buffering large bodies into `string` or `byte[]`.

## HttpContext Safety

- Do not store `HttpContext` in fields.
- Store `IHttpContextAccessor` if needed, then read `HttpContext` per request.
- Do not access `HttpContext` from parallel threads.
- Do not use `HttpContext` after the request completes.
- Do not capture `HttpContext` for background work; copy required values first.

## Background Work

- Do not run long CPU-bound or blocking work in the request path.
- Use `BackgroundService`, a queue, or an external worker.
- Do not capture scoped services such as `DbContext` for background threads.
- Create a scope with `IServiceScopeFactory` inside background work.

## HTTP Clients

- Prefer `IHttpClientFactory` for outgoing HTTP calls.
- Do not repeatedly create/dispose `HttpClient` per request.

## Security and Robustness

- Enforce request size limits.
- Do not assume `Request.ContentLength` has a value.
- Check `ContentLength is null` explicitly when size matters.
- Validate and bind inputs using framework features where possible.
