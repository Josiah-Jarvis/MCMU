#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A script to download mods from Modrinth"""

from re import match, Match
from os import listdir, getenv, replace, mkdir, environ
from pathlib import Path
from logging import getLogger, basicConfig, INFO, DEBUG
from requests import get
from platform import system
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from importlib.metadata import version as get_version

logger = getLogger(__name__)
logger.setLevel(INFO)
basicConfig(format="%(levelname)s: %(message)s")  # Set logging format


def cli() -> dict:
    """Parses command line arguments"""
    try:
        environ['MCMU_MOD_PATH']
    except KeyError:
        if system() == "Linux":
            mod_dir = Path(Path.home(), ".minecraft/mods/")
        elif system() == "Darwin":
            mod_dir = Path(
                Path.home(), "Library/Application Support/minecraft/mods/"
            )
        elif system() == "Windows":
            mod_dir = Path(getenv('APPDATA'), ".minecraft\\mods\\")
        else:
            logger.warning("System %s not known.", system())
            mod_dir = Path(Path.home(), ".minecraft/mods/")
    else:
        mod_dir = environ['MCMU_MOD_PATH']
        logger.info(
            "Mod dir set to %s because of environment variable.",
            mod_dir
        )
    try:
        environ['MCMU_GAME_VERSION']
    except KeyError:
        game_version = "26.1.2"
    else:
        game_version = environ['MCMU_GAME_VERSION']
        logger.info(
            "Game version set to %s because of environment variable.",
            game_version
        )

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
    group.add_argument("-p", "--project", help="Get info about a project")
    group.add_argument("-e", "--enable", help="Enable a mod")
    group.add_argument("-d", "--disable", help="Disable a mod")
    parser.add_argument(
        "--mod-dir",
        default=mod_dir,
        help="Path to the Minecraft mods folder"
    )
    parser.add_argument(
        "--game-version",
        default=game_version,
        help="The game version to use to install mods"
    )
    parser.add_argument(
        "--enable-experimental-features",
        default="false",
        help="Enable experimental features",
        action="store_true"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Increase logging level",
        action="store_true"
    )
    return parser.parse_args()  # Parser the arguments


def ask(question: str) -> bool:
    """Ask a question"""
    answer = input(f"{question} [Y/n]: ").lower()
    if answer in ("y", ""):  # Check if answer was Y, y or ""
        return True  # Return 'yes'
    return False  # Return 'no'


def check_update(
    mod_name: str,  # The name of the mod on Modrinth
    current_version: str,  # The current installed version of the mod
    game_version: str  # Game version to look for
) -> [bool, dict]:  # Modrinth mod object or False if already at latest version
    """Checks for mod update from Modrinth"""
    response = ModAPI.project_version(
        mod_name, '["fabric"]', f'["{game_version}"]'
    )
    latest_version = {}  # None to indicate no newer version found yet
    for version in response:  # Check each mod version in the returned data
        if latest_version == {} or version["version_number"] > latest_version["version_number"]:  # Check to see if version newer
            latest_version = version  # Set to latest version
    if latest_version != {} and latest_version["version_number"] != current_version:  # Return latest version if it is newer than the current version
        return latest_version
    return False  # Return false for failure


def list_mods(mod_path: Path) -> [Match, bool]:
    """Gets a list of installed mods"""
    mods = {}
    mods_disabled = {}
    for mod in listdir(mod_path):
        m = match(r'^(.*?)_version_(.*)\.jar$', str(mod))
        try:
            mods[m.group(1)] = {
                "name": m.group(1),
                "version": m.group(2),
                "file": mod
            }
        except AttributeError as e:
            print(e)
            logger.info("Mod dir is empty, %s", e)
    try:
        for mod in listdir(Path(Path(mod_path), "mods_disabled/")):
            m = match(r'^(.*?)_version_(.*)\.jar$', str(mod))
            try:
                mods_disabled[m.group(1)] = {
                    "name": m.group(1),
                    "version": m.group(2),
                    "file": mod
                }
            except AttributeError as e:
                logger.info("Mod dir is empty, %s", e)
    except FileNotFoundError:
        mkdir(Path(Path(mod_path), "mods_disabled/"))
        mods_disabled = {}
    return mods, mods_disabled


class ModrinthAPI:
    """Modrinth API class"""
    def __init__(self):
        self.headers = {
            'User-Agent': f"Josiah-Jarvis/MCMU/{get_version(__package__)} (https://github.com/Josiah-Jarvis/MCMU)"
        }

    def query(
        self,
        endpoint: str = "https://api.modrinth.com/v2/",  # The API endpoint
        parameters: dict = None  # The parameters to pass the API
    ) -> dict:  # API json
        """Query's the Modrinth API

        Raises:
            DeprecationWarning: If response is 410
            UserWarning: If response is 400 or 404
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

    def search(
        self,
        query: str,  # The query string
        facets: str  # Used to limit the search results see
    ) -> [dict]:  # Response data
        """Search's Mod on Modrinth"""
        parameters = {
            'query': query,
            'facets': facets,
            'limit': "100"
        }
        return self.query("search", parameters)

    def project(
        self,
        slug: str  # The slug of the project
    ) -> [dict]:  # Project data
        """Get data about a project"""
        return self.query(f"project/{slug}")

    def project_dependencies(
        self,
        slug: str  # The slug of the project
    ) -> [dict]:  # Dependency information
        """Get a list of a projects dependencies"""
        return self.query(f"project/{slug}/dependencies")

    def project_version(
        self,
        slug: str,  # The slug of the project
        loaders: str,  # Loaders to filter for
        version: str  # Game versions to filter for
    ) -> [dict]:  # Project version data
        """List a projects versions"""
        parameters = {
            'loaders': loaders,
            'game_versions': version,
            'include_changelog': 'false'
        }
        return self.query(f"project/{slug}/version", parameters)

    def get_project_version(
        self,
        slug: str,  # The name of the project
        version_number: str  # The specific version of the project
    ) -> [dict]:  # The query's json
        """Get a specific version from a mod"""
        return self.query(f"project/{slug}/version/{version_number}")

    def get_file(
        self,
        file: str,  # The file to download
        path: Path  # The file to write to
    ) -> bool:  # True if success
        """Gets file from the CDN
        Raises:
            UserWarning: 404 code
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


def download_dependency_s(
    dependency_s: list,  # List of mods dependency's
    mods: list,  # List of installed mods
    mod_path: Path  # Path to the mods folder
):
    """Download a mods dependency's"""
    for dependency in dependency_s:
        mod_data = ModAPI.project(dependency['project_id'])
        if (mod_data['slug'] not in mods) and (dependency['dependency_type'] == "required"):
            dependency_latest_version = check_update(mod_data['slug'], 0, game_version)
            mod_jar_file = Path(mod_path, f"{mod_data['slug']}_version_{dependency_latest_version['version_number']}.jar")
            ModAPI.get_file(dependency_latest_version['files'][0]['url'], mod_jar_file)
            print(f"\tDownloaded required dependency at {mod_jar_file} successfully.")  # Print the success
        elif (mod_data['slug'] not in mods) and (dependency['dependency_type'] == "optional"):
            if ask(f"Would you like to install optional dependency: {mod_data['slug']}?"):
                dependency_latest_version = check_update(mod_data['slug'], 0, game_version)
                mod_jar_file = Path(mod_path, f"{mod_data['slug']}_version_{dependency_latest_version['version_number']}.jar")
                ModAPI.get_file(dependency_latest_version['files'][0]['url'], mod_jar_file)
                print(f"\tDownloaded optional dependency at {mod_jar_file} successfully.")  # Print the success
        elif (mod_data['slug'] in mods) and (dependency['dependency_type'] == "incompatible"):
            print(f"Incompatible dependency: {mod_data['slug']} installed, please remove.")


def update_mods(
    mods: dict,  # A dict of mods
    mod_path: Path,  # The path to the mods
    game_version  # The game version to install for
) -> bool:
    """Updates mods"""
    for mod_name in mods:
        latest_version = check_update(mod_name, mods[mod_name]['version'], game_version)  # Check for update
        if latest_version:  # If latest version is a dict it should be True
            old_file = Path(mod_path, mods[mod_name]['file'])  # Path to the old mod file
            additional_storage = latest_version['files'][0]['size'] - old_file.stat().st_size  # Calculate how much more storage will be taken up
            if ask(f"{mods[mod_name]['name']} will take up: {additional_storage} additional bytes, would you like to install?"):
                download_dependency_s(latest_version['dependencies'], mods, mod_path)
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


def install_mod(
        mod: str,  # The mod
        mods: dict,  # Dict of mods
        mod_path: Path,  # The path to the mods folder
        game_version: str,  # Game version to install for
        mods_disabled,  # List of disabled mods
) -> bool:
    """Installs a mod"""
    if (mod in mods) or (mod in mods_disabled):  # If mod already installed exit
        print(f"{mod} already installed.")
        return True
    mod_version = mod.split("==")
    if len(mod_version) > 1:
        mod = mod_version
        latest_version = ModAPI.get_project_version(mod[0], mod[1])
        if game_version not in latest_version['game_versions']:
            logger.error("%s version does not support this game version.", mod[1])
        if ask(f"{mod[0]} will take up: {latest_version['files'][0]['size']} bytes, would you like to install?"):
            download_dependency_s(latest_version['dependencies'], mods, mod_path)
            mod_jar_file = Path(mod_path, f"{mod[0]}_version_{latest_version['version_number']}.jar")
            ModAPI.get_file(latest_version['files'][0]['url'], mod_jar_file)
            print(f"Downloaded mod at {mod_jar_file} successfully.")  # Print the success
            return True
    latest_version = check_update(mod, "0", game_version)  # Set the version to 0 so any version would be higher
    if latest_version:  # Should be True if it is a dict with items
        if ask(f"{mod} will take up: {latest_version['files'][0]['size']} bytes, would you like to install?"):
            download_dependency_s(latest_version['dependencies'], mods, mod_path)
            mod_jar_file = Path(mod_path, f"{mod}_version_{latest_version['version_number']}.jar")
            ModAPI.get_file(latest_version['files'][0]['url'], mod_jar_file)
            print(f"Downloaded mod at {mod_jar_file} successfully.")  # Success
        else:
            print("Canceling.")
            return True
    else:
        logger.error("Mod does not exist for that version and loader")
        return False
    return True


def remove_mod(
    mod: str,  # The mod
    mods: dict,  # Dict of mods
    mod_path: Path  # Path to the mods
):
    """Removes a mod"""
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


def enable_mod(
    mod: str,  # Name of mod
    mod_list: list,  # List of mods
    disabled_mods_list: list,  # List of disabled mods
    mod_path: Path  # Mod path
) -> bool:
    """Enable a mod"""
    if mod in disabled_mods_list:
        if mod in mod_list:
            return False
        replace(
            Path(
                mod_path,
                "mods_disabled/",
                disabled_mods_list[mod]['file']
            ),
            Path(mod_path, disabled_mods_list[mod]['file'])
        )
    return True


def disable_mod(
    mod: str,  # Mod name
    mod_list: list,  # List of mods
    disabled_mods_list: list,  # List of disabled mods
    mod_path: Path  # Mod path
) -> bool:
    """Disable a mod"""
    if mod in mod_list:
        if mod in disabled_mods_list:
            return False
        replace(
            Path(mod_path, mod_list[mod]['file']),
            Path(
                mod_path, "mods_disabled/",
                mod_list[mod]['file']
            )
        )
    return True


def get_dependency(project: str) -> str:
    """Gets a mods dependency's"""
    response = ModAPI.project_dependencies(project)
    for mod in response['projects']:
        dependency = f"""\t{mod['title']}"""
        return dependency


def main():
    """Main function

    Returns:
        0: Success
        1: Failure
    """
    args = cli()
    if args.verbose:
        logger.setLevel(DEBUG)
    try:
        mods, mods_disabled = list_mods(args.mod_dir)
    except FileNotFoundError:
        logger.error("Mod folder: %s does not exist", args.mod_folder)
    if args.up:
        if not update_mods(mods, args.mod_dir, args.game_version):
            return 1
    elif args.install:  # If were installing the mod
        if not install_mod(
            args.install, mods, args.mod_dir, args.game_version,
            mods_disabled
        ):
            return 1
    elif args.remove:  # If were removing the mod
        if not remove_mod(args.remove, mods, args.mod_dir):
            return 1
    elif args.list:  # List installed mod
        for name, mod in mods.items():  # Iterate over all installed mods
            print(
                f"{name}\n\tVersion: {mod['version']}\n\tFile: {mod['file']}"
            )
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
    elif args.project:
        response = ModAPI.project(args.project)
        info = f"""{response['slug']}
    Title: {response['title']}
    Description: {response['description']}
    Client Side: {response['client_side']}
"""
        print(info)
        print("Dependency's:")
        print(get_dependency(args.project))
    elif args.enable:
        if enable_mod(args.enable, mods, mods_disabled, args.mod_dir):
            logger.info("Successfully enabled mod: %s", args.enable)
        else:
            return 1
    elif args.disable:
        if disable_mod(args.disable, mods, mods_disabled, args.mod_dir):
            logger.info("Successfully disabled mod: %s", args.disable)
        else:
            return 1
    else:
        logger.error("No arguments were passed, try '%s --help'", __package__)
    return 0  # Return 0 if all good


if __name__ == "__main__":
    def get_version():
        return "Terminal Test Edition"

    main()
