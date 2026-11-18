# .NET 10 containers

**Researched**, **2026-09-23**; WPR-N10-CONT-001/002. [Index](index.md).

## Explicit image family and OS default

**Possibly applies.** Unqualified .NET 10 tags default to Ubuntu 24.04; Debian .NET 10 images are not shipped. Explicit Alpine avoids an implicit default OS change, not the need to change major. Deliberately select supported tags. Ubuntu requires replacing apk paths and checking ICU/native dependencies. Alpine requires musl, Oracle, SQL and culture checks, plus actual execution on each required architecture.

Sources: [default Ubuntu](https://learn.microsoft.com/en-us/dotnet/core/compatibility/containers/10.0/default-images-use-ubuntu), [images](https://learn.microsoft.com/en-us/dotnet/core/docker/container-images).

## Publish workflow and image gates

Plain dotnet publish/Dockerfile publish does not implicitly become SDK PublishContainer. `/t:PublishContainer` is opt-in; no source SDK container properties. Early research suggested Compose/build.sh/live connectivity; accepted plan instead used safe temporary publish/disposable image to avoid destructive/shared state. Do not execute historical suggestions as portable defaults.

Verify published port/assets/Data Protection storage, startup/auth/database/native libraries, ICU/timezones, bounded graceful stop and every deployed architecture. The original Dockerfile passed TARGETARCH through restore/publish; that alone does not prove multi-architecture behavior.

Sources: [SDK what's new](https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-10/overview), [SDK publish](https://learn.microsoft.com/en-us/dotnet/core/containers/sdk-publish), [configuration](https://learn.microsoft.com/en-us/dotnet/core/containers/publish-configuration), [lessons](../../../lessons.md).
