#!/usr/bin/env python3

import argparse
import requests
import json
import sys
import re
from pathlib import Path
from urllib.parse import urlsplit

__version__ = "0.1.1"
__author__ = "Josiah Jarvis"

parser = argparse.ArgumentParser(
    prog="MCModUpdater",
    epilog="..."
)
parser.add_argument("-v", "--version", action="version", version=__version__)
parser.add_argument("-a", "--add")
parser.add_argument("-m", "--mod_path", default=Path(Path.home(), ".minecraft/mods"))
parser.add_argument("-g", "--game_version", default="1.21.11")
parser.add_argument("-c", "--config", default=Path(Path.home(), ".minecraft/config/mcmodupdater.json"))
args = parser.parse_args()


class Mod:
    def __init__(self, mod_name: str, game_version: str, loader: str = "fabric"):
        self.name = mod_name
        self.version = game_version
        self.loader = loader

    def check_update(self):
        parameters = {
            "loaders": [self.loader],
            "game_versions": [self.version],
            "include_changelog": "false"
        }
        response = requests.get(f"https://api.modrinth.com/v2/project/{self.name}/version", params=parameters)
        if response == "404":
            print("404 Mod not found")
            sys.exit(1)
        print(response)
        print(json.dumps(
            response.json(),
            indent=4
            )
        )

    def exists(self):
        parameters = {
            "loaders": [self.loader],
            "game_versions": [self.version],
            "include_changelog": "false"
        }
        response = requests.get(f"https://api.modrinth.com/v2/project/{self.name}/version", params=parameters)
        print(response)
        print(response.status_code)
        if response.status_code == 404:
            return False
        else:
            return True

    def install(self):
        pass

    def delete(self):
        pass

def setup():
    try:
        config_file = Path(args.config)
        if not config_file.exists():
            raise FileNotFoundError()
    except FileNotFoundError:
        print(f"Config file: {config_file} not found, creating...")
        with open(config_file, "w") as fp:
            json.dump({"mods": []}, fp, indent=4)
        print(f"Config file created at: {config_file}.")
    finally:
        with open(config_file) as fp:
            config = json.load(fp)

    return config

def main():
    config = setup()
    print(config)
    mods = config['mods']
    for mod_name in mods:
        mod = Mod(mod_name, "1.21.11")
        if mod.check_update():
            print(f"Mod: \"{mod.name}\" has an update available.")

    if args.add:
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
            if Mod(mod_name, "1.21.11").exists():
                print("Mod exists.")
            else:
                print("Mod does not exist.")
        else:
            pass

main()
