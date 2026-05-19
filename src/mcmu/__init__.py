#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Package wide code"""

from os import getenv, environ
from logging import getLogger, basicConfig, INFO
from pathlib import Path
from platform import system
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("mcmu")
except PackageNotFoundError:
    __version__ = "Version  Not Found"

logger = getLogger(__name__)
logger.setLevel(INFO)
basicConfig(format="%(levelname)s: %(message)s")  # Set logging format

try:
    MOD_DIR = environ['MCMU_MOD_PATH']
    logger.info(
        "Mod dir set to '%s' because of environment variable",
        MOD_DIR
    )
except KeyError:
    if system() == "Darwin":
        MOD_DIR = Path(
            Path.home(), "Library/Application Support/minecraft/mods/"
        )
    elif system() == "Windows":
        MOD_DIR = Path(getenv('APPDATA'), ".minecraft\\mods\\")
    else:  # Should be linux or other unix like systems
        MOD_DIR = Path(Path.home(), ".minecraft/mods/")

try:
    GAME_VERSION = environ['MCMU_GAME_VERSION']
    logger.info(
        "Game version set to '%s' because of environment variable",
        GAME_VERSION
    )
except KeyError:
    GAME_VERSION = "26.2"

try:
    MOD_LOADER = environ['MCMU_MOD_LOADER']
    logger.info(
        "Mod loader set to '%s' because of environment variable",
        MOD_LOADER
    )
except KeyError:
    MOD_LOADER = "fabric"


__all__ = [GAME_VERSION, MOD_DIR, MOD_LOADER]
