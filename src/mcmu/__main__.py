#!/usr/bin/env python3

# Imports
import sys
import logging
import argparse
from json import load, dump, JSONDecodeError
from pathlib import Path
from .minecraft_mod import Mod  # Mod function import

__version__ = "1.1.0"
__author__ = "Josiah Jarvis"

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(levelname)s: %(message)s")

parser = argparse.ArgumentParser(prog="mcmu")
parser.add_argument("-u", "--update", help="Updates installed mods", action="store_true")
parser.add_argument("-r", "--remove", help="Removes an installed mod")
parser.add_argument("-i", "--install", help="Installs a mod")
parser.add_argument("-l", "--list", help="List installed mods", action="store_true")
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
            config = load(fp)
        return config
    except JSONDecodeError:
        logger.critical("Config file not valid JSON.")
    except FileNotFoundError:
        logger.warn("Config file does not exist.")
        with open(config_f, "w+") as fp:
            logger.debug("Creating config file.")
            dump({"mods":{}}, fp, indent=4)
        logger.info("Exiting, please re-run.")
    except PermissionError:
        logger.error("No permission to write to file.")
    sys.exit(1) # Exit if there are errors

def write_config_file(config_f: Path, config_d: dict):
    try:
        with open(config_f, "w") as fp:
            dump(config_d, fp, indent=4)
            return
    except FileNotFoundError:
        logger.critical("Config file does not exist.")
    except PermissionError:
        logger.error("No permission to write to file.")
    sys.exit(1) # Exit if there are errors

def main():
    config = load_config_file(config_file)
    mods = config['mods']
    mod_path = Path(args.minecraft_dir, "mods/")
    if args.update:
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
            else:
                print(f"Mod: {mods[mod_name]} at latest version!")
    elif args.install:
        mod = Mod(args.install, args.game_version)
        if mod.exists():
            installed = mod.install(mod_path)
            if installed:
                config['mods'][args.install] = installed
                write_config_file(config_file, config)
        else:
            logger.error("Mod does not exist on Modrinth.")
    elif args.remove:
        if args.remove not in config['mods']:
            logger.error("Mod not installed")
            sys.exit(1)
        mod = Mod(args.remove, game_version=args.game_version)
        try:
            mod.delete(mod_path, config['mods'][args.remove]['file'])
        except FileNotFoundError:
            logger.warn("Mod's file already deleted.")
        except PermissionError:
            logger.critical("No permission to delete mod file.")
            sys.exit(1)
        del config['mods'][args.remove]
        write_config_file(config_file, config)
    elif args.list:
        for mod in config['mods']:
            print(f"{config['mods'][mod]['name']}\n\tVersion: {config['mods'][mod]['version']}\n\tFile: {config['mods'][mod]['file']}")
    else:
        parser.print_help()
