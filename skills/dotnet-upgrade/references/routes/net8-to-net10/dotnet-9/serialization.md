# .NET 9 serialization

**Researched**, date unspecified; WPR-N9-SER-001 through 003. All three entries originally not applicable to direct source. STJ API/scheduler JSON and Hangfire Newtonsoft are distinct contracts. [Index](index.md).

## BinaryFormatter removal

In-box BinaryFormatter always throws. No BinaryFormatter/IFormatter found, persistence/HTTP use JSON. Check dependency calls in actual tests instead of enabling obsolete formatter for compatibility.

Source: [removal](https://learn.microsoft.com/en-us/dotnet/core/compatibility/serialization/9.0/binaryformatter-removal).

## Nullable JsonDocument properties

Nullable JsonDocument properties deserialize to document JsonValueKind.Null, not a null reference. Source JsonDocument calls parsed tests; production dropdown used JsonElement, not that property shape. Future DTOs need explicit null-document tests.

Source: [JsonDocument properties](https://learn.microsoft.com/en-us/dotnet/core/compatibility/serialization/9.0/jsondocument-props).

## Escaped JSON metadata

STJ metadata reader unescapes names. Ordinary camel-case/encoder/default scheduler options, no ReferenceHandler/JsonPolymorphic/JsonDerivedType. Preserve response shapes and JobRequest round trips; reassess escaped metadata if introduced.

Source: [metadata reader](https://learn.microsoft.com/en-us/dotnet/core/compatibility/serialization/9.0/json-metadata-reader).
