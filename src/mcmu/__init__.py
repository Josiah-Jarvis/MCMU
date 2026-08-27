#!/usr/bin/env python3

"""Package wide code"""

from importlib.metadata import version, PackageNotFoundError
from logging import getLogger, basicConfig

try:
    __version__ = version("mcmu")
except PackageNotFoundError:
    __version__ = "Version  Not Found"

logger = getLogger(__name__)
logger.setLevel(20)
basicConfig(format="%(levelname)s: %(message)s")  # Set logging format
