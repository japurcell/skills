"""Provider-neutral behavior vectors for generated secret scanners."""

from __future__ import annotations

import json


FAKE_GITHUB_TOKEN = "gh" + "p_" + ("0" * 36)
FAKE_GITHUB_FINE_GRAINED_TOKEN = "github_" + "pat_" + ("fake_" * 5)
FAKE_AWS_ACCESS_KEY = "AKIA" + ("0" * 16)
FAKE_STRIPE_KEY = "sk_" + "live_" + ("0" * 16)
FAKE_SLACK_TOKEN = "xox" + "b-" + ("0" * 10)

PATTERN_VECTORS = (
    ("github_classic_pat", FAKE_GITHUB_TOKEN, "high", "ghp_...0000"),
    ("github_fine_grained_pat", FAKE_GITHUB_FINE_GRAINED_TOKEN, "high", "gith...ake_"),
    ("aws_access_key", FAKE_AWS_ACCESS_KEY, "high", "AKIA...0000"),
    ("stripe_live_key", FAKE_STRIPE_KEY, "high", "sk_l...0000"),
    ("slack_token", FAKE_SLACK_TOKEN, "medium", "xoxb...0000"),
)

NEGATIVE_PATTERN_VECTORS = (
    "gh" + "p_" + ("0" * 35),
    "AKIA" + ("0" * 15),
    "sk_" + "test_" + ("0" * 20),
    "xox" + "b-" + ("0" * 9),
)

CREDENTIAL_PATH_VECTORS = (
    ("credentials", True),
    ("config/credentials.fake", True),
    (".ssh/config", True),
    ("deploy/.secrets/notes.md", True),
    ("scan-secrets.sh", False),
    ("docs/secrets-guide.md", False),
)

ENV_PATH_VECTORS = (
    (".env", True),
    ("config/.env.local", True),
    ("config/environment.txt", False),
)

ALLOWLIST_INPUT = "credentials.md:1:credential_path:[SENSITIVE PATH]"
ALLOWLIST_RAW = json.dumps(
    [{"tool": "scan_secrets", "input": ALLOWLIST_INPUT}],
    separators=(",", ":"),
)
ALLOWLIST_ENTRIES = (("scan_secrets", ALLOWLIST_INPUT),)

