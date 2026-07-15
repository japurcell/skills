# Output Formats

## PR comment mode

Before commenting, repeat the PR eligibility check from `references/pr-protocol.md`.

If findings remain, use exactly:

```text
### Code review
Found <N> issues:
1. <brief description>
   <link to file and line with full SHA and line range>
2. <brief description>
   <link to file and line with full SHA and line range>
```

If no findings remain, use exactly:

```text
### Code review
## No issues found. Checked for change-linked correctness, security, standards, spec when available, test, and maintainability issues.
```

Requirements:

- keep it brief
- no emojis
- cite relevant files, code, standards, and URLs
- code links must use full Git SHA and line ranges
- include 1 context line before and after when possible

Code link format:

```text
https://github.com/OWNER/REPO/blob/FULL_SHA/path/to/file.ext#L10-L15
```

## Machine-readable mode

Use:

```yaml
review:
  summary: "<brief summary>"
  findings:
    - severity: Critical | Important | Suggestion
      title: "<short title>"
      file: "<path>"
      lines: "<start-end>"
      link: "<full GitHub link if available>"
      introduced_by_change: true
      confidence_score: 80-100
      category: correctness | standards | spec | maintainability | architecture | security | performance | readability
      evidence: "<specific evidence>"
      impact: "<practical impact>"
      recommendation: "<specific fix>"
  notes:
    - "<optional concise note>"
```

If no findings remain:

```yaml
review:
  summary: "No qualifying issues found."
  findings: []
```
