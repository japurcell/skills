---
title: Avalonia Build, Run, and Launch Verification
priority: CRITICAL
tags: avalonia, build, run, launch, verification, dotnet, desktop
sources:
  - https://docs.avaloniaui.net/docs/get-started/
  - https://docs.avaloniaui.net/docs/deployment/
---

## Use For

Building, running, startup debugging, and verifying an Avalonia app actually opened.

## Workflow

1. Identify solution/project, target framework, configuration, runtime identifier if relevant, and target platform.
2. Build after meaningful edits.
3. Run when feasible.
4. Verify objective launch: visible window, expected title/content, responsive app, no immediate crash.
5. Debug ambiguous launch before saying ready.

## Commands

- `dotnet restore`
- `dotnet build`
- `dotnet run --project ./MyApp.csproj`
- `dotnet build ./MyApp.sln`
- `dotnet build -c Release`

## Startup Checks

- `Program.cs`
- `App.axaml`
- `App.axaml.cs`
- `MainWindow.axaml`
- `MainWindow.axaml.cs`
- lifetime configuration
- theme/style includes
- resource dictionaries
- assets
- view locator/data templates
- DI startup code
- platform-specific services

## Common Failures

- Missing templates or restore failure.
- `x:Class` or namespace mismatch.
- Resource URI/path problems.
- Style selector errors.
- Missing theme include.
- Binding errors in debug output.
- Platform-specific API used unguarded.
- Missing native dependency.

## Automated Headless UI Testing

To run integration tests that verify actual UI layouts, bindings, controls, and events in a CI or headless CLI environment:

### Packages Required

- `Avalonia.Headless`
- `Avalonia.Headless.XUnit` (or `Avalonia.Headless.NUnit`)

### Implementation Pattern

1. Add an assembly-level attribute to your test project to specify the application builder provider:

   ```csharp
   [assembly: AvaloniaTestApplication(typeof(MyProject.Tests.AppBuilderProvider))]
   ```

2. Define the setup provider class:

   ```csharp
   public class AppBuilderProvider
   {
       public static AppBuilder BuildAvaloniaApp() =>
           AppBuilder.Configure<App>()
               .UseHeadless(new AvaloniaHeadlessPlatformOptions());
   }
   ```

3. Write standard facts using `[AvaloniaFact]` instead of standard `[Fact]` to force execution on the headless UI Thread:

   ```csharp
   [AvaloniaFact]
   public void Button_Click_Should_Update_Message()
   {
       var window = new MainWindow();
       var btn = window.FindControl<Button>("SubmitButton");
       var txt = window.FindControl<TextBlock>("StatusText");
       
       // Trigger user interaction headlessly
       btn.Command.Execute(null);
       
       Assert.Equal("Submitted!", txt.Text);
   }
   ```

## Exit Criteria

- Build succeeds.
- App launches.
- Expected top-level UI appears.
- No unresolved startup exception remains.
