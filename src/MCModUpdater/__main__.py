#!/usr/bin/env python3

import argparse
import requests
from pathlib import Path

__version__ = "0.1.0"
__author__ = "Josiah Jarvis"

parser = argparse.ArgumentParser(
    prog="MCModUpdater",
    epilog="..."
)
parser.add_argument("-v", "--version", action="version", version=__version__)
parser.add_argument("-m", "--mod_path", default=Path(Path.home(), ".minecraft/mods"))
parser.add_argument("-i", "--install")
parser.parse_args()

def main():
    pass

main()