# .NET 10 serialization

**Researched**, **2026-09-23**; WPR-N10-SER-001. Both entries originally not applicable. [Index](index.md).

## Reserved JSON metadata and obsolete XML properties

STJ rejects names conflicting with reserved metadata `$type/$id/$ref`. Source STJ jobs/reports had no JsonPolymorphic/JsonDerivedType/custom discriminator/ReferenceHandler.Preserve. Newtonsoft JsonProperty attributes are not the same feature.

XmlSerializer now serializes obsolete properties rather than ignoring them. No XmlSerializer/serialization attributes found. Reassess both contract shapes elsewhere; negative source search is not every dependency's guarantee.

Sources: [JSON names](https://learn.microsoft.com/en-us/dotnet/core/compatibility/serialization/10/property-name-validation), [XML obsolete](https://learn.microsoft.com/en-us/dotnet/core/compatibility/serialization/10/xmlserializer-obsolete-properties).
