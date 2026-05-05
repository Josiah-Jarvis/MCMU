#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Main helper script (python3 -m mcmu)"""

from .cli import CLI


def main():
    """Main function"""
    cli = CLI()
    return cli.cli()


if __name__ == "__main__":
    raise SystemExit(main())
