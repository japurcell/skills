"""Build-time compatibility view of the normal streaming matcher."""
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / "runtime/scan_stream.py").read_text().split("\n", 1)[1]
