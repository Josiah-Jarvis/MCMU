#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A script to download mods from Modrinth"""

from re import match
from os import listdir
from pathlib import Path
from logging import getLogger, basicConfig, INFO, DEBUG
from requests import get
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from importlib.metadata import version as get_version

logger = getLogger(__name__)
basicConfig(format="%(levelname)s: %(message)s")  # Set logging format
if __debug__:
    logger.setLevel(DEBUG)
else:
    logger.setLevel(INFO)


def cli() -> dict:
    """Parses command line arguments"""
    parser = ArgumentParser(
        description=__doc__,
        epilog=f"Version: {get_version(__package__)}",
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    group = parser.add_mutually_exclusive_group()  # Group for arguments
    group.add_argument("-u", "--up", help="Update mods", action="store_true")
    group.add_argument("-r", "--remove", help="Remove a mod")
    group.add_argument("-i", "--install", help="Install a mod")
    group.add_argument("-l", "--list", help="List mods", action="store_true")
    group.add_argument("-s", "--search", help="Search mods on Modrinth")
    group.add_argument("-d", "--dependency", help="List a mods dependency's")
    group.add_argument("-p", "--project", help="Get info about a project")
    parser.add_argument(
        "--mod_dir",
        default=Path(Path.home(), ".minecraft/mods/"),
        help="Path to the Minecraft mods folder"
    )
    parser.add_argument(
        "--game-version",
        default="26.1.1",
        help="The game version to use to install mods"
    )
    return parser.parse_args()  # Parser the arguments


def ask(question: str) -> bool:
    """Ask a question"""
    answer = input(f"{question} [Y/n]: ").lower()
    if answer in ("y", ""):  # Check if answer was Y, y or ""
        return True  # Return 'yes'
    return False  # Return 'no'


def check_update(mod_name: str, current_version: str, game_version: str) -> [bool, dict]:
    """Checks for mod update from Modrinth

    Arguments:
        mod_name -- The name of the mod on Modrinth
        current_version -- The current installed version of the mod

    Returns:
        Returns:
            False: Mod already at latest version
            Dict: Modrinth mod object
    """
    response = ModAPI.project_version(mod_name, '["fabric"]', f'["{game_version}"]')
    latest_version = None  # Set the latest_version to None to indicate no newer version found yet
    for version in response:  # Check each mod version in the returned data
        if latest_version is None or version["version_number"] > latest_version["version_number"]:  # Check to see if version newer
            latest_version = version  # If it is set latest_version to the newer version
    if latest_version is not None and latest_version["version_number"] != current_version:  # Return latest version if it is newer than the current version
        return latest_version
    return False  # Return false for failure


def list_mods(mod_path: Path):
    """Gets a list of installed mods"""
    mods = {}
    for mod in listdir(mod_path):
        m = match(r'^(.*?)_version_(.*)\.jar$', str(mod))
        mods[m.group(1)] = {
            "name": m.group(1),
            "version": m.group(2),
            "file": mod
        }
    return mods


class ModrinthAPI:
    """Modrinth API class"""
    def __init__(self):
        self.headers = {
            'User-Agent': f"Josiah-Jarvis/MCMU/{get_version(__package__)} (https://github.com/Josiah-Jarvis/MCMU)"
        }

    def query(self, endpoint: str, parameters: dict = None) -> dict:
        """Query's the Modrinth API

        Arguments:
            endpoint -- The API endpoint

        Keyword Arguments:
            parameters -- The parameters to pass the API (default: {None})

        Raises:
            DeprecationWarning: If response is 410
            UserWarning: If response is 400 or 404

        Returns:
            API json
        """
        response = get(
            url=f"https://api.modrinth.com/v2/{endpoint}",
            params=parameters,
            headers=self.headers,
            timeout=10
        )
        logger.debug(response.text)
        if response.status_code == 410:
            raise DeprecationWarning("API deprecated")
        if response.status_code == 404:
            raise UserWarning(f"Mod: {endpoint} not found")
        if response.status_code == 400:
            raise UserWarning("API request invalid")
        return response.json()

    def search(self, query: str, facets: str) -> [dict]:
        """Search's Mod on Modrinth

        Arguments:
            query -- The query string
            facets -- Used to limit the search results see

        Returns:
            dict: Response data
        """
        parameters = {
            'query': query,
            'facets': facets,
            'limit': "100"
        }
        return self.query("search", parameters)

    def project(self, slug: str) -> [dict]:
        """Get data about a project

        Arguments:
            slug -- The slug of the project

        Returns:
            dict: Project data
        """
        return self.query(f"project/{slug}")

    def project_dependencies(self, slug: str) -> [dict]:
        """Get a list of a projects dependencies

        Arguments:
            slug -- The slug of the project

        Returns:
            dict: Dependency information
        """
        return self.query(f"project/{slug}/dependencies")

    def project_version(self, slug: str, loaders: str, version: str) -> [dict]:
        """List a projects versions

        Arguments:
            slug -- The slug of the project
            loaders -- Loaders to filter for
            game_version -- Game versions to filter for

        Returns:
            dict: Project version data
        """
        parameters = {
            'loaders': loaders,
            'game_versions': version,
            'include_changelog': 'false'
        }
        return self.query(f"project/{slug}/version", parameters)

    def get_project_version(self, slug: str, version_number: str) -> [dict]:
        """Get a specific version from a mod

        Arguments:
            slug -- The name of the project
            version_number -- The specific version of the project

        Returns:
            The query's json
        """
        return self.query(f"project/{slug}/version/{version_number}")

    def get_file(self, file: str, path: Path):
        """Gets file from the CDN

        Arguments:
            file -- The file to download
            path -- The file to write to

        Raises:
            UserWarning: 404 code

        Returns:
            True if success
        """
        response = get(file, stream=True, timeout=10, headers=self.headers)
        if response.status_code == 404:
            raise UserWarning("Version file failed to download")
        try:
            with open(path, 'wb') as jar_file:  # Write to the jar file
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        jar_file.write(chunk)
        except PermissionError as exc:
            raise PermissionError(f"No permission to write: {path}") from exc
        return True


ModAPI = ModrinthAPI()


def update_mods(mods: dict, mod_path: Path, game_version) -> bool:
    """Updates mods

    Arguments:
        mods -- A dict of mods
        mod_path -- The path to the mods
    """
    for mod_name in mods:
        latest_version = check_update(mod_name, mods[mod_name]['version'], game_version)  # Check for update
        if latest_version:  # If latest version is a dict it should be True
            old_file = Path(mod_path, mods[mod_name]['file'])  # Path to the old mod file
            additional_storage = latest_version['files'][0]['size'] - old_file.stat().st_size  # Calculate how much more storage will be taken up
            if ask(f"{mods[mod_name]['name']} will take up: {additional_storage} additional bytes, would you like to install?"):
                for dependency in latest_version['dependencies']:
                    mod_data = ModAPI.project(dependency['project_id'])
                    if (mod_data['slug'] not in mods) and (dependency['dependency_type'] in ("required", "optional")):
                        dependency_latest_version = check_update(mod_data['slug'], 0, game_version)
                        mod_jar_file = Path(mod_path, f"{mod_data['slug']}_version_{dependency_latest_version['version_number']}.jar")
                        ModAPI.get_file(dependency_latest_version['files'][0]['url'], mod_jar_file)
                        print(f"\tDownloaded required dependency at {mod_jar_file} successfully.")  # Print the success
                    elif (mod_data['slug'] in mods) and (dependency['dependency_type'] == "incompatible"):
                        print(f"Incompatible dependency: {mod_data['slug']} installed, please remove.")
                        return True
                mod_jar_file = Path(mod_path, f"{mod_name}_version_{latest_version['version_number']}.jar")
                ModAPI.get_file(latest_version['files'][0]['url'], mod_jar_file)
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


def install_mod(mod: str, mods: dict, mod_path: Path, game_version: str) -> bool:
    """Installs a mod

    Arguments:
        mod -- The mod
        mods -- Dict of mods
        mod_path -- The path to the mods folder
    """
    if mod in mods:  # If mod already installed exit
        print(f"{mod} already installed.")
        return True
    mod_version = mod.split("==")
    if len(mod_version) > 1:
        mod = mod_version
        latest_version = ModAPI.get_project_version(mod[0], mod[1])
        if game_version not in latest_version['game_versions']:
            logger.error("%s version does not support this game version.", mod[1])
        if ask(f"{mod[0]} will take up: {latest_version['files'][0]['size']} bytes, would you like to install?"):
            for dependency in latest_version['dependencies']:
                mod_data = ModAPI.project(dependency['project_id'])
                if (mod_data['slug'] not in mods) and (dependency['dependency_type'] in ("required", "optional")):
                    dependency_latest_version = check_update(mod_data['slug'], 0, game_version)
                    mod_jar_file = Path(mod_path, f"{mod_data['slug']}_version_{dependency_latest_version['version_number']}.jar")
                    ModAPI.get_file(dependency_latest_version['files'][0]['url'], mod_jar_file)
                    print(f"\tDownloaded required/optional dependency at {mod_jar_file} successfully.")  # Print the success
                elif (mod_data['slug'] in mods) and (dependency['dependency_type'] == "incompatible"):
                    print(f"Incompatible dependency: {mod_data['slug']} installed, please remove.")
            mod_jar_file = Path(mod_path, f"{mod[0]}_version_{latest_version['version_number']}.jar")
            ModAPI.get_file(latest_version['files'][0]['url'], mod_jar_file)
            print(f"Downloaded mod at {mod_jar_file} successfully.")  # Print the success
            return True
    latest_version = check_update(mod, "0", game_version)  # Set the version to 0 so any version would be higher
    if latest_version:  # Should be True if it is a dict
        if ask(f"{mod} will take up: {latest_version['files'][0]['size']} bytes, would you like to install?"):
            for dependency in latest_version['dependencies']:
                mod_data = ModAPI.project(dependency['project_id'])
                if (mod_data['slug'] not in mods) and (dependency['dependency_type'] in ("required", "optional")):
                    dependency_latest_version = check_update(mod_data['slug'], 0, game_version)
                    mod_jar_file = Path(mod_path, f"{mod_data['slug']}_version_{dependency_latest_version['version_number']}.jar")
                    ModAPI.get_file(dependency_latest_version['files'][0]['url'], mod_jar_file)
                    print(f"\tDownloaded required/optional dependency at {mod_jar_file} successfully.")  # Print the success
                elif (mod_data['slug'] in mods) and (dependency['dependency_type'] == "incompatible"):
                    print(f"Incompatible dependency: {mod_data['slug']} installed, please remove.")
            mod_jar_file = Path(mod_path, f"{mod}_version_{latest_version['version_number']}.jar")
            ModAPI.get_file(latest_version['files'][0]['url'], mod_jar_file)
            print(f"Downloaded mod at {mod_jar_file} successfully.")  # Print the success
        else:
            print("Canceling.")
            return True
    else:
        logger.error("Mod does not exist on Modrinth for that version and/or loader")
        return False
    return True


def remove_mod(mod: str, mods: dict, mod_path: Path):
    """Removes a mod

    Arguments:
        mod -- The mod
        mods -- Dict of mods
        mod_path -- Path to the mods
    """
    if mod not in mods:  # If the mod is not installed
        logger.error("Mod not installed")
        return False
    try:
        mod_file = Path(mod_path, mods[mod]['file'])  # Path to the mod jar
        if ask(f"Would you like to remove {mod}? This operation will clear {mod_file.stat().st_size} bytes."):
            mod_file.unlink()  # Remove the file
        else:
            print("Canceling.")
            return False
    except PermissionError:  # No permission to delete the file
        logger.critical("No permission to delete mod file.")
        return False
    print(f"Mod: {mod}, successfully removed")  # Print success
    return True


def main():
    """Main function

    Returns:
        0: Success
        1: Failure
    """
    args = cli()
    logger.debug(args)
    try:
        mods = list_mods(args.mod_dir)
    except FileNotFoundError:
        logger.error("Mod folder: %s does not exist", args.mods_folder)
    logger.debug(mods)
    if args.up:
        if not update_mods(mods, args.mod_dir, args.game_version):
            return 1
    elif args.install:  # If were installing the mod
        if not install_mod(args.install, mods, args.mod_dir, args.game_version):
            return 1
    elif args.remove:  # If were removing the mod
        if not remove_mod(args.remove, mods, args.mod_dir):
            return 1
    elif args.list:  # List installed mod
        for name, mod in mods.items():  # Iterate over all installed mods
            print(f"{name}\n\tVersion: {mod['version']}\n\tFile: {mod['file']}")
    elif args.search:  # If we are searching for a mod
        facets = '[["categories:fabric"],["project_type:mod"]]'
        response = ModAPI.search(args.search, facets)
        for mod in response['hits']:  # Iterate over and list all the mods
            search = f"""{mod['title']}:
    Description: {mod['description']}
    Author: {mod['author']}
    Downloads: {mod['downloads']}
    Latest Version: {mod['latest_version']}

"""
            print(search)
    elif args.dependency:
        response = ModAPI.project_dependencies(args.dependency)
        for mod in response['projects']:
            dependency = f"""{mod['title']}:
    Description: {mod['description']}
    Downloads: {mod['downloads']}

"""
            print(dependency)
    elif args.project:
        response = ModAPI.project(args.project)
        info = f"""{response['slug']}
    Title: {response['title']}
    Description: {response['description']}
    Client Side: {response['client_side']}
"""
        print(info)
    else:
        logger.error("No arguments were passed, try '%s --help'", __package__)
    return 0  # Return 0 if all good
