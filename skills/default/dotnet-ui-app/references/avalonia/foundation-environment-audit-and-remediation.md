---
title: Avalonia Environment Audit and Remediation
priority: CRITICAL
tags: avalonia, setup, audit, dotnet, templates, ide, cross-platform
sources:
  - https://docs.avaloniaui.net/docs/get-started/
  - https://docs.avaloniaui.net/docs/get-started/install-avalonia
---

## Use For

Machine readiness checks, missing .NET SDK/templates, IDE support, and setup remediation.

## Audit Workflow

For audit-only requests, do not install or change anything without confirmation.

Check:

- OS and architecture.
- `dotnet --info`
- `dotnet --list-sdks`
- `dotnet new list avalonia`
- IDE/editor if relevant.
- Existing project build if present.

Summarize under:

- present
- missing
- uncertain
- recommended optional tools

## Remediation

If approved:

- `dotnet new install Avalonia.Templates`
- `dotnet new list avalonia`

For new projects, scaffold, build, and run before calling setup complete.

## Required

- Supported .NET SDK.
- Avalonia templates for CLI scaffolding.
- Working .NET build tools.

## Optional

- Visual Studio, Rider, or VS Code.
- Avalonia extensions or preview tooling.
- Platform-specific packaging/signing tools.
- Git.

## Review

- Environment checked before remediation?
- Machine-changing commands approved?
- Missing and uncertain items separated?
- App actually builds and launches?
