---
title: WinUI Setup and Project Selection
priority: CRITICAL
tags: winui, setup, prerequisites, packaged, unpackaged, visual-studio, dotnet
sources:
  - https://learn.microsoft.com/windows/apps/get-started/start-here
  - https://learn.microsoft.com/windows/apps/winui/winui3/
  - https://learn.microsoft.com/windows/apps/windows-app-sdk/
  - https://learn.microsoft.com/windows/apps/windows-app-sdk/system-requirements
---

## What This Reference Is For

Use this file when the user is starting from scratch, choosing a WinUI project template, or asking what a WinUI machine needs before code work begins.

## Prefer

- The WinUI setup-and-scaffold flow in the top-level skill for prerequisite setup, template verification, and first scaffold.
- A C# WinUI 3 desktop app on the Windows App SDK unless the user has a clear reason to prefer C++ or an existing non-WinUI stack.
- Official project templates and default packaging choices first.
- The current supported LTS .NET SDK for new C# work instead of only meeting the bare minimum.
- A packaged app by default for the smoothest first-project, deployment, and Store-compatible path.
- An unpackaged app when the user explicitly needs repeatable CLI build-and-run verification or direct executable launches as the normal local workflow.

## Avoid

- Starting project setup before the WinUI setup-and-scaffold flow has finished.
- Starting with unpackaged deployment unless the user needs repeatable CLI launch, an installer, existing desktop app integration, or a deliberate runtime strategy.
- Giving machine-readiness advice without verification.
- Treating old Windows builds, missing SDKs, or partial Visual Studio installs as "probably fine."
- Deferring the packaging choice until after startup, storage, and launch code are already written.

## Setup Baseline

- Use the WinUI setup-and-scaffold flow for prerequisite setup, template verification, and first scaffold.
- Treat `configs/winui-config.yaml` as the bundled WinGet bootstrap source for setup and remediation.
- Return to this reference only after that workflow completes or when the task moves beyond initial project creation.
- Windows 10 version 1809, build 17763, or later is the floor.
- Windows SDK 10.0.19041.0 or later is the practical baseline.
- Visual Studio with the WinUI application development workload is the supported primary IDE path.
- For C# apps, a supported .NET SDK must be installed.
- Developer Mode matters for common local deploy and debug flows.

## Project Selection Guidance

- Choose packaged when the user wants the default WinUI 3 path, easy local F5 workflows, or Store-friendly deployment.
- Choose packaged when the app needs package identity or package-backed APIs during normal operation.
- Choose unpackaged when the user expects direct `.exe` launches, agent-driven local verification after each change, or integration with an existing installer or external location.
- For either packaging model, scaffold first through the setup flow and continue from the generated project instead of copying in prebuilt baseline files.
- If startup or shared resources later become suspect, create a fresh comparison app with the same packaging model and diff against that `dotnet new winui` output before broader restructuring.
- Once the model is chosen, keep startup and service code consistent with that model.
- Choose the standard blank app template first, then layer in navigation, title bar, or windowing patterns as the app matures.

## Template Commands

Verify template availability:

```powershell
dotnet new list winui
```

Scaffold:

```powershell
dotnet new winui -o <AppName>
```

Common supported options include:

- `-f|--framework net10.0|net9.0|net8.0`
- `-slnx|--use-slnx`
- `-cpm|--central-pkg-mgmt`
- `-mvvm|--use-mvvm`
- `-imt|--include-mvvm-toolkit`
- `-un|--unpackaged`
- `-nsf|--no-solution-file`
- `--force`

Do not invent unsupported flags. If the user asks for packaged behavior, pass `--unpackaged false`. Otherwise keep the template default.

## Review Checklist

- Is the machine baseline actually verified?
- Is the chosen packaging model intentional?
- Does the launch workflow match the chosen packaging model?
- Is the app still rooted in the standard WinUI template unless there is a real reason not to?
- Is the recommendation aligned with a C#-first WinUI 3 workflow?
