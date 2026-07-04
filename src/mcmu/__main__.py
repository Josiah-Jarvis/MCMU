#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Main helper script (python3 -m mcmu)"""

from .shared import logger
from .cli import CLI


def main() -> int:
    """Main function"""
    try:
        logger.setLevel(10)  # Set to debug
        cli = CLI()  # Set up CLI class
        return cli.cli()  # Run CLI
    except KeyboardInterrupt:  # If CTRL+C
        print("^C pressed. Exiting...")  # Print error
        return 130  # Exit


if __name__ == "__main__":
    raise SystemExit(main())
