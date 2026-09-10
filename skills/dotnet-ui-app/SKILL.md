---
name: dotnet-ui-app
description: Bootstrap, develop, and design modern .NET desktop and cross-platform UI applications with C# using WinUI 3, the Windows App SDK, and Avalonia UI. Mandatory whenever creating a brand new app, preparing a machine for WinUI or Avalonia development, choosing between Windows-first and cross-platform UI frameworks, reviewing, refactoring, planning, troubleshooting, environment-checking, or setting up WinUI 3 or Avalonia XAML, controls, navigation, shell composition, windowing, theming, styling, accessibility, input, localization, responsiveness, performance, deployment, packaging, or related .NET app design and development work.
---

# .NET UI App

Use this skill for modern .NET UI work across WinUI 3 / Windows App SDK and Avalonia UI.

## Framework Paths

- **WinUI 3 / Windows App SDK**: use for Windows-first desktop apps, Fluent Windows UX, Store/MSIX workflows, Windows App SDK APIs, lifecycle, notifications, packaging, Mica, and Windows shell integration.
- **Avalonia UI**: use for cross-platform .NET UI across Windows, macOS, Linux, and selected browser/mobile/embedded targets, especially when CLI-friendly development and shared UI code matter.

## Required Flow

1. Classify the task as framework selection, environment/setup, new-app bootstrap, design, implementation, review, troubleshooting, or deployment.
2. Determine the framework:
   - Use WinUI when the user asks for WinUI, Windows App SDK, Windows-only desktop, Microsoft Store/MSIX, Mica, Windows lifecycle, notifications, or windowing APIs.
   - Use Avalonia when the user asks for Avalonia, cross-platform desktop, Linux/macOS support, shared XAML UI, or CLI-friendly .NET desktop work.
   - Ask a concise clarifying question if the framework is not implied.
3. Read `references/_sections.md`, then load only the narrowest matching references.
4. Apply shared UI guidance first, then framework-specific guidance only when implementation details matter.
5. For new apps:
   - Choose or confirm a safe app name.
   - Create the project in the current workspace unless another location is requested.
   - Do not overwrite existing files unless the user explicitly asks.
   - Verify templates before scaffolding.
   - Scaffold from official templates.
   - Build, run, and verify a real top-level window or expected UI.
6. For WinUI setup, use `configs/winui-config.yaml` only after approval for machine-changing remediation.
7. For Avalonia setup, prefer non-mutating checks first: `dotnet --info`, `dotnet new list avalonia`; install `Avalonia.Templates` only when needed and appropriate.
8. For app edits, make a minimal complete edit set, build, run when feasible, and verify objective startup behavior.
9. Preserve existing codebase conventions.
10. Do not mechanically translate XAML across frameworks. Adapt controls, resources, bindings, styles, and platform APIs.

## Common Routes

| Request                          | Read first                                                                   |
| -------------------------------- | ---------------------------------------------------------------------------- |
| Choose WinUI vs Avalonia         | `references/_sections.md`                                                    |
| General UI design review         | `references/common/testing-debugging-and-review-checklists.md`               |
| Controls or layout               | `references/common/controls-layout-and-adaptive-ui.md`                       |
| Accessibility/input/localization | `references/common/accessibility-input-and-localization.md`                  |
| Styling/theme/icons              | `references/common/styling-theming-and-icons.md`                             |
| Performance/responsiveness       | `references/common/performance-diagnostics-and-responsiveness.md`            |
| New WinUI app                    | `references/winui/foundation-setup-and-project-selection.md`                 |
| New Avalonia app                 | `references/avalonia/foundation-setup-and-project-selection.md`              |
| Build/run WinUI                  | `references/winui/build-run-and-launch-verification.md`                      |
| Build/run Avalonia               | `references/avalonia/build-run-and-launch-verification.md`                   |
| WinUI lifecycle/deployment       | `references/winui/windows-app-sdk-lifecycle-notifications-and-deployment.md` |
| Avalonia deployment              | `references/avalonia/platform-targets-and-deployment.md`                     |

## Universal UI Rules

- Use framework controls before custom controls.
- Avoid bespoke component systems unless explicitly required.
- Support light and dark mode by default.
- Avoid hard-coded light-only or dark-only colors.
- Treat accessibility as part of implementation.
- Preserve visible focus and keyboard reachability.
- Make scroll ownership explicit.
- Avoid redundant cards, borders, and nested visual containers.
- Treat responsiveness as shell plus page behavior.
- Keep navigation simple, stable, and task-oriented.

## WinUI Rules

- Prefer native WinUI and Fluent controls.
- Prefer `NavigationView` for standard desktop shells.
- Prefer `CommandBar` for grouped commands.
- Make packaged vs unpackaged explicit early.
- Use Windows App SDK APIs for lifecycle, notifications, deployment, and windowing.
- Use CommunityToolkit only when built-in WinUI does not cover the need cleanly.

## Avalonia Rules

- Prefer built-in Avalonia controls, resources, styles, theme variants, and selectors.
- Prefer official Avalonia templates for new apps.
- Prefer MVVM for nontrivial state and commands, but avoid ceremony for small prototypes.
- Use compiled bindings where they improve safety/performance and the project is structured for them.
- Keep platform-specific behavior explicit.
- Do not assume Windows App SDK, Mica, WinUI `NavigationView`, or WinUI resource keys exist.
- Verify on the target OS when platform behavior matters.
