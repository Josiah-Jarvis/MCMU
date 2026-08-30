"""Main helper script (python3 -m mcmu)"""

from logging import DEBUG
from . import logger
from .cli import CLI


def main() -> int:
    """Main function"""
    try:
        cli = CLI()  # Set up CLI class
        return cli.cli()  # Run CLI
    except KeyboardInterrupt:  # If CTRL+C
        print(" pressed, exiting...")  # Print error
        return 130  # Exit


if __name__ == "__main__":
    logger.level = DEBUG
    logger.debug("DEBUG mode on")
    raise SystemExit(main())
