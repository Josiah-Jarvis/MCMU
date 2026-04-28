#!/usr/bin/env python3

"""Package wide code"""

from os import getenv, environ
from logging import getLogger, basicConfig, INFO
from pathlib import Path
from platform import system
from importlib.metadata import version, PackageNotFoundError

from .api import ModrinthAPI

try:
    __version__ = version("mcmu")
except PackageNotFoundError:
    __version__ = "vDev"

logger = getLogger(__name__)
logger.setLevel(INFO)
basicConfig(format="%(levelname)s: %(message)s")  # Set logging format

ModAPI = ModrinthAPI()

try:
    MOD_DIR = environ['MCMU_MOD_PATH']
    logger.info(
        "Mod dir set to %s because of environment variable.",
        MOD_DIR
    )
except KeyError:
    if system() == "Linux":
        MOD_DIR = Path(Path.home(), ".minecraft/mods/")
    elif system() == "Darwin":
        MOD_DIR = Path(
            Path.home(), "Library/Application Support/minecraft/mods/"
        )
    elif system() == "Windows":
        MOD_DIR = Path(getenv('APPDATA'), ".minecraft\\mods\\")
    else:
        logger.warning("System %s not known.", system())
        MOD_DIR = Path(Path.home(), ".minecraft/mods/")

try:
    GAME_VERSION = environ['MCMU_GAME_VERSION']
    logger.info(
        "Game version set to %s because of environment variable.",
        GAME_VERSION
    )
except KeyError:
    GAME_VERSION = "26.1.2"

__all__ = [GAME_VERSION, MOD_DIR]
