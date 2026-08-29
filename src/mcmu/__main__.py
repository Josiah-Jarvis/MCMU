"""Main helper script (python3 -m mcmu)"""

from .cli import CLI
from .shared import logger


def main() -> int:
    """Main function"""
    try:
        cli = CLI()  # Set up CLI class
        return cli.cli()  # Run CLI
    except KeyboardInterrupt:  # If CTRL+C
        print("^C pressed. Exiting...")  # Print error
        return 130  # Exit


if __name__ == "__main__":
    logger.setLevel(10)  # Set to debug
    raise SystemExit(main())
