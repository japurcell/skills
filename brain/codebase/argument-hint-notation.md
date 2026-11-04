# Skill argument hints

Claude Code's `argument-hint` is display text shown during autocomplete. It does not parse or validate arguments. Invocation text is exposed through `$ARGUMENTS`, indexed placeholders such as `$0`, or named placeholders; the separate `arguments` field declares names for `$name` substitution. See the [Claude Code frontmatter reference](https://code.claude.com/docs/en/skills#frontmatter-reference) and [argument substitution](https://code.claude.com/docs/en/skills#pass-arguments-to-skills).

For CLI-style hints, use notation consistently:

- `<value>` marks a placeholder value the user supplies.
- `[item]` marks an optional item or group. Thus `[--arg <value>]` means the option can be omitted, but requires a value when used.
- Bare text is ambiguous across conventions. Microsoft's syntax key treats text without brackets as literal, while angle brackets clearly mark placeholders. Prefer `[--arg <value>]` over `[--arg name]` when `name` is a placeholder.
- Do not infer a default from brackets. Defaults and whether an input is truly optional come from the workflow or parser. Python `argparse`, for example, exposes a `default` setting and a separate `required` setting for options; its generated usage brackets optional options and leaves required positionals unbracketed. See [Python argparse](https://docs.python.org/3/library/argparse.html).

In this repository, a hint describes an invocation surface; it does not establish new runtime behavior. Keep body-defined input names such as `progress_file` and `task_id` as written, and do not render them as `--progress-file` or `--task-id` unless the body defines actual CLI flags. Use `<...>` for supplied values, and brackets only when the input may be omitted under the skill's actual workflow. State defaults in the body or hint only when they are established there.

For option syntax, Microsoft's [Command-line syntax key](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/command-line-syntax-key) defines angle-bracket text as a value placeholder and square brackets as optional items. PowerShell's [syntax guidance](https://learn.microsoft.com/en-us/powershell/scripting/developer/help/how-to-add-syntax-to-a-cmdlet-help-topic?view=powershell-7.6) distinguishes optional parameter names from required values and shows the equivalent `[-Parameter <Value>]` grouping.

## YAML quoting

Prefer single-quoted strings for `argument-hint` values, including hints that begin with `[`, so the value is clearly a scalar rather than YAML flow-collection syntax. An unquoted `<value>` is valid plain YAML, but quote hints consistently. Quote style is presentation only; it must not change the hint text.

YAML single quotes do not require escaping double quotes or backslashes. Represent an apostrophe by doubling it inside the single-quoted value, for example `argument-hint: 'user''s <path>'`. Use double quotes only when YAML escape processing is needed, such as a `\n` newline escape; a literal apostrophe alone is not a reason to switch styles. See the YAML 1.2.2 sections on [plain scalars](https://yaml.org/spec/1.2.2/#733-plain-style), [single-quoted scalars](https://yaml.org/spec/1.2.2/#732-single-quoted-style), and [double-quoted scalars](https://yaml.org/spec/1.2.2/#731-double-quoted-style).
