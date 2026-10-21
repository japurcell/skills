---
title: Testing, Debugging, and Review Checklists
priority: HIGH
tags: testing, debugging, review, verification, accessibility, performance
---

## Verification Loop

- Build after each meaningful edit.
- Run after startup, shell, navigation, resource, or packaging changes.
- Verify actual launch, not just process start.
- Debug startup failures before continuing feature work.
- Test the workflow the user will actually use.

## Design Review

- Navigation simple and predictable.
- Layout usable when narrow.
- Light, dark, contrast, hierarchy, and states hold up.
- Commands placed clearly.
- Built-in controls do most of the work.
- Scroll ownership explicit.

## Code Review

- Structure proportionate to app size.
- Resources and styles centralized where appropriate.
- Dependencies justified.
- Platform assumptions explicit.
- Intended build/run workflow works.

## Accessibility Review

- Keyboard-only flow works.
- Focus visible.
- Accessible names present.
- High contrast and text scaling do not break UI.

## Automated Testing

Test business and presentation logic at the lowest level possible. Ensure a test project is created under the naming convention `[ProjectName].Tests`.

### Core Commands

- Run all tests: `rtk test "dotnet test"`
- Filter specific tests: `rtk test "dotnet test --filter Category=Unit"`

### ViewModel and Presentation Logic (MVVM)

- **Do not bind unit tests to UI elements.** Verify binding logic by instantiating the ViewModel directly and asserting on state change notifications.
- **Property Change Notifications (`INotifyPropertyChanged`)**: Assert that properties notify changes as expected:

  ```csharp
  var vm = new MainViewModel(mockService.Object);
  bool notified = false;
  vm.PropertyChanged += (s, e) => { if (e.PropertyName == nameof(vm.UserName)) notified = true; };
  vm.UserName = "Alice";
  Assert.True(notified);
  ```

- **Async Command Execution**: Avoid calling standard `Command.Execute(null)` on async commands as exceptions are swallowed. Instead, cast to `IRelayCommand` (or framework equivalent) and verify async execution state:

  ```csharp
  await vm.SubmitCommand.ExecuteAsync(null);
  Assert.Equal("Success", vm.StatusMessage);
  ```

- **Mock Dependencies**: Inject service interfaces (e.g., `IDataService`) into ViewModels rather than concrete platform implementations. Use `NSubstitute` or `Moq` to stub/mock these interfaces during test runs.

### Threading and Dispatcher contexts in Tests

Because UI frameworks enforce thread affinity, executing unit tests that interact with UI controls or trigger ViewModels that push updates to the UI thread will throw threading errors in typical test runners.

- **Avoid Thread Affinity in ViewModels**: Abstract thread dispatcher references (e.g., `Dispatcher.UIThread` in Avalonia, `DispatcherQueue` in WinUI) behind a custom mockable dependency like `IDispatcherService` to decouple ViewModels from the concrete UI thread during tests.
- **Avalonia Thread Guard**: Execute tests using headless XUnit's `[AvaloniaFact]` and `[AvaloniaTheory]` attributes, which automatically run test routines inside the active UI synchronization context.
- **WinUI Thread Guard**: Ensure tests that must spin up WinUI components are dispatched using a helper class to queue them onto the active `DispatcherQueueSynchronizationContext`.

## Exit Criteria

- Build succeeds.
- App launches and shows expected UI.
- Primary flows are usable, accessible, and responsive.
