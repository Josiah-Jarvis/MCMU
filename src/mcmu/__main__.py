"""Main helper script (python3 -m mcmu)"""

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
    raise SystemExit(main())
