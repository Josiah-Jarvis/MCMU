#!/usr/bin/env python3

"""Logging config"""

from logging import getLogger, basicConfig, INFO

logger = getLogger(__name__)
logger.setLevel(INFO)
basicConfig(format="%(levelname)s: %(message)s")  # Set logging format
