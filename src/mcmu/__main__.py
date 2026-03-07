#!/usr/bin/env python3

import argparse
import requests
import json
import sys
import re
from pathlib import Path
from urllib.parse import urlsplit

__version__ = "0.2.1"
game_version = "1.21.11"
__author__ = "Josiah Jarvis"

def cmd():
    parser = argparse.ArgumentParser(
        prog="MCModUpdater",
        epilog="..."
    )
    subparsers = parser.add_subparsers()
    update_parser = subparsers.add_parser("update",)
    remove_parser = subparsers.add_parser("remove")
    install_parser = subparsers.add_parser("install")
    update_parser.add_argument("-n", "--now", action="store_true")
    remove_parser.add_argument("remove_package")
    install_parser.add_argument("install_package")
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("-m", "--mod_path", default=Path(Path.home(), ".minecraft/mods"))
    parser.add_argument("-g", "--game_version", default=game_version)
    parser.add_argument("-c", "--config", default=Path(Path.home(), ".minecraft/config/mcmodupdater.json"))

    return parser.parse_args()


class Mod:
    def __init__(self, mod_name: str, game_version: str, loader: str = "fabric"):
        self.name = mod_name
        self.version = game_version
        self.loader = loader
        self.parameters = {
            "loaders": [self.loader],
            "game_versions": [self.version],
            "include_changelog": "false"
        }

    def check_update(self, current_version):
        response = requests.get(f"https://api.modrinth.com/v2/project/{self.name}/version", params=self.parameters)
        if response.status_code == 404:
            print("404 Mod not found")
            sys.exit(1)

        project_info = response.json()
        latest_version = None
        for version in project_info:
            if self.version in version["game_versions"] and self.loader in version["loaders"]:
                if latest_version is None or version["version_number"] > latest_version["version_number"]:
                    latest_version = version

        if latest_version is not None and latest_version["version_number"] != current_version:
            return True
        return False

    def exists(self):
        parameters = {
            "loaders": [self.loader],
            "game_versions": [self.version],
            "include_changelog": "false"
        }
        response = requests.get(f"https://api.modrinth.com/v2/project/{self.name}/version", params=self.parameters)
        if response.status_code == 404:
            return False
        else:
            return True

    def install(self, mod_path):
        response = requests.get(f"https://api.modrinth.com/v2/project/{self.name}/version", params=self.parameters)
        if response.status_code != 200:
            print(f"Failed to retrieve project information. Status code: {response.status_code}")
            return

        project_info = response.json()
        latest_version = None
        for version in project_info:
            if self.version in version["game_versions"] and self.loader in version["loaders"]:
                if latest_version is None or version["version_number"] > latest_version["version_number"]:
                    latest_version = version

        if latest_version is None:
            print("No version found for the specified game version and loader.")
            return

        response = requests.get(latest_version['files'][0]['url'], stream=True)
        if response.status_code != 200:
            print(f"Failed to download the mod. Status code: {response.status_code}")
            return False
        with open(Path(mod_path, latest_version['files'][0]['filename']), 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

        print(f"Downloaded {latest_version['files'][0]['filename']} successfully.")
        return {'file': latest_version['files'][0]['filename'], 'version': latest_version['version_number'], 'name': latest_version['name']}

    def delete(self, mod_path, mod_file):
        Path(mod_path, mod_file).unlink()

    def update(self, mod_path, mod_file):
        print(f"Deleting {mod_path}{mod_file}...")
        self.delete(mod_path, mod_file)
        print("Deleted.")
        print(f"Installing latest version...")
        return self.install(mod_path)

def setup(args):

    try:
        config_file = Path(args.config)
        if not config_file.exists():
            raise FileNotFoundError()
    except FileNotFoundError:
        print(f"Config file: {config_file} not found, creating...")
        with open(config_file, "w") as fp:
            json.dump({"mods": {}}, fp, indent=4)
        print(f"Config file created at: {config_file}.")
    finally:
        with open(config_file) as fp:
            config = json.load(fp)

    return config

def main():
    args = cmd()
    config = setup(args)
    mods = config['mods']
    print(args)
    if hasattr(args, 'now'):
        for mod_name in mods:
            mod = Mod(mod_name, args.game_version)
            if mod.check_update(mods[mod_name]['version']):
                print(f"Mod: \"{mod.name}\" has an update available.")
                update = input("Would you like to update [Y/n]: ")
                if update == ("" or "Y"):
                    installed = mod.update(args.mod_path, mods[mod_name]['file'])
                    if installed:
                        with open(Path(args.config), "w") as fp:
                            config['mods'][mod.name] = installed
                            json.dump(config, fp, indent=4)
    elif hasattr(args, 'install_package'):
        mod = urlsplit(args.install_package)
        if re.match(r"/mod/*", mod.path):
            match = re.split(r"mod/", mod.path)
            if match:
                mod_name = match[1]
            else:
                print("Invalid mod name")
            mod = Mod(mod_name, args.game_version)
            if mod.exists():
                print("Mod exists.")
                installed = mod.install(args.mod_path)
                if installed:
                    with open(Path(args.config), "w") as fp:
                        config['mods'][mod.name] = installed
                        json.dump(config, fp, indent=4)
            else:
                print("Mod does not exist.")
        else:
            pass
    elif hasattr(args, 'remove_package'):
        mod = urlsplit(args.remove_package)
        if re.match(r"/mod/*", mod.path):
            match = re.split(r"mod/", mod.path)
            if match:
                mod_name = match[1]
        if mod_name in config['mods']:
            mod = Mod(mod_name, game_version=game_version)
            mod.delete(args.mod_path, config['mods'][mod_name]['file'])
            with open(Path(args.config), "w") as fp:
                del config['mods'][mod.name]
                json.dump(config, fp, indent=4)
        else:
            print("Mod not installed")
    else:
        print("Nothing to do.")
