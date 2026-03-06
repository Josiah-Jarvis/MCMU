#!/usr/bin/env python3

import argparse
import requests
import json
import sys
import re
from pathlib import Path
from urllib.parse import urlsplit

__version__ = "0.1.3"
game_version = "1.21.11"
__author__ = "Josiah Jarvis"

def cmd():
    parser = argparse.ArgumentParser(
        prog="MCModUpdater",
        epilog="..."
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("-a", "--add")
    parser.add_argument("-m", "--mod_path", default=Path(Path.home(), ".minecraft/mods"))
    parser.add_argument("-g", "--game_version", default=game_version)
    parser.add_argument("-c", "--config", default=Path(Path.home(), ".minecraft/config/mcmodupdater.json"))
    parser.add_argument("-d", "--delete")
    parser.add_argument("-u", "--update")

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
        x=0
        for version in response.json():
            print(response.json()[x]['game_versions'])
            print(x)
#            print(version)
            print(f"[\'{self.version}\']")
            if (response.json()[x]["game_versions"] != f"[\'{self.version}\']") and (self.loader not in response.json()[x]["loaders"]):
                x+=1
                continue
            else:
                if response.json()[x]["version_number"] != current_version:
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

        x=0
        project_info = response.json()
        print(project_info)
        for version in project_info:
            print(project_info[x]["game_versions"][0])
            print(self.version)
            if (project_info[x]["game_versions"] != f"[\'{self.version}\']") and (self.loader not in project_info[x]["loaders"]):
                x+=1
                continue
            else:
                latest_version = project_info[x]['files']
                break

        print(latest_version[0])
        response = requests.get(latest_version[0]['url'], stream=True)
        if response.status_code != 200:
            print(f"Failed to download the mod. Status code: {response.status_code}")
            return False
        with open(Path(mod_path, latest_version[0]['filename']), 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
    
        print(f"Downloaded {latest_version[0]['filename']} successfully.")
        return {'file': latest_version[0]['filename'], 'version': project_info[0]['version_number'], 'name': project_info[0]['name']}

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
    print(args)
    print(args.add)
    print(config)
    mods = config['mods']
    if args.update:
        for mod_name in mods:
            print(mod_name)
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
    elif args.add:
        mod = urlsplit(args.add)
        print(mod.path)
        if re.match(r"/mod/*", mod.path):
            match = re.split(r"mod/", mod.path)
            print(match)
            if match:
                mod_name = match[1]
                print(mod_name)
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
    if args.delete:
        mod = urlsplit(args.delete)
        print(mod.path)
        if re.match(r"/mod/*", mod.path):
            match = re.split(r"mod/", mod.path)
            print(match)
            if match:
                mod_name = match[1]
                print(mod_name)
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
