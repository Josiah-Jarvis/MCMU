#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from re import match
from os import listdir
from pathlib import Path  # Import for file functions
from logging import getLogger, basicConfig  # Logging functionality
from requests import get  # Get files from the CDN
from argparse import ArgumentParser  # Command line arguments class
from importlib.metadata import version as get_version

logger = getLogger(__name__)
basicConfig(format="%(levelname)s: %(message)s")  # Set logging format

parser = ArgumentParser(
    prog="mcmu",
    description="Downloads Minecraft mods from Modrinth",
    epilog=f"Version: {get_version('mcmu')}"
)
group = parser.add_mutually_exclusive_group()  # Group for arguments
group.add_argument("-u", "--update", help="Updates installed mods", action="store_true")
group.add_argument("-r", "--remove", help="Removes an installed mod")
group.add_argument("-i", "--install", help="Installs a mod")
group.add_argument("-l", "--list", help="List installed mods", action="store_true")
group.add_argument("-s", "--search", help="Search packages on Modrinth")
group.add_argument("-d", "--dependency", help="List a mods dependency's")
# Unix systems defaults to ~/.minecraft/ for the minecraft dir, I don't know about Windows or MacOS
parser.add_argument("-m", "--minecraft_dir", default=Path(Path.home(), ".minecraft/"), help="Path to the Minecraft folder, defaults to '~/.minecraft/'")
# Game version defaults to 1.21.11 as it is the latest Minecraft release
parser.add_argument("-g", "--game_version", default="26.1", help="The game version to use to install mods, defaults to '26.1'")

args = parser.parse_args()  # Parser the arguments


def check_update(mod_name: str, current_version: str) -> [bool, dict]:
    """Checks for mod update from Modrinth

    Arguments:
        mod_name -- The name of the mod on Modrinth
        current_version -- The current installed version of the mod

    Returns:
        Returns:
            404: Mod does not exist
            False: Mod already at latest version
            Dict: Modrinth mod object
    """
    response = ModAPI.project_version(mod_name, '["fabric"]', f'["{args.game_version}"]')
    if response == 410:  # That means the API is deprecated: https://docs.modrinth.com/api/
        logger.critical("API is deprecated, you probably have to update MCMU")
        sys.exit(1)
    elif response == 404:  # Response 404 if mod not found: https://docs.modrinth.com/api/operations/getprojectversions/
        logger.error("Mod does not exist on Modrinth")
        sys.exit(1)
    latest_version = None  # Set the latest_version to None to indicate no newer version found yet
    for version in response:  # Check each mod version in the returned data
        if latest_version is None or version["version_number"] > latest_version["version_number"]:  # Check to see if version newer
            latest_version = version  # If it is set latest_version to the newer version
    if latest_version is not None and latest_version["version_number"] != current_version:  # Return latest version if it is newer than the current version
        return latest_version
    return False  # Return false for failure


def list_mods(mod_path: Path):
    mods = {}
    for mod in listdir(mod_path):
        m = match(r'^(.*?)_version_(.*)\.jar$', mod)
        mods[m.group(1)] = {
            "name": m.group(1),
            "version": m.group(2),
            "file": mod
        }

    return mods


def install_mod(file: str, path: Path):
    response = get(file, stream=True)  # Get mod jar file
    if response.status_code != 200:
        return False
    with open(path, 'wb') as file:  # Write to the jar file
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
    return True


class ModrinthAPI:
    def __init__(self, UserAgent: str):
        self.headers = {'User-Agent': UserAgent}

    def search(self, query: str, facets: str) -> [dict, int]:
        """Search's Mod on Modrinth: https://docs.modrinth.com/api/operations/searchprojects/

        Arguments:
            query -- The query string
            facets -- Used to limit the search results see Modrinth API documentation

        Returns:
            dict: Response data
            int:
                410: API deprecated
                400: Search invalid
        """
        parameters = {
            'query': query,
            'facets': facets,
            'limit': "100"
        }
        response = get(url="https://api.modrinth.com/v2/search", params=parameters, headers=self.headers)
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()

    def project(self, slug: str) -> [dict, int]:
        """Get data about a project: https://docs.modrinth.com/api/operations/getproject/

        Arguments:
            slug -- The slug of the project

        Returns:
            dict: Project data
            int:
                410: API deprecated
                404: Project not found
        """
        response = get(url=f"https://api.modrinth.com/v2/project/{slug}", headers=self.headers)
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()

    def project_dependencies(self, slug: str) -> [dict, int]:
        """Get a list of a projects dependencies: https://docs.modrinth.com/api/operations/getdependencies/

        Arguments:
            slug -- The slug of the project

        Returns:
            dict: Dependency information
            int:
                410: API deprecated
                404: Project not found
        """
        response = get(url=f"https://api.modrinth.com/v2/project/{slug}/dependencies", headers=self.headers)
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()

    def project_version(self, slug: str, loaders: str, game_version: str) -> [dict, int]:
        """List a projects versions: https://docs.modrinth.com/api/operations/getprojectversions/

        Arguments:
            slug -- The slug of the project
            loaders -- Loaders to filter for
            game_version -- Game versions to filter for

        Returns:
            dict: Project version data
            int:
                410: API deprecated
                404: Project not found
        """
        parameters = {
            'loaders': loaders,
            'game_versions': game_version,
            'include_changelog': 'false'
        }
        response = get(url=f"https://api.modrinth.com/v2/project/{slug}/version", params=parameters, headers=self.headers)
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()
    
    def get_project_version(self, slug: str, version_number: str, loaders: str, game_version: str) -> [dict, int]:
        response = get(url=f"https://api.modrinth.com/v2/project/{slug}/version/{version_number}", params=parameters, headers=self.headers)
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()  


ModAPI = ModrinthAPI(f"Josiah-Jarvis/MCMU/{get_version('mcmu')} (https://github.com/Josiah-Jarvis/MCMU)")


def main():
    """Main function

    Returns:
        0: Success
        1: Failure
    """
    mod_path = Path(args.minecraft_dir, "mods/")  # Path to folder where the mod jar's are stored
    mods = list_mods(mod_path)
    if not mod_path.exists():
        logger.critical(f"Mods folder: {mod_path} does not exist. Please create it.\nExiting...")  # Fabric creates the mods/ folder on first run by they might not have run it yet
        return 1
    if args.update:
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
                            if install_mod(dependency_latest_version['files'][0]['url'], mod_jar_file):
                                print(f"\tDownloaded required dependency at {mod_jar_file} successfully.")  # Print the success
                            else:
                                print("Failed to download required dependency.")
                                return 1
                        elif (mod_data['slug'] not in mods) and (dependency['dependency_type'] == "optional"):
                            dependency_latest_version = check_update(mod_data['slug'], 0)
                            print(f"Optional dependency: {mod_data['slug']} not installed")
                        elif (mod_data['slug'] in mods) and (dependency['dependency_type'] == "incompatible"):
                            print(f"Incompatible dependency: {mod_data['slug']} installed, please remove.")
                            return 1
                    mod_jar_file = Path(mod_path, f"{args.install}_version_{latest_version['version_number']}.jar")
                    if install_mod(latest_version['files'][0]['url'], mod_jar_file):
                        print(f"Downloaded mod at {mod_jar_file} successfully.")  # Print the success
                        print(f"Deleting old file: {old_file}")
                        old_file.unlink()  # Delete old file
                    else:
                        print("Failed to download the mod.")
                        return 1
                else:
                    print("Canceling.")
                    return 0
            else:
                print(f"Mod: {mod_name} at latest version!")
    elif args.install:  # If were installing the mod
        if args.install in mods:  # If mod already installed exit
            print(f"{args.install} already installed.")
            return 0
        latest_version = check_update(args.install, "0")  # Set the version to 0 so any version would be higher
        if latest_version is None:  # If it is None no mod exists for that version and or loader
            print("No version found for the specified game version and loader.")
            return 1
        if latest_version:  # Should be True if it is a dict
            if input(f"{args.install} will take up: {latest_version['files'][0]['size']} bytes, would you like to install? [Y/n]: ") is ("" or "Y"):  # Ask if the want to install it
                for dependency in latest_version['dependencies']:
                    mod_data = ModAPI.project(dependency['project_id'])
                    if (mod_data['slug'] not in mods) and (dependency['dependency_type'] == "required"):
                        dependency_latest_version = check_update(mod_data['slug'], 0)
                        mod_jar_file = Path(mod_path, f"{mod_data['slug']}_version_{dependency_latest_version['version_number']}.jar")
                        if install_mod(dependency_latest_version['files'][0]['url'], mod_jar_file):
                            print(f"\tDownloaded required dependency at {mod_jar_file} successfully.")  # Print the success
                        else:
                            print("Failed to download required dependency.")
                            return 1
                    elif (mod_data['slug'] not in mods) and (dependency['dependency_type'] == "optional"):
                        dependency_latest_version = check_update(mod_data['slug'], 0)
                        print(f"Optional dependency: {mod_data['slug']} not installed")
                    elif (mod_data['slug'] in mods) and (dependency['dependency_type'] == "incompatible"):
                        print(f"Incompatible dependency: {mod_data['slug']} installed, please remove.")
                        return 1
                mod_jar_file = Path(mod_path, f"{args.install}_version_{latest_version['version_number']}.jar")
                if install_mod(latest_version['files'][0]['url'], mod_jar_file):
                    print(f"Downloaded mod at {mod_jar_file} successfully.")  # Print the success
                else:
                    print("Failed to download the mod.")
                    return 1
            else:
                print("Canceling.")
                return 0
        else:
            logger.error("Mod does not exist on Modrinth")
            return 1
    elif args.remove:  # If were removing the mod
        if args.remove not in mods:  # If the mod is not installed
            logger.error("Mod not installed")
            return 1
        try:
            mod_file = Path(mod_path, mods[args.remove]['file'])  # Path to the mod jar
            if input(f"Would you like to remove {args.remove}? This operation will clear {mod_file.stat().st_size} bytes. [Y/n]: ") is ("" or "Y"):  # Ask if they want to remove it
                mod_file.unlink()  # Remove the file
            else:
                print("Canceling.")
                return 0
        except PermissionError:  # No permission to delete the file
            logger.critical("No permission to delete mod file.")
            return 1
        print(f"Mod: {args.remove}, successfully removed")  # Print success
        return 0
    elif args.list:  # List installed mod
        for mod in mods:  # Iterate over all installed mods
            print(f"{mods[mod]['name']}\n\tVersion: {mods[mod]['version']}\n\tFile: {mods[mod]['file']}")
    elif args.search:  # If we are searching for a mod
        response = ModAPI.search(args.search, '[["categories:fabric"],["project_type:mod"]]')
        if response == 410:  # That means the API is deprecated: https://docs.modrinth.com/api/
            logger.critical("API is deprecated, try updating MCMU")
        elif response == 400:  # Response of 400 means request was invalid: https://docs.modrinth.com/api/operations/searchprojects/
            logger.error("Request invalid")  # Print error
        else:
            for mod in response['hits']:  # Iterate over and list all the mods
                print(f"{mod['title']}:\n\tDescription: {mod['description']}\n\tAuthor: {mod['author']}\n\tDownloads: {mod['downloads']}\n\tLatest Version: {mod['latest_version']}\n\n")
    elif args.dependency:
        response = ModAPI.project_dependencies(args.dependency)
        if response == 410:  # That means the API is deprecated: https://docs.modrinth.com/api/
            logger.critical("API is deprecated, try updating MCMU")
        elif response == 404:  # Response of 400 means request was invalid: https://docs.modrinth.com/api/operations/searchprojects/
            logger.error("Mod not found on Modrinth")  # Print error
        else:
            for mod in response['projects']:
                print(f"{mod['title']}:\n\tDescription: {mod['description']}\n\tDownloads: {mod['downloads']}\n\n")
    else:
        parser.print_help()  # Prints help message if there is nothing to do

    return 0  # Return 0 if all good
