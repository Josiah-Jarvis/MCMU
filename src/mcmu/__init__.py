#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Package wide code"""

from logging import getLogger, basicConfig
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("mcmu")
except PackageNotFoundError:
    __version__ = "Version  Not Found"

logger = getLogger(__name__)
logger.setLevel(20)
basicConfig(format="%(levelname)s: %(message)s")  # Set logging format
