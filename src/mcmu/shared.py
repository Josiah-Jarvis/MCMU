#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Shared helper scripts for MCMU"""

from re import match
from os import listdir, getenv, environ
from pathlib import Path
from platform import system


from . import logger
from .mods import Mod
from .api import ModrinthAPI

ModAPI = ModrinthAPI()


def get_categories() -> list:
    """Get a list of categories"""
    response = ModAPI.query("tag/category")
    categories = []
    for category in response:
        if category['project_type'] == "mod":
            categories.append(category['name'])
    return categories


def get_loaders() -> list:
    """Get a list of loaders"""
    response = ModAPI.query("tag/loader")
    loaders = []
    for loader in response:
        if "mod" in loader['supported_project_types']:
            loaders.append(loader['name'])
    return loaders


def get_game_versions() -> list:
    """Get a list of game versions"""
    response = ModAPI.query("tag/game_version")
    versions = []
    for version in response:
        versions.append(version['version'])
    return versions


modrinth_categories = get_categories()
modrinth_loaders = get_loaders()
modrinth_game_versions = get_game_versions()

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
    if GAME_VERSION in modrinth_game_versions:
        logger.info(
            "Game version set to '%s' because of environment variable",
            GAME_VERSION
        )
    else:
        logger.error(
            "Game version '%s' not a valid game version, setting to default...",
            GAME_VERSION
        )
        raise ValueError("Game version not a valid game version")
except (KeyError, ValueError):
    GAME_VERSION = "26.2"

try:
    MOD_LOADER = environ['MCMU_MOD_LOADER']
    if MOD_LOADER in modrinth_loaders:
        logger.info(
            "Mod loader set to '%s' because of environment variable",
            MOD_LOADER
        )
    else:
        logger.error(
            "Mod loader '%s' not a valid mod loader, setting to default...",
            MOD_LOADER
        )
        raise ValueError("Mod loader not a valid mod loader")
except (KeyError, ValueError):
    MOD_LOADER = "fabric"


def ask(question: str) -> bool:
    """Ask a question"""
    if input(f"{question} [Y/n]: ").lower() in ("y", ""):  # Check if y or ""
        return True  # Return 'yes'
    return False  # Return 'no'


def get_latest_version(
    mod_name: str,  # The name of the mod on Modrinth
    mod_loader: str,  # The mod loader to get for
    game_version: str,
    channel: list  # The channel to get mods from
) -> dict:  # Modrinth mod object or False if already at latest version
    """Checks for mod update from Modrinth"""
    response = ModAPI.project_version(
        mod_name, f"[\"{mod_loader}\"]", f'["{game_version}"]'
    )
    latest_version = {'version_number': "0"}
    for version in response:  # Check each mod version in the returned data
        if version['version_type'] in channel:
            if version["version_number"] > latest_version["version_number"]:
                latest_version = version  # Set to latest version if newer
    return latest_version  # Return the latest version


def list_mods(mod_path: Path) -> dict[Mod]:
    """Gets a list of installed mods"""
    mods = {}
    for mod in listdir(mod_path):
        m = match(r'^(.*?)_version_(.*)\.(?:jar|jar.disabled)$', str(mod))
        try:
            mods[m.group(1)] = Mod(
                name=m.group(1),
                version=m.group(2),
                file_name=mod,
                mod_folder=mod_path,
            )
        except AttributeError:
            logger.info("Unknown file in mod dir '%s'", mod)

    return mods


def download_dependency_s(
    dependency_s: list,  # List of mods dependency's
    mods: list,  # List of installed mods
    mod_path: Path,  # Path to the mods folder
    mod_loader: str = MOD_LOADER,
    game_version: str = GAME_VERSION,
    channel: list = "release"
):
    """Download a mods dependency's"""
    for dependency in dependency_s:
        mod_data = ModAPI.project(dependency['project_id'])
        if mod_data['slug'] not in mods:
            if dependency['dependency_type'] == "required":
                latest_version = get_latest_version(
                    mod_data['slug'],
                    mod_loader,
                    game_version,
                    channel
                )
                jar_file = Path(mod_path, f"{mod_data['slug']}_version_{latest_version['version_number']}.jar")
                ModAPI.get_file(
                    latest_version['files'][0]['url'],
                    jar_file,
                    latest_version['files'][0]['hashes']
                )
                print(f"\tDownloaded {jar_file} successfully.")
            elif dependency['dependency_type'] == "optional":
                if ask(f"Would you like to install optional dependency: {mod_data['slug']}?"):
                    latest_version = get_latest_version(
                        mod_data['slug'],
                        mod_loader,
                        game_version,
                        channel
                    )
                    jar_file = Path(mod_path, f"{mod_data['slug']}_version_{latest_version['version_number']}.jar")
                    ModAPI.get_file(
                        latest_version['files'][0]['url'],
                        jar_file,
                        latest_version['files'][0]['hashes']
                    )
                    print(f"\tDownloaded {jar_file} successfully.")  # Print the success
        elif (mod_data['slug'] in mods) and (dependency['dependency_type'] == "incompatible"):
            print(f"Incompatible dependency: {mod_data['slug']} installed, please remove.")


def update_mods(
    mods: dict,  # A dict of mods
    mod_path: Path,  # The path to the mods
    game_version: str = GAME_VERSION,
    mod_loader: str = MOD_LOADER,
    channel: list = "release"
) -> bool:
    """Updates mods"""
    for mod_name in mods:
        latest_version = get_latest_version(
            mod_name,
            mod_loader,
            game_version,
            channel
        )  # Check for update
        if not latest_version["version_number"] > mods[mod_name].version:
            latest_version = False
        if latest_version:  # If latest version is a dict it should be True
            old_file = Path(
                mod_path,
                mods[mod_name].file_name
            )  # Path to the old mod file
            additional_storage = latest_version['files'][0]['size'] - old_file.stat().st_size  # Calculate how much more storage will be taken up
            if ask(f"{mods[mod_name].name} will take up: {additional_storage} additional bytes. Would you like to install?"):
                download_dependency_s(
                    latest_version['dependencies'],
                    mods,
                    mod_path,
                    mod_loader,
                    game_version,
                    channel
                )
                jar_file = Path(
                    mod_path,
                    f"{mod_name}_version_{latest_version['version_number']}.jar"
                )
                ModAPI.get_file(
                    latest_version['files'][0]['url'],
                    jar_file,
                    latest_version['files'][0]['hashes']
                )
                print(f"Downloaded mod at {jar_file} successfully.")
                print(f"Deleting old file: {old_file}")
                try:
                    old_file.unlink()  # Delete old file
                except PermissionError:
                    print("No permission to delete the file.")
                    return False
            else:
                print("Canceling.")
        else:
            print(f"Mod '{mod_name}' at latest version!")
    return True


def install_mod(
        mod: str,  # The mod
        mods: dict,  # Dict of mods
        mod_path: Path,  # The path to the mods folder
        game_version: str = GAME_VERSION,
        mod_loader: str = MOD_LOADER,
        channel: list = "release"
) -> bool:
    """Installs a mod"""
    if mod in mods:  # If mod already installed exit
        print(f"{mod} already installed.")
        return True
    mod = mod.split("==")
    if len(mod) > 1:
        latest_version = ModAPI.get_project_version(mod[0], mod[1])
        if latest_version["version_number"] == "0":
            latest_version = False
        if latest_version:
            if game_version not in latest_version['game_versions']:
                latest_version = False
        if latest_version:
            logger.error(
                "%s does not support this game version.",
                mod[1]
            )
            return False
        if ask(f"{mod[0]} will take up: {latest_version['files'][0]['size']} bytes. Would you like to install?"):
            download_dependency_s(
                latest_version['dependencies'],
                mods,
                mod_path,
                mod_loader,
                game_version,
                channel
            )
            jar_file = Path(
                mod_path,
                f"{mod[0]}_version_{latest_version['version_number']}.jar"
            )
            ModAPI.get_file(
                latest_version['files'][0]['url'],
                jar_file,
                latest_version['files'][0]['hashes']
                )
            print(f"Downloaded mod at {jar_file} successfully.")
            return True
    latest_version = get_latest_version(
        mod[0],
        mod_loader,
        game_version,
        channel
    )
    if latest_version["version_number"] == "0":
        latest_version = False
    if latest_version:
        if game_version not in latest_version['game_versions']:
            latest_version = False
    if latest_version:  # Should be True if it is a dict with items
        if ask(f"{mod[0]} will take up: {latest_version['files'][0]['size']} bytes. Would you like to install?"):
            download_dependency_s(
                latest_version['dependencies'],
                mods,
                mod_path,
                mod_loader,
                game_version
            )
            jar_file = Path(
                mod_path,
                f"{mod[0]}_version_{latest_version['version_number']}.jar"
            )
            ModAPI.get_file(
                latest_version['files'][0]['url'],
                jar_file,
                latest_version['files'][0]['hashes']
                )
            print(f"Downloaded mod at {jar_file} successfully.")  # Success
        else:
            print("Canceling.")
            return True
    else:
        logger.error("Mod does not exist for that version and loader")
        return False
    return True


__all__ = [
    "modrinth_categories",
    "modrinth_loaders",
    "modrinth_game_versions",
    "GAME_VERSION",
    "MOD_DIR",
    "MOD_LOADER"
]
