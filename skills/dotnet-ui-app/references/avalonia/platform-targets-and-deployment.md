---
title: Avalonia Platform Targets and Deployment
priority: HIGH
tags: avalonia, deployment, publish, windows, macos, linux, browser, mobile, nativeaot
sources:
  - https://docs.avaloniaui.net/docs/deployment/
  - https://docs.avaloniaui.net/docs/deployment/native-aot
  - https://docs.avaloniaui.net/docs/platform-specific-guides
---

## Use For

Publishing, packaging, or targeting Avalonia apps for Windows, macOS, Linux, browser, mobile, or embedded systems.

## Prefer

- Identify target platforms before publish settings.
- Test on the real target OS.
- Framework-dependent deployment for development simplicity.
- Self-contained publishing when users should not install .NET.
- Platform-native packaging for end users.
- Native AOT only after compatibility is confirmed.

## Avoid

- Treating `dotnet publish` as proof the packaged app works.
- Assuming one publish command fits every OS.
- Enabling trimming/AOT without testing reflection, serialization, bindings, and third-party libraries.
- Shipping unsigned/unnotarized builds where signing is required.

## Publish Concepts

Decide:

- runtime identifier
- framework-dependent vs self-contained
- single-file vs directory
- trimming
- Native AOT
- OS-specific package
- signing/notarization
- update mechanism

Commands:

- `dotnet publish -c Release`
- `dotnet publish -c Release -r <runtime-identifier> --self-contained true`

## Platform Notes

- Windows: `.exe`, MSIX/MSI, signing, file associations, notifications, tray.
- macOS: app bundle, DMG/PKG, signing, notarization, sandboxing, Intel/Apple Silicon.
- Linux: AppImage, DEB/RPM, Flatpak/Snap, native dependencies, desktop files, icons.
- Browser/mobile/embedded: treat as distinct targets requiring target-specific testing.

## Exit Criteria

- Target platforms explicit.
- Publish mode documented.
- Published artifact runs on target OS.
- Platform features verified.
- Signing/packaging requirements identified.
