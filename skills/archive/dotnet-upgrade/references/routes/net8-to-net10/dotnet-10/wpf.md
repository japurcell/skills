# .NET 10 WPF

**Researched**, **2026-09-23**; WPR-N10-WPF-001. Both entries originally not applicable; no UseWPF/XAML/resources. [Index](index.md).

## Grid definitions and dynamic resources

Empty Grid.ColumnDefinitions/RowDefinitions disallowed. Incorrect DynamicResource usage now crashes. Reassess layout/resource runtime failures in actual WPF targets; Angular templates are outside these APIs. No WPF run proves portability here.

Sources: [empty grids](https://learn.microsoft.com/en-us/dotnet/core/compatibility/wpf/10.0/empty-grid-definitions), [DynamicResource](https://learn.microsoft.com/en-us/dotnet/core/compatibility/wpf/10.0/dynamicresource-crash).
