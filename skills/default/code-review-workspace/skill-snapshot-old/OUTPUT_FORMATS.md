# Output Formats

## PR comment mode

If reviewing a PR, repeat the PR eligibility check before commenting.

If still eligible, post with `gh pr comment`.

If qualifying findings remain, use this format exactly:

```text
### Code review
Found <N> issues:
1. <brief description>
   <link to file and line with full sha and line range>
2. <brief description>
   <link to file and line with full sha and line range>
3. <brief description>
   <link to file and line with full sha and line range>
   <sub>- If this code review was useful, please react with 👍. Otherwise, react with 👎.</sub>
...
```

If no qualifying findings remain, use:

```text
### Code review
## No issues found. Checked for bugs, standards compliance, and maintainability.
```

## PR comment requirements

- keep it brief
- no emojis except the required footer line
- cite and link relevant files, code, standards, and URLs
- for code links, use full Git SHA and line ranges
- provide at least 1 line of context before and after when possible

## Code link format

Link format must be exactly:

```text
https://github.com/OWNER/REPO/blob/FULL_SHA/path/to/file.ext#L10-L15
```

Requirements:

- full git SHA only
- repository name must match the reviewed repo
- line format must be `#L[start]-L[end]`

## Machine-readable mode

Categorize findings as `Critical`, `Important`, or `Suggestion`.

Use this structure:

```yaml
review:
  summary: "<brief summary>"
  findings:
    - severity: Critical | Important | Suggestion
      title: "<short finding title>"
      file: "<path>"
      lines: "<start-end>"
      link: "<full GitHub link if available>"
      introduced_by_change: true
      confidence: 75 | 100
      category: correctness | standards | spec | maintainability | architecture | security | performance | readability
      evidence: "<specific evidence>"
      impact: "<practical impact>"
      recommendation: "<specific fix>"
  notes:
    - "<optional concise note>"
```

If no qualifying findings remain:

```yaml
review:
  summary: "No qualifying issues found."
  findings: []
```
