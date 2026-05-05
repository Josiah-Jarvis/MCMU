#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Shared helper scripts for MCMU"""


from re import match
from os import listdir
from pathlib import Path

from . import logger, GAME_VERSION
from .mods import Mod
from .api import ModrinthAPI

ModAPI = ModrinthAPI()


def ask(question: str, no_ask: bool = False) -> bool:
    """Ask a question"""
    if no_ask:
        print(f"{question} [Y/n]: Y")
        return True
    answer = input(f"{question} [Y/n]: ").lower()
    if answer in ("y", ""):  # Check if answer was Y, y or ""
        return True  # Return 'yes'
    return False  # Return 'no'


def get_latest_version(
    mod_name: str,  # The name of the mod on Modrinth
    game_version: str = GAME_VERSION
) -> dict:  # Modrinth mod object or False if already at latest version
    """Checks for mod update from Modrinth"""
    response = ModAPI.project_version(
        mod_name, '["fabric"]', f'["{game_version}"]'
    )
    latest_version = response[0]  # Set to first version in list
    for version in response:  # Check each mod version in the returned data
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
    game_version: str = GAME_VERSION
):
    """Download a mods dependency's"""
    for dependency in dependency_s:
        mod_data = ModAPI.project(dependency['project_id'])
        if mod_data['slug'] not in mods:
            if dependency['dependency_type'] == "required":
                latest_version = get_latest_version(
                    mod_data['slug'],
                    game_version
                )
                jar_file = Path(mod_path, f"{mod_data['slug']}_version_{latest_version['version_number']}.jar")
                ModAPI.get_file(
                    latest_version['files'][0]['url'],
                    jar_file
                )
                print(f"\tDownloaded {jar_file} successfully.")
            elif dependency['dependency_type'] == "optional":
                if ask(f"Would you like to install optional dependency: {mod_data['slug']}?"):
                    latest_version = get_latest_version(
                        mod_data['slug'],
                        game_version
                    )
                    jar_file = Path(mod_path, f"{mod_data['slug']}_version_{latest_version['version_number']}.jar")
                    ModAPI.get_file(
                        latest_version['files'][0]['url'],
                        jar_file
                    )
                    print(f"\tDownloaded {jar_file} successfully.")  # Print the success
        elif (mod_data['slug'] in mods) and (dependency['dependency_type'] == "incompatible"):
            print(f"Incompatible dependency: {mod_data['slug']} installed, please remove.")


def update_mods(
    mods: dict,  # A dict of mods
    mod_path: Path,  # The path to the mods
    game_version: str = GAME_VERSION,
    no_ask: bool = False
) -> bool:
    """Updates mods"""
    for mod_name in mods:
        latest_version = get_latest_version(
            mod_name,
            game_version
        )  # Check for update
        if not latest_version["version_number"] > mods[mod_name].version:
            latest_version = False
        if latest_version:  # If latest version is a dict it should be True
            old_file = Path(
                mod_path,
                mods[mod_name].file_name
            )  # Path to the old mod file
            additional_storage = latest_version['files'][0]['size'] - old_file.stat().st_size  # Calculate how much more storage will be taken up
            if ask(f"{mods[mod_name].name} will take up: {additional_storage} additional bytes. Would you like to install?", no_ask):
                download_dependency_s(
                    latest_version['dependencies'],
                    mods,
                    mod_path,
                    game_version
                )
                jar_file = Path(
                    mod_path,
                    f"{mod_name}_version_{latest_version['version_number']}.jar"
                )
                ModAPI.get_file(
                    latest_version['files'][0]['url'],
                    jar_file
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
        no_ask: bool = False
) -> bool:
    """Installs a mod"""
    if mod in mods:  # If mod already installed exit
        print(f"{mod} already installed.")
        return True
    mod = mod.split("==")
    if len(mod) > 1:
        latest_version = ModAPI.get_project_version(mod[0], mod[1])
        if game_version not in latest_version['game_versions']:
            logger.error(
                "%s does not support this game version.",
                mod[1]
            )
        if ask(f"{mod[0]} will take up: {latest_version['files'][0]['size']} bytes. Would you like to install?", no_ask):
            download_dependency_s(
                latest_version['dependencies'],
                mods,
                mod_path,
                game_version
            )
            jar_file = Path(
                mod_path,
                f"{mod[0]}_version_{latest_version['version_number']}.jar"
            )
            ModAPI.get_file(latest_version['files'][0]['url'], jar_file)
            print(f"Downloaded mod at {jar_file} successfully.")
            return True
    latest_version = get_latest_version(mod[0], game_version)
    if latest_version:  # Should be True if it is a dict with items
        if ask(f"{mod[0]} will take up: {latest_version['files'][0]['size']} bytes. Would you like to install?", no_ask):
            download_dependency_s(
                latest_version['dependencies'],
                mods,
                mod_path,
                game_version
            )
            jar_file = Path(
                mod_path,
                f"{mod[0]}_version_{latest_version['version_number']}.jar"
            )
            ModAPI.get_file(latest_version['files'][0]['url'], jar_file)
            print(f"Downloaded mod at {jar_file} successfully.")  # Success
        else:
            print("Canceling.")
            return True
    else:
        logger.error("Mod does not exist for that version and loader")
        return False
    return True
