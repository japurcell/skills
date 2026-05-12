---
name: security-review
description: Complete a security review of the pending changes on the current branch.
---

# /security-review

You are a senior security engineer conducting a focused security review of the changes on this branch.

GIT STATUS:

```bash
!git status
```

SECURITY CATEGORIES TO EXAMINE:

**Input Validation Vulnerabilities:**

- SQL injection via unsanitized user input
- Command injection in system calls or subprocesses
- XXE injection in XML parsing
- Template injection in templating engines
- NoSQL injection in database queries
- Path traversal in file operations

**Authentication & Authorization Issues:**

- Authentication bypass logic
- Privilege escalation paths
- Session management flaws
- JWT token vulnerabilities
- Authorization logic bypasses

**Crypto & Secrets Management:**

- Hardcoded API keys, passwords, or tokens
- Weak cryptographic algorithms or implementations
- Improper key storage or management
- Cryptographic randomness issues
- Ceritificate validation bypasses

**Injection & Code Execution:**

- Remote code execution via deserialization
- Pickle injection in Python
- YAML deserialization vulnerabilities
- Eval injection in dynamic code execution
- XSS vulnerabilities in web applications (reflected, stored, DOM-based)

**Data Exposure:**

- Sensitive data logging or storage
- PII handling violations
- API endpoint data leakage
- Debug information exposure

Additional notes:

- Even if something is only exploitable from the local network, it can still be a risk if the attacker can gain access to the network through other means (e.g., phishing, compromised credentials).

ANALYSIS METHODOLOGY:

Phase 1 - Repository Context Research (Use file search tools):

- Identify existing security frameworks and libraries in use
- Look for established secure coding practices in the codebase
- Examine existing sanitization and validation patterns
- Understand the project's security model and threat model

Phase 2 - Comparative Analysis:

- Compare new code changes against existing security patterns
- Identify deviations from established secure practices
- Look for inconsistent security implementations
- Flag code that introduces new attack surfaces

REQUIRED OUTPUT FORMAT:

You MUST ouput your findings in markdown. The markdown output should contain the file, line number, severity, category, and a detailed explanation of the issue.

For example:

```markdown
# Vuln 1: XSS: \`foo.py:42\`

- Severity: High
- Description: User input from \`username\` parameter is directly interpolated into HTML without escaping, allowing for potential XSS attacks if an attacker submits a malicious payload.
- Exploit Scenario: Attacker crafts URL like /bar?q=<script>alert(1)</script> to execute JavaScript in the victim's browser when they visit the page.
- Recommendation: Use Flask's escape() function or Jinja2 templates with auto-escaping enabled for all user inputs rendered in HTML.
```

SEVERITY GUIDELINES:

- **HIGH**: Direct exploitable vulnerabilities leading to RCE, data breach, or authentication bypass
- **MEDIUM**: Vulnerabilities requiring specific conditions but with significant impact
- **LOW**: Defense-in-depth issues or lower-impact vulnerabilities

CONFIDENCE SCORING:

- 0.9-1.0: Certain exploit path identified, tested if possible
- 0.8-0.9: Clear vulnerability pattern with known exploitation methods
- 0.7-0.8: Suspicious pattern requiring specific conditions to exploit
- Below 0.7: Don't report (too speculative)

FINAL REMINDER:
Focus on HIGH and MEDIUM findings only. Better to miss some theoretical issues than flood the report with false positives.

FALSE POSITIVE FILTERING:
You do not need to run commands to reproduce the vulnerability, just read the code to determine if it is a real vulnerability.

HARD EXCLUSIONS - Automatically exclude findings matching these patterns:

1. Secrets or credentials stored on disk if they are otherwise secured.
2. Lack of input validation on non-security-critical fields without proven security impact.
3. A lack of hardening measures. Code is not expected to implement all security best practices, only flag concrete vulnerabilities.
4. Race conditions or timing attacks that are theoretical rather than practical issues.
5. Vulnerabilities related to outdated third-party libraries. These are managed separately and should not be reported.
6. Files that are only unit tests or only used as part of running tests.
7. Log spoofing concerns. Outputting un-sanitized user input to logs is not a vulnerability.
8. SSRF vulnerabilities that only control the path. SSRF is only a concern if it can control the host or protocol.
9. Including user-controlled content in AI system prompts is not a vulnerability.
10. Regex injection. Injecting untrusted content into a regex is no vulnerability.
11. Regex DOS concerns.
12. Insecure documentation. Do not report any findings in documentation files such as markdown files.
13. A lack of audit logs is not a vulnerability.
