#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A script to download mods from Modrinth"""

from re import match
from os import listdir
from pathlib import Path
from logging import getLogger, basicConfig
from requests import get
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from importlib.metadata import version as get_version

logger = getLogger(__name__)
basicConfig(format="%(levelname)s: %(message)s")  # Set logging format

parser = ArgumentParser(
    description=__doc__,
    epilog=f"Version: {get_version('mcmu')}",
    formatter_class=ArgumentDefaultsHelpFormatter
)
group = parser.add_mutually_exclusive_group()  # Group for arguments
group.add_argument("-u", "--update", help="Updates a mod", action="store_true")
group.add_argument("-r", "--remove", help="Remove a mod")
group.add_argument("-i", "--install", help="Install a mod")
group.add_argument("-l", "--list", help="List mods", action="store_true")
group.add_argument("-s", "--search", help="Search mods on Modrinth")
group.add_argument("-d", "--dependency", help="List a mods dependency's")
parser.add_argument(
    "-m",
    "--minecraft_dir",
    default=Path(Path.home(), ".minecraft/"),
    help="Path to the Minecraft folder"
)
parser.add_argument(
    "-g",
    "--game_version",
    default="26.1",
    help="The game version to use to install mods"
)

args = parser.parse_args()  # Parser the arguments


def check_update(mod_name: str, current_version: str) -> [bool, dict]:
    """Checks for mod update from Modrinth

    Arguments:
        mod_name -- The name of the mod on Modrinth
        current_version -- The current installed version of the mod

    Returns:
        Returns:
            False: Mod already at latest version
            Dict: Modrinth mod object
    """
    response = ModAPI.project_version(mod_name, '["fabric"]', f'["{args.game_version}"]')
    latest_version = None  # Set the latest_version to None to indicate no newer version found yet
    for version in response:  # Check each mod version in the returned data
        if latest_version is None or version["version_number"] > latest_version["version_number"]:  # Check to see if version newer
            latest_version = version  # If it is set latest_version to the newer version
    if latest_version is not None and latest_version["version_number"] != current_version:  # Return latest version if it is newer than the current version
        return latest_version
    return False  # Return false for failure


def list_mods(mod_path: Path):
    """Gets a list of installed mods
    """
    mods = {}
    for mod in listdir(mod_path):
        m = match(r'^(.*?)_version_(.*)\.jar$', mod)
        mods[m.group(1)] = {
            "name": m.group(1),
            "version": m.group(2),
            "file": mod
        }
    return mods


class ModrinthAPI:
    """Modrinth API class
    """
    def __init__(self, user_agent: str):
        self.headers = {'User-Agent': user_agent}

    def query(self, endpoint: str, parameters: dict = None) -> dict:
        """Query's the Modrinth API

        Arguments:
            endpoint -- The API endpoint

        Keyword Arguments:
            parameters -- The parameters to pass to requests.get() (default: {None})

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
        if response.status_code == 410:
            raise DeprecationWarning("API deprecated")
        if response.status_code == 404:
            raise UserWarning(f"Mod: {endpoint} not found")
        if response.status_code == 400:
            raise UserWarning("API request invalid")
        return response.json()

    def search(self, query: str, facets: str) -> [dict]:
        """Search's Mod on Modrinth: https://docs.modrinth.com/api/operations/searchprojects/

        Arguments:
            query -- The query string
            facets -- Used to limit the search results see Modrinth API documentation

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
        """Get data about a project: https://docs.modrinth.com/api/operations/getproject/

        Arguments:
            slug -- The slug of the project

        Returns:
            dict: Project data
        """
        return self.query(f"project/{slug}")

    def project_dependencies(self, slug: str) -> [dict]:
        """Get a list of a projects dependencies: https://docs.modrinth.com/api/operations/getdependencies/

        Arguments:
            slug -- The slug of the project

        Returns:
            dict: Dependency information
        """
        return self.query(f"project/{slug}/dependencies")

    def project_version(self, slug: str, loaders: str, game_version: str) -> [dict]:
        """List a projects versions: https://docs.modrinth.com/api/operations/getprojectversions/

        Arguments:
            slug -- The slug of the project
            loaders -- Loaders to filter for
            game_version -- Game versions to filter for

        Returns:
            dict: Project version data
        """
        parameters = {
            'loaders': loaders,
            'game_versions': game_version,
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
        response = get(file, stream=True, timeout=10, headers=self.headers)  # Get mod jar file
        if response.status_code == 404:
            raise UserWarning("Version file failed to download")
        with open(path, 'wb') as file:  # Write to the jar file
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        return True


ModAPI = ModrinthAPI(
    f"Josiah-Jarvis/MCMU/{get_version('mcmu')} (https://github.com/Josiah-Jarvis/MCMU)"
)


def update_mods(mods: dict, mod_path: Path):
    """Updates mods

    Arguments:
        mods -- A dict of mods
        mod_path -- The path to the mods

    Returns:
        1 or 0
    """
    for mod_name in mods:
        latest_version = check_update(mod_name, mods[mod_name]['version'])  # Check for update
        if latest_version is None:  # If latest version is None no newer version was found
            print("No version found for the specified game version and loader.")
        elif latest_version:  # If latest version is a dict it should return True
            old_file = Path(mod_path, mods[mod_name]['file'])  # Path to the old mod file
            additional_storage = latest_version['files'][0]['size'] - old_file.stat().st_size  # Calculate how much more storage will be taken up
            if input(f"{mods[mod_name]['name']} will take up: {additional_storage} additional bytes, would you like to install? [Y/n]: ") is ("" or "Y"):  # Ask them if they want to install it
                for dependency in latest_version['dependencies']:
                    mod_data = ModAPI.project(dependency['project_id'])
                    if (mod_data['slug'] not in mods) and (dependency['dependency_type'] == "required"):
                        dependency_latest_version = check_update(mod_data['slug'], 0)
                        mod_jar_file = Path(mod_path, f"{mod_data['slug']}_version_{dependency_latest_version['version_number']}.jar")
                        ModAPI.get_file(dependency_latest_version['files'][0]['url'], mod_jar_file)
                        print(f"\tDownloaded required dependency at {mod_jar_file} successfully.")  # Print the success
                    elif (mod_data['slug'] not in mods) and (dependency['dependency_type'] == "optional"):
                        dependency_latest_version = check_update(mod_data['slug'], 0)
                        print(f"Optional dependency: {mod_data['slug']} not installed")
                    elif (mod_data['slug'] in mods) and (dependency['dependency_type'] == "incompatible"):
                        print(f"Incompatible dependency: {mod_data['slug']} installed, please remove.")
                        return 1
                mod_jar_file = Path(mod_path, f"{mod_name}_version_{latest_version['version_number']}.jar")
                ModAPI.get_file(latest_version['files'][0]['url'], mod_jar_file)
                print(f"Downloaded mod at {mod_jar_file} successfully.")  # Print the success
                print(f"Deleting old file: {old_file}")
                old_file.unlink()  # Delete old file
            else:
                print("Canceling.")
                return 0
        else:
            print(f"Mod: {mod_name} at latest version!")


def install_mod(mod: str, mods: dict, mod_path: Path):
    """Installs a mod

    Arguments:
        mod -- The mod
        mods -- Dict of mods
        mod_path -- The path to the mods folder

    Returns:
        1 or 0
    """
    if args.install in mods:  # If mod already installed exit
        print(f"{mod} already installed.")
        return 0
    latest_version = check_update(mod, "0")  # Set the version to 0 so any version would be higher
    if latest_version is None:  # If it is None no mod exists for that version and or loader
        print("No version found for the specified game version and loader.")
        return 1
    if latest_version:  # Should be True if it is a dict
        if input(f"{mod} will take up: {latest_version['files'][0]['size']} bytes, would you like to install? [Y/n]: ") is ("" or "Y"):  # Ask if the want to install it
            for dependency in latest_version['dependencies']:
                mod_data = ModAPI.project(dependency['project_id'])
                if (mod_data['slug'] not in mods) and (dependency['dependency_type'] == "required"):
                    dependency_latest_version = check_update(mod_data['slug'], 0)
                    mod_jar_file = Path(mod_path, f"{mod_data['slug']}_version_{dependency_latest_version['version_number']}.jar")
                    ModAPI.get_file(dependency_latest_version['files'][0]['url'], mod_jar_file)
                    print(f"\tDownloaded required dependency at {mod_jar_file} successfully.")  # Print the success
                elif (mod_data['slug'] not in mods) and (dependency['dependency_type'] == "optional"):
                    dependency_latest_version = check_update(mod_data['slug'], 0)
                    print(f"Optional dependency: {mod_data['slug']} not installed")
                elif (mod_data['slug'] in mods) and (dependency['dependency_type'] == "incompatible"):
                    print(f"Incompatible dependency: {mod_data['slug']} installed, please remove.")
                    return 1
            mod_jar_file = Path(mod_path, f"{mod}_version_{latest_version['version_number']}.jar")
            ModAPI.get_file(latest_version['files'][0]['url'], mod_jar_file)
            print(f"Downloaded mod at {mod_jar_file} successfully.")  # Print the success
        else:
            print("Canceling.")
            return 0
    else:
        logger.error("Mod does not exist on Modrinth")
        return 1


def remove_mod(mod: str, mods: dict, mod_path: Path):
    """Removes a mod

    Arguments:
        mod -- The mod
        mods -- Dict of mods
        mod_path -- Path to the mods

    Returns:
        1 or 0
    """
    if mod not in mods:  # If the mod is not installed
        logger.error("Mod not installed")
        return 1
    try:
        mod_file = Path(mod_path, mods[mod]['file'])  # Path to the mod jar
        if input(f"Would you like to remove {mod}? This operation will clear {mod_file.stat().st_size} bytes. [Y/n]: ") is ("" or "Y"):  # Ask if they want to remove it
            mod_file.unlink()  # Remove the file
        else:
            print("Canceling.")
            return 0
    except PermissionError:  # No permission to delete the file
        logger.critical("No permission to delete mod file.")
        return 1
    print(f"Mod: {mod}, successfully removed")  # Print success
    return 0


def main():
    """Main function

    Returns:
        0: Success
        1: Failure
    """
    mod_path = Path(args.minecraft_dir, "mods/")  # Path to folder where the mod jar's are stored
    mods = list_mods(mod_path)
    if not mod_path.exists():
        logger.critical("Mods folder: %s does not exist. Please create it.\nExiting...", mod_path)  # Fabric creates the mods/ folder on first run by they might not have run it yet
        return 1
    if args.update:
        update_mods(mods, mod_path)
    elif args.install:  # If were installing the mod
        install_mod(args.install, mods, mod_path)
    elif args.remove:  # If were removing the mod
        remove_mod(args.remove, mods, mod_path)
    elif args.list:  # List installed mod
        for name, mod in mods.items():  # Iterate over all installed mods
            print(f"{name}\n\tVersion: {mod['version']}\n\tFile: {mod['file']}")
    elif args.search:  # If we are searching for a mod
        response = ModAPI.search(args.search, '[["categories:fabric"],["project_type:mod"]]')
        for mod in response['hits']:  # Iterate over and list all the mods
            print(f"{mod['title']}:\n\tDescription: {mod['description']}\n\tAuthor: {mod['author']}\n\tDownloads: {mod['downloads']}\n\tLatest Version: {mod['latest_version']}\n\n")
    elif args.dependency:
        response = ModAPI.project_dependencies(args.dependency)
        for mod in response['projects']:
            print(f"{mod['title']}:\n\tDescription: {mod['description']}\n\tDownloads: {mod['downloads']}\n\n")
    else:
        parser.print_help()  # Prints help message if there is nothing to do
    return 0  # Return 0 if all good
