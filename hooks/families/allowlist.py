"""Build-time view of canonical runtime suppression shared with Guardian."""
from pathlib import Path

ALLOWLIST_SOURCE = (Path(__file__).resolve().parents[1] / "runtime/scan_allowlist.py").read_text().split("\n\n", 1)[1].rstrip() + "\n\n\n"
