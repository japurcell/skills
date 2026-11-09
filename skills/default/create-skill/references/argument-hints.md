# Argument hints

In Claude Code, `argument-hint` displays expected input during autocomplete. Parsing and validation belong to the workflow or parser. The body can read the invocation through `$ARGUMENTS`, an indexed placeholder such as `$0`, or a named positional placeholder such as `$task_id` declared in the separate `arguments` field. Check which fields the target host supports. [Claude Code frontmatter](https://code.claude.com/docs/en/skills#frontmatter-reference) and [argument substitution](https://code.claude.com/docs/en/skills#pass-arguments-to-skills).

## Match the invocation

- Use `<value>` for a value the caller supplies. Keep literal words and supported flags bare.
- Use `[item]` only for input the workflow permits callers to omit. In `[--format <value>]`, the flag is optional and requires a value when present. State a default only when the workflow or parser defines it. [Command-line syntax key](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/command-line-syntax-key).
- Preserve the body's input names. For a required positional `progress_file` and an optional positional `task_id`, write `<progress_file> [<task_id>]`. Spell an input as a flag only if the workflow accepts that flag.

## Quote the YAML scalar

Single-quote the whole hint consistently. A leading `[` starts a YAML flow sequence when unquoted. Inside single quotes, backslashes and double quotes are literal. Double an embedded apostrophe. Use double quotes when the parsed text needs a YAML escape such as `\n`. [YAML scalar styles](https://yaml.org/spec/1.2.2/#73-flow-scalar-styles).

```yaml
argument-hint: '[--format <value>]'
```

For the literal hint `user's <path>`, write `argument-hint: 'user''s <path>'`.
