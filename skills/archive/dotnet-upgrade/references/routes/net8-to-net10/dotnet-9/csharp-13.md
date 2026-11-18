# C# 13 compiler

**Researched**, date unspecified; WPR-N9-CS-001 through 003. SDK moves C# 12 to 13 under LangVersion latest. [Compiler changes](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/breaking-changes/compiler%20breaking%20changes%20-%20dotnet%209), [C# 13](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-13), [index](index.md).

## Collection expression overload resolution

**Possibly applies.** Exact element-type preference/empty collection binding can change. Target-typed test arguments and SetCookieHeaderValue.ParseList calls existed, no competing Span/ReadOnlySpan example confirmed. Compile/exercise; explicit type/cast only for demonstrated changed behavior.

## Interface accessibility style

**Applies to analyzer configuration.** Style now checks interface members. Original for_non_interface_members:warning and members without redundant explicit modifiers should stay consistent; no new warning expected. Actual diagnostics decide, not speculative language pin/suppression.

## Record iterator indexer and method group changes

Original absent scenarios: InlineArray forbidden on record structs (none); iterators introduce safe context (async iterators, no unsafe/pointer inheritance); indexers require valid DefaultMemberAttribute (no user declarations); optional/params affect method-group natural types (direct calls only). Reassess each elsewhere; compile/test every project.
