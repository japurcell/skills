# .NET 10 Windows Forms

**Researched**, **2026-09-23**; WPR-N10-WIN-001/002. All six entries, originally not applicable. No desktop projects/controls; Angular distinct. [Index](index.md).

## Desktop API and control changes

- WinForms API obsoletions. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/windows-forms/10.0/obsolete-apis).
- WPF/WinForms MenuItem/ContextMenu ambiguity. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/windows-forms/10.0/menuitem-contextmenu).
- HtmlElement.InsertAdjacentElement parameter rename. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/windows-forms/10.0/insertadjacentelement-orientation).
- TreeView checkbox/text rendering. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/windows-forms/10.0/treeview-text-location).
- StatusStrip.RenderMode default. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/windows-forms/10.0/statusstrip-renderer).

## GDI exception boundaries

GDI+ failures change OutOfMemoryException to ExternalException. Original only System.Drawing.Color.LightGreen in Excel style, not native graphics/image operations/catches. Color usage alone does not prove affected GDI path. Reassess actual drawing consumers.

Source: [GDI exception](https://learn.microsoft.com/en-us/dotnet/core/compatibility/windows-forms/10.0/system-drawing-outofmemory-externalexception). No desktop runtime testing here.
