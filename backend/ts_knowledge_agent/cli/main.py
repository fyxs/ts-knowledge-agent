from __future__ import annotations

import argparse
from collections.abc import Sequence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ts-kb")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("status")
    sub.add_parser("scan")
    sub.add_parser("search")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    print(f"ts-kb: {args.command} scaffold; implementation pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
