# Async and Performance

Use for async-heavy code, streaming, hot paths, high-throughput services, and large I/O.

## Async

- Use async all the way; avoid sync-over-async.
- Do not use `.Result`, `.Wait()`, or blocking waits.
- Do not use `async void` except event handlers.
- Do not fire-and-forget request work; use a background queue/service.
- Pass `CancellationToken` through async APIs.
- In long loops, check `ct.ThrowIfCancellationRequested()`.
- Make delays cancellable: `Task.Delay(delay, ct)`.
- Use `Task.WhenAll` for independent concurrent work.
- Use `ConfigureAwait(false)` in reusable library code when appropriate.

## Task vs ValueTask

- Prefer `Task` by default.
- Use `ValueTask` only when:
  - profiling shows benefit,
  - the method often completes synchronously, and
  - callers can follow `ValueTask` usage rules.

## Async Streams

- Return `IAsyncEnumerable<T>` for streamed async results.
- Accept cancellation with `[EnumeratorCancellation] CancellationToken`.
- Avoid materializing large streams unless required.

## Large JSON / HTTP Payloads

Prefer streaming:

1. `GetAsync(..., HttpCompletionOption.ResponseHeadersRead, ct)`
2. `ReadAsStreamAsync(ct)`
3. `JsonSerializer.DeserializeAsync<T>(stream, cancellationToken: ct)`

Avoid buffering large payloads into `string` or `byte[]`.

## Hot Paths

Optimize only when code is measured or clearly performance-sensitive.

- Avoid avoidable allocations.
- Avoid LINQ in tight loops if it allocates or obscures cost.
- Use `Span<T>` / `ReadOnlySpan<T>` for slicing transient memory.
- Use `ArrayPool<T>` or `ObjectPool<T>` for large reusable buffers/objects.
- Prefer `StringBuilder` for repeated string appends.
- Avoid exceptions for normal control flow.
- Keep logging structured but not noisy.

## Collections

- Choose the simplest collection that fits:
  - `T[]` for fixed-size data
  - `List<T>` for append-heavy mutable lists
  - `Dictionary<TKey,TValue>` for keyed lookups
  - `HashSet<T>` for membership checks
- Use `string.Contains` for substring checks.
- Use `.Chunk(size)` for simple batching when supported.
