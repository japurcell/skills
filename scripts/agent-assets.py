#!/usr/bin/env python3
"""Install selected committed agent assets into a team repository."""

from collections.abc import Sequence

from agent_assets.cli import main as cli_main


def main(argv: Sequence[str] | None = None) -> int:
    return cli_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
