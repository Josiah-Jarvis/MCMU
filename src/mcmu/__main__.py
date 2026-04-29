#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A robust script to install, update, and manage Minecraft mods from Modrinth"""

from re import match
from os import listdir
from shutil import make_archive
from pathlib import Path
from logging import DEBUG
from datetime import datetime
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from . import __version__, logger, GAME_VERSION, MOD_DIR
from .api import ModrinthAPI
from .mods import Mod, ModDisabledError, ModEnabledError

ModAPI = ModrinthAPI()


def cli_update(args, mods) -> int:
    """CLI function to update mod"""
    if not update_mods(mods, args.mod_dir):
        return 1
    return 0


def cli_remove(args, mods) -> int:
    """CLI function to remove mod"""
    try:
        if ask(f"Would you like to remove {mods[args.mod]}? This operation will clear {mods[args.mod].file.stat().st_size} bytes."):
            mods[args.mod].delete()
            logger.info("Mod '%s' successfully deleted", args.mod)
    except KeyError:
        logger.error("Mod '%s' not installed", args.mod)
        return 1
    except PermissionError:
        logger.error(
            "No permission to delete '%s'", mods[args.mod].file_name
        )
        return 1
    except FileNotFoundError:
        logger.warning(
            "Mod file '%s' does not exist.", mods[args.mod].file_name
        )
        return 1
    return 0


def cli_install(args, mods) -> int:
    """CLI function to install mod"""
    try:
        if not install_mod(args.mod, mods, args.mod_dir):
            return 1
    except UserWarning:
        logger.error("Mod '%s' does not exist on Modrinth", args.mod)
        return 1
    return 0


def cli_list(args, mods) -> int:
    """CLI function to list mod"""
    for name, mod in mods.items():  # Iterate over all installed mods
        print(
            f"{name}\n\tVersion: {mod.version}\n\tFile: {mod.file_name}"
        )
    return 0


def cli_search(args, mods) -> int:
    """CLI function to search mods"""
    facets = '[["categories:fabric"],["project_type:mod"]]'
    response = ModAPI.search(args.term, facets)
    for mod in response['hits']:  # Iterate over and list all the mods
        search = f"""{mod['title']}:
    Description: {mod['description']}
    Author: {mod['author']}
    Downloads: {mod['downloads']}
    Latest Version: {mod['latest_version']}

"""
        print(search)
    return 0


def cli_info(args, mods) -> int:
    """CLI function to get info on a mod"""
    try:
        response = ModAPI.project(args.mod)
        info = f"""{response['slug']}
    Title: {response['title']}
    Description: {response['description']}
    Client Side: {response['client_side']}
"""
        print(info)
        print("Dependency's:")
        print(get_dependency(args.mod))
        return 0
    except UserWarning:
        logger.error("Mod '%s' does not exist on Modrinth", args.mod)
        return 1


def cli_enable(args, mods) -> int:
    """CLI function to enable mod"""
    try:
        mods[args.mod].enable()
        logger.info("Successfully enabled mod '%s'", args.mod)
    except KeyError:
        logger.error("Mod '%s' not installed so can't enable", args.mod)
    except ModEnabledError:
        logger.info("Mod '%s' already enabled", args.mod)
        return 1
    return 0


def cli_disable(args, mods) -> int:
    """CLI function to disable mod"""
    try:
        mods[args.mod].disable()
        logger.info("Successfully disabled mod '%s'", args.mod)
    except KeyError:
        logger.error("Mod '%s' not installed so can't disable", args.mod)
    except ModDisabledError:
        logger.info("Mod '%s' already disabled", args.mod)
        return 1
    return 0


def cli_backup(args, mods) -> int:
    """CLI function to backup mod"""
    make_archive(
        base_name=Path(
            args.mod_dir,
            "mods-backup",
            datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        ),
        format=args.type,
        root_dir=args.mod_dir
    )
    logger.info("Successfully backed up mods folder")
    return 0


def cli() -> dict:
    """Parses command line arguments"""
    parser = ArgumentParser(
        description=__doc__,
        epilog=f"Version: {__version__}",
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--mod-dir",
        default=MOD_DIR,
        help="Path to the Minecraft mods folder"
    )
    parser.add_argument(
        "--game-version",
        default=GAME_VERSION,
        help="The game version to use to install mods"
    )
    parser.add_argument(
        "--verbose",
        help="Increase logging level",
        action="store_true"
    )
    parser.add_argument(
        "-v",
        "--version",
        help="Display the version",
        action="version",
        version=__version__
    )
    subparsers = parser.add_subparsers(
        description="The function to run",
        dest="command",
        help="Action to run"
    )
    update_parser = subparsers.add_parser("update", help="Update mods")
    update_parser.set_defaults(func=cli_update)
    remove_parser = subparsers.add_parser("remove", help="Remove a mod")
    remove_parser.add_argument("mod", help="The mod to remove")
    remove_parser.set_defaults(func=cli_remove)
    install_parser = subparsers.add_parser("install", help="Install a mod")
    install_parser.add_argument("mod", help="Install a mod")
    install_parser.set_defaults(func=cli_install)
    list_parser = subparsers.add_parser("list", help="List mods")
    list_parser.set_defaults(func=cli_list)
    search_parser = subparsers.add_parser("search", help="Search mods")
    search_parser.add_argument("term", help="The term to search for")
    search_parser.set_defaults(func=cli_search)
    info_parser = subparsers.add_parser("info", help="Get info on a mod")
    info_parser.add_argument("mod", help="Get info on a mod")
    info_parser.set_defaults(func=cli_info)
    enable_parser = subparsers.add_parser("enable", help="Enable a mod")
    enable_parser.add_argument("mod", help="The mod to enable")
    enable_parser.set_defaults(func=cli_enable)
    disable_parser = subparsers.add_parser("disable", help="Disable a mod")
    disable_parser.add_argument("mod", help="The mod to disable")
    disable_parser.set_defaults(func=cli_disable)
    backup_parser = subparsers.add_parser("backup", help="Backup mods folder")
    backup_parser.add_argument(
        "type",
        help="The type of archive to make",
        choices=['zip', 'tar', 'gztar', 'bztar', 'xztar', 'zstdtar']
    )
    backup_parser.set_defaults(func=cli_backup)
    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(DEBUG)
    try:
        mods = list_mods(args.mod_dir)
    except FileNotFoundError:
        logger.error("Mod folder: %s does not exist", args.mod_dir)
        return 1
    if args.command is None:
        parser.print_help()
        return 0
    return args.func(args, mods)  # Parser the arguments


def ask(question: str) -> bool:
    """Ask a question"""
    answer = input(f"{question} [Y/n]: ").lower()
    if answer in ("y", ""):  # Check if answer was Y, y or ""
        return True  # Return 'yes'
    return False  # Return 'no'


def check_update(
    mod_name: str,  # The name of the mod on Modrinth
    current_version: str,  # The current installed version of the mod
) -> [bool, dict]:  # Modrinth mod object or False if already at latest version
    """Checks for mod update from Modrinth"""
    response = ModAPI.project_version(
        mod_name, '["fabric"]', f'["{GAME_VERSION}"]'
    )
    latest_version = {}  # None to indicate no newer version found yet
    for version in response:  # Check each mod version in the returned data
        if latest_version == {} or version["version_number"] > latest_version["version_number"]:  # Check to see if version newer
            latest_version = version  # Set to latest version
    if latest_version != {} and latest_version["version_number"] != current_version:  # Return latest version if it is newer than the current version
        return latest_version
    return False  # Return false for failure


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
                mod_folder=mod_path
            )
        except AttributeError:
            logger.debug("Unknown file in mod dir '%s'", mod)

    return mods


def download_dependency_s(
    dependency_s: list,  # List of mods dependency's
    mods: list,  # List of installed mods
    mod_path: Path,  # Path to the mods folder
):
    """Download a mods dependency's"""
    for dependency in dependency_s:
        mod_data = ModAPI.project(dependency['project_id'])
        if mod_data['slug'] not in mods:
            if dependency['dependency_type'] == "required":
                dependency_latest_version = check_update(mod_data['slug'], 0)
                mod_jar_file = Path(mod_path, f"{mod_data['slug']}_version_{dependency_latest_version['version_number']}.jar")
                ModAPI.get_file(dependency_latest_version['files'][0]['url'], mod_jar_file)
                print(f"\tDownloaded {mod_jar_file} successfully.")
            elif dependency['dependency_type'] == "optional":
                if ask(f"Would you like to install optional dependency: {mod_data['slug']}?"):
                    dependency_latest_version = check_update(mod_data['slug'], 0)
                    mod_jar_file = Path(mod_path, f"{mod_data['slug']}_version_{dependency_latest_version['version_number']}.jar")
                    ModAPI.get_file(dependency_latest_version['files'][0]['url'], mod_jar_file)
                    print(f"\tDownloaded {mod_jar_file} successfully.")  # Print the success
        elif (mod_data['slug'] in mods) and (dependency['dependency_type'] == "incompatible"):
            print(f"Incompatible dependency: {mod_data['slug']} installed, please remove.")


def update_mods(
    mods: dict,  # A dict of mods
    mod_path: Path,  # The path to the mods
) -> bool:
    """Updates mods"""
    for mod_name in mods:
        latest_version = check_update(mod_name, mods[mod_name].version)  # Check for update
        if latest_version:  # If latest version is a dict it should be True
            old_file = Path(mod_path, mods[mod_name].file_name)  # Path to the old mod file
            additional_storage = latest_version['files'][0]['size'] - old_file.stat().st_size  # Calculate how much more storage will be taken up
            if ask(f"{mods[mod_name].name} will take up: {additional_storage} additional bytes, would you like to install?"):
                download_dependency_s(
                    latest_version['dependencies'],
                    mods,
                    mod_path
                )
                mod_jar_file = Path(
                    mod_path,
                    f"{mod_name}_version_{latest_version['version_number']}.jar"
                )
                ModAPI.get_file(
                    latest_version['files'][0]['url'],
                    mod_jar_file
                )
                print(f"Downloaded mod at {mod_jar_file} successfully.")
                print(f"Deleting old file: {old_file}")
                try:
                    old_file.unlink()  # Delete old file
                except PermissionError:
                    print("No permission to delete the file.")
                    return False
            else:
                print("Canceling.")
        else:
            print(f"Mod: {mod_name} at latest version!")
    return True


def install_mod(
        mod: str,  # The mod
        mods: dict,  # Dict of mods
        mod_path: Path,  # The path to the mods folder
) -> bool:
    """Installs a mod"""
    if mod in mods:  # If mod already installed exit
        print(f"{mod} already installed.")
        return True
    mod_version = mod.split("==")
    if len(mod_version) > 1:
        mod = mod_version
        latest_version = ModAPI.get_project_version(mod[0], mod[1])
        if GAME_VERSION not in latest_version['game_versions']:
            logger.error(
                "%s version does not support this game version.",
                mod[1]
            )
        if ask(f"{mod[0]} will take up: {latest_version['files'][0]['size']} bytes, would you like to install?"):
            download_dependency_s(
                latest_version['dependencies'],
                mods,
                mod_path
            )
            mod_jar_file = Path(
                mod_path,
                f"{mod[0]}_version_{latest_version['version_number']}.jar"
            )
            ModAPI.get_file(latest_version['files'][0]['url'], mod_jar_file)
            print(f"Downloaded mod at {mod_jar_file} successfully.")  # Print the success
            return True
    latest_version = check_update(mod, "0")  # Set the version to 0 so any version would be higher
    if latest_version:  # Should be True if it is a dict with items
        if ask(f"{mod} will take up: {latest_version['files'][0]['size']} bytes, would you like to install?"):
            download_dependency_s(
                latest_version['dependencies'],
                mods,
                mod_path
            )
            mod_jar_file = Path(
                mod_path,
                f"{mod}_version_{latest_version['version_number']}.jar"
            )
            ModAPI.get_file(latest_version['files'][0]['url'], mod_jar_file)
            print(f"Downloaded mod at {mod_jar_file} successfully.")  # Success
        else:
            print("Canceling.")
            return True
    else:
        logger.error("Mod does not exist for that version and loader")
        return False
    return True


def get_dependency(project: str) -> str:
    """Gets a mods dependency's"""
    response = ModAPI.project_dependencies(project)
    for mod in response['projects']:
        dependency = f"""\t{mod['title']}"""
        return dependency


if __name__ == "__main__":
    exit(cli())
