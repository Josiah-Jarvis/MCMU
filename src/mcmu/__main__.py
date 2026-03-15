#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from copy import copy  # Import copy
from json import load, dump, JSONDecodeError  # Import JSON functions
from pathlib import Path  # Import for file functions
from logging import getLogger, basicConfig  # Logging functionality
from requests import get  # Get object from the API
from argparse import ArgumentParser  # Command line arguments class

__version__ = "1.3.0"
__author__ = "Josiah Jarvis"

logger = getLogger(__name__)
basicConfig(format="%(levelname)s: %(message)s")  # Set logging config

parser = ArgumentParser(prog="mcmu")
group = parser.add_mutually_exclusive_group()  # Get mutually exclusive group set up
group.add_argument("-u", "--update", help="Updates installed mods", action="store_true")
group.add_argument("-r", "--remove", help="Removes an installed mod")
group.add_argument("-i", "--install", help="Installs a mod")
group.add_argument("-l", "--list", help="List installed mods", action="store_true")
group.add_argument("-s", "--search", help="Search packages on Modrinth")
group.add_argument("-v", "--version", action="version", version=f"MCMU version: {__version__}")
# Unix systems defaults to ~/.minecraft/ for the minecraft dir, I don't know about Windows or MacOS
parser.add_argument("-m", "--minecraft_dir", default=Path(Path.home(), ".minecraft/"), help="Path to the Minecraft folder, defaults to '~/.minecraft/'")
# Game version defaults to 1.21.11 as it is the latest Minecraft release
parser.add_argument("-g", "--game_version", default="26.1", help="The game version to use to install mods, defaults to '26.1'")

args = parser.parse_args()  # Parser the arguments
config_file = Path(args.minecraft_dir, "config/mcmu.json")  # Path to the config file

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
    parameters = {
            "loaders": '["fabric"]',
            "game_versions": f'["{args.game_version}"]',
            "include_changelog": "false"
    }
    response = get(f"https://api.modrinth.com/v2/project/{mod_name}/version", params=parameters)  # Get the mod from Modrinth
    if response.status_code == 404:  # Response 404 if mod not found: https://docs.modrinth.com/api/operations/getprojectversions/
        return 404
    project_info = response.json()  # Get the JSON from the request
    latest_version = None  # Set the latest_version to None to indicate no newer version found yet
    for version in project_info:  # Check each mod version in the returned data
        if latest_version is None or version["version_number"] > latest_version["version_number"]:  # Check to see if version newer
            latest_version = version  # If it is set latest_version to the newer version
    if latest_version is not None and latest_version["version_number"] != current_version:  # Return latest version if it is newer than the current version
        return latest_version
    return False  # Return false for failure

def write_config_file(config_f: Path, config_d: dict):
    """Writes the config file

    Arguments:
        config_f -- The config file
        config_d -- The config data

    Returns:
        True: Success
        False: Failure
    """
    try:
        with open(config_f, "w") as fp:  # Open the config file
            dump(config_d, fp, indent=4)  # Write the config file
            return True
    except PermissionError:  # Uh oh we do not have permission
        logger.error("No permission to write to file.")
        return False

def main():
    """Main function

    Returns:
        1: Failure
        0: Success
    """
    try:
        with open(config_file, "r") as fp:  # Open the config file
            config = load(fp)  # Read the config file
    except JSONDecodeError:
        logger.critical("Config file not valid JSON.")  # Welp its not valid JSON
        return 1
    except FileNotFoundError:  # Oops config file does not exist
        logger.warn("Config file does not exist.")
        with open(config_file, "w") as fp:  # Create the file since it does not exist
            logger.debug("Creating config file.")
            dump({"mods":{}}, fp, indent=4)
        logger.info("Exiting, please re-run.")
        return 1
    except PermissionError:  # Can't we just have the permission :?
        logger.error("No permission to write to file.")
        return 1
    mods = copy(config['mods'])  # Get the mods data from the config file
    mod_path = Path(args.minecraft_dir, "mods/")  # Path to folder where the mod jar's are stored
    if not mod_path.exists():
        logger.critical(f"Mods folder: {mod_path} does not exist. Please create it.\nExiting...")  # Fabric creates the mods/ folder on first run by they might not have run it yet
        return 1
    if args.update:
        for mod_name in mods:
            latest_version = check_update(mod_name, mods[mod_name]['version'])  # Check for update
            if latest_version == 404:  # Thats weird, maybe the user tampered with the config file or the mod was deleted
                print("Mod does not exist on Modrinth.")
                sys.exit(1)
            elif latest_version is None:  # If latest version is None no newer version was found
                print("No version found for the specified game version and loader.")
                return 1
            elif latest_version:  # If latest version is a dict it should return True
                old_file = Path(mod_path, mods[mod_name]['file'])  # Path to the old mod file
                additional_storage = latest_version['files'][0]['size'] - old_file.stat().st_size  # Calculate how much more storage will be taken up
                if input(f"{args.install} will take up: {additional_storage} additional bytes, would you like to install? [Y/n]: ") is ("" or "Y"):  # Ask them if they want to install it
                    old_file.unlink()  # Delete old file
                    response = get(latest_version['files'][0]['url'], stream=True)  # Get the new file
                    if response.status_code != 200:  # If its not 200 fail
                        print(f"Failed to download the mod. Status code: {response.status_code}")
                        return 1
                    with open(f"{mod_path}/{latest_version['files'][0]['filename']}", 'wb') as file:  # IF everything good write to the file
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                file.write(chunk)
                    print(f"Downloaded {latest_version['files'][0]['filename']} successfully.")  # Print the success
                    config['mods'][mod_name] = {'file': latest_version['files'][0]['filename'], 'version': latest_version['version_number'], 'name': mod_name}
                    if not write_config_file(config_file, config):  # Write the config file
                        return 1  # Fail if writing failed
                else:
                    print("Canceling.")
                    return 0
            else:
                print(f"Mod: {mod_name} at latest version!")
    elif args.install:  # If were installing the mod
        if args.install in config['mods']:  # If mod already installed exit
            print(f"{args.install} already installed.")
            return 0
        latest_version = check_update(args.install, "0")  # Set the version to 0 so any version would be higher
        if latest_version is None:  # If it is None no mod exists for that version and or loader
            print("No version found for the specified game version and loader.")
            return 1
        if latest_version:  # Should be True if it is a dict
            if input(f"{args.install} will take up: {latest_version['files'][0]['size']} bytes, would you like to install? [Y/n]: ") is ("" or "Y"):  # Ask if the want to install it
                response = get(latest_version['files'][0]['url'], stream=True)  # Get mod jar file
                if response.status_code != 200:
                    print(f"Failed to download the mod. Status code: {response.status_code}")
                    return False
                with open(f"{mod_path}/{latest_version['files'][0]['filename']}", 'wb') as file:  # Write to the jar file
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                print(f"Downloaded {latest_version['files'][0]['filename']} successfully.")  # Print the success
                config['mods'][args.install] = {'file': latest_version['files'][0]['filename'], 'version': latest_version['version_number'], 'name': args.install}
                if not write_config_file(config_file, config):  # Write to the config file
                    return 1
            else:
                print("Canceling.")
                return 0
        else:
            logger.error("Mod does not exist on Modrinth")
            return 1
    elif args.remove:  # If were removing the mod
        if args.remove not in config['mods']:  # If the mod is not listed in the config file exit with error
            logger.error("Mod not installed")
            return 1
        try:
            mod_file = Path(mod_path, config['mods'][args.remove]['file'])  # Path to the mod jar
            if input(f"Would you like to remove {args.remove}? This operation will clear {mod_file.stat().st_size} bytes. [Y/n]: ") is ("" or "Y"):  # Ask if they want to remove it
                mod_file.unlink()  # Remove the file
            else:
                print("Canceling.")
                return 0
        except FileNotFoundError:  # Oops file not found must already be deleted
            logger.warn("Mod's file already deleted.")
        except PermissionError:  # No permission to delete the file
            logger.critical("No permission to delete mod file.")
            return 1
        del config['mods'][args.remove]  # Remove the mods entry in the config file
        if not write_config_file(config_file, config):  # Write to the config file
            return 1
        print(f"Mod: {args.remove}, successfully removed")  # Print success
        return 0
    elif args.list:  # List installed mod
        for mod in config['mods']:  # Iterate over all installed mods
            print(f"{config['mods'][mod]['name']}\n\tVersion: {config['mods'][mod]['version']}\n\tFile: {config['mods'][mod]['file']}")
    elif args.search:  # If we are searching for a mod
        parameters = {
            "query": args.search,
            "facets": '[["categories:fabric"],["project_type:mod"]]'
        }  # Set up params for the query
        response = get("https://api.modrinth.com/v2/search", params=parameters)  # Query the API
        if response.status_code == 400:  # Response of 400 means request was invalid: https://docs.modrinth.com/api/operations/searchprojects/
            logger.error(f"Query failed with error: {response.text}")  # Print error
        else:
            for mod in response.json()['hits']:  # Iterate over and list all the mods
                print(f"{mod['title']}:\n\tDescription: {mod['description']}\n\tAuthor: {mod['author']}\n\tDownloads: {mod['downloads']}\n\tLatest Version: {mod['latest_version']}\n\n")
    else:
        parser.print_help()  # Prints help message if there is nothing to do

    return 0 # Return 0 if all good
