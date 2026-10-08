# .NET 9 Windows Forms and WPF

**Researched**, date unspecified; WPR-N9-DESKTOP-001 through 003. Nine WinForms/one WPF entries retained. No WindowsDesktop SDK, UseWindowsForms/UseWPF or desktop APIs in seven original server projects. Angular is not a desktop .NET UI. Reassess each for actual desktop targets; none runtime-tested here. [Index](index.md).

## Binding nullability designers and accessibility

- BindingSource.SortDescriptions no longer returns null. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/windows-forms/9.0/sortdescriptions-return-value).
- Nullability annotations change, including IWindowsFormsEditorService. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/windows-forms/9.0/nullability-changes).
- ComponentDesigner.Initialize throws ArgumentNullException. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/windows-forms/9.0/componentdesigner-initialize).
- DataGridViewRowAccessibleObject.Name uses one-based row index. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/windows-forms/9.0/datagridviewrowaccessibleobject-name-row).

## Component manager analyzers and control behavior

- IMsoComponent support opt-in; assess Office/COM UI integration. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/windows-forms/9.0/imsocomponent-support).
- New security analyzers, including designer serialization. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/windows-forms/9.0/security-analyzers).
- DataGridViewHeaderCell no longer throws when grid null. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/windows-forms/9.0/datagridviewheadercell-nre).
- PictureBox raises HttpClient exceptions. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/windows-forms/9.0/httpclient-exceptions).
- StatusStrip default renderer changes. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/windows-forms/9.0/statusstrip-renderer).

## WPF XML namespace maps

GetXmlNamespaceMaps type changes; no DependencyObject/markup use in original source. Preserve for WPF consumers rather than collapsing desktop guidance to irrelevant.

Source: [XML namespace maps](https://learn.microsoft.com/en-us/dotnet/core/compatibility/wpf/9.0/xml-namespace-maps).
