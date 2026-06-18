#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Main helper script (python3 -m mcmu)"""

from .cli import CLI


def main() -> int:
    """Main function"""
    try:
        cli = CLI()
        return cli.cli()
    except KeyboardInterrupt:
        print("^C pressed. Exiting...")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
