#!/usr/bin/env python3

import argparse
import requests
import json
import sys
import re
from pathlib import Path
from urllib.parse import urlsplit

# Local Imports
from .minecraft_mod import Mod

__version__ = "1.0.0"
__author__ = "Josiah Jarvis"

parser = argparse.ArgumentParser(
    prog="mcmu",
    epilog="..."
)
subparsers = parser.add_subparsers()
update_parser = subparsers.add_parser("update")
remove_parser = subparsers.add_parser("remove")
install_parser = subparsers.add_parser("install")
update_parser.add_argument("-n", "--now", action="store_true", help="Update mods now", required=True)
remove_parser.add_argument("remove_package", help="Mod to remove")
install_parser.add_argument("install_package", help="Mod to install")
parser.add_argument("-v", "--version", action="version", version=__version__)
# Unix systems defaults to ~/.minecraft/ for the minecraft dir, I don't know about Windows or MacOS
parser.add_argument("-m", "--minecraft_dir", default=Path(Path.home(), ".minecraft/"), help="Path to the Minecraft folder, defaults to '~/.minecraft/'")
# Game version defaults to 1.21.11 as it is the latest Minecraft release
parser.add_argument("-g", "--game_version", default="1.21.11", help="Default game version")

args = parser.parse_args()
config_file = Path(args.minecraft_dir, "config/mcmu.json")

def load_config_file(config_f: Path) -> dict:
    try:
        with open(config_f, "r") as fp:
            config = json.load(fp)
    except json.JSONDecodeError:
        print("Not a valid JSON file.")
        sys.exit(1)
    except FileNotFoundError:
        print("Config file does not exist.")
        print("Creating...")
        with open(config_f, "w+") as fp:
            json.dump({"mods":{}}, fp, indent=4)
        sys.exit(1)
    except PermissionError:
        print("No permission to write file.")
        sys.exit(1)
    return config

def write_config_file(config_f: Path, config_d: dict):
    try:
        with open(config_f, "w") as fp:
            json.dump(config_d, fp, indent=4)
    except FileNotFoundError:
        print("Config file does not exist.")
        sys.exit(1)
    except PermissionError:
        print("No permission to write file.")
        sys.exit(1)


def setup(args):
    if config_file.exists():
        config = load_config_file(config_file)
    else:
        print(f"Config file: {config_file} not found, creating...")
        write_config_file(config_file, {"mods": {}})
        print(f"Config file created at: {config_file}.")

    return config

def main():
    config = setup(args)
    mods = config['mods']
    mod_path = Path(args.minecraft_dir, "mods/")
    print(args)
    if hasattr(args, 'now'):
        for mod_name in mods:
            mod = Mod(mod_name, args.game_version)
            if mod.check_update(mods[mod_name]['version']):
                print(f"Mod: \"{mod.name}\" has an update available.")
                update = input("Would you like to update [Y/n]: ")
                if update == (None or "Y"):
                    installed = mod.update(mod_path, mods[mod_name]['file'])
                    if installed:
                        config['mods'][mod.name] = installed
                        write_config_file(config_file, config)
    elif hasattr(args, 'install_package'):
        mod_name = args.install_package
        mod = Mod(mod_name, args.game_version)
        if mod.exists():
            print("Mod exists.")
            installed = mod.install(mod_path)
            if installed:
                config['mods'][mod.name] = installed
                write_config_file(config_file, config)
        else:
            print("Mod does not exist.")
    elif hasattr(args, 'remove_package'):
        mod_name = args.remove_package
        if mod_name in config['mods']:
            mod = Mod(mod_name, game_version=args.game_version)
            try:
                mod.delete(mod_path, config['mods'][mod_name]['file'])
            except FileNotFoundError:
                print("Mod already deleted.")
            except PermissionError:
                print(f"No permission to delete mod file: {config['mods'][mod_name]['file']}")
                sys.exit(1)
            del config['mods'][mod.name]
            write_config_file(config_file, config)
        else:
            print("Mod not installed")
    else:
        parser.print_help()
