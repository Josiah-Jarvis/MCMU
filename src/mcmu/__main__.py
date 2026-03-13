#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Imports
from json import load, dump, JSONDecodeError
from pathlib import Path
from logging import getLogger, basicConfig
from argparse import ArgumentParser
from .minecraft_mod import Mod  # Mod function import

__version__ = "1.2.0.dev1"
__author__ = "Josiah Jarvis"

logger = getLogger(__name__)
basicConfig(format="%(levelname)s: %(message)s")

parser = ArgumentParser(prog="mcmu")
parser.add_argument("-u", "--update", help="Updates installed mods", action="store_true")
parser.add_argument("-r", "--remove", help="Removes an installed mod")
parser.add_argument("-i", "--install", help="Installs a mod")
parser.add_argument("-l", "--list", help="List installed mods", action="store_true")
parser.add_argument("-v", "--version", action="version", version=f"MCMU version: {__version__}")
# Unix systems defaults to ~/.minecraft/ for the minecraft dir, I don't know about Windows or MacOS
parser.add_argument("-m", "--minecraft_dir", default=Path(Path.home(), ".minecraft/"), help="Path to the Minecraft folder, defaults to '~/.minecraft/'")
# Game version defaults to 1.21.11 as it is the latest Minecraft release
parser.add_argument("-g", "--game_version", default="26.1", help="Default game version")

args = parser.parse_args()
config_file = Path(args.minecraft_dir, "config/mcmu.json")

def write_config_file(config_f: Path, config_d: dict):
    try:
        with open(config_f, "w") as fp:
            dump(config_d, fp, indent=4)
            return True
    except FileNotFoundError:
        logger.critical("Config file does not exist.")
        return False
    except PermissionError:
        logger.error("No permission to write to file.")
        return False

def main():
    try:
        with open(config_file, "r") as fp:
            config = load(fp)
    except JSONDecodeError:
        logger.critical("Config file not valid JSON.")
        return 1
    except FileNotFoundError:
        logger.warn("Config file does not exist.")
        with open(config_file, "w+") as fp:
            logger.debug("Creating config file.")
            dump({"mods":{}}, fp, indent=4)
        logger.info("Exiting, please re-run.")
        return 1
    except PermissionError:
        logger.error("No permission to write to file.")
        return 1
    mods = config['mods']
    mod_path = Path(args.minecraft_dir, "mods/")
    if not mod_path.exists():
        logger.critical(f"Mods folder: {mod_path} does not exist. Please create it.\nExiting...")
        return 1
    if args.update:
        for mod_name in mods:
            mod = Mod(mod_name, args.game_version)
            if mod.check_update(mods[mod_name]['version']):
                print(f"Mod: \"{mod.name}\" has an update available.")
                update = input("Would you like to update [Y/n]: ")
                if update == (None or "Y"):
                    Path(mod_path, mods[mod_name]['file']).unlink()
                    installed = mod.install(mod_path)
                    if installed:
                        config['mods'][mod.name] = installed
                        if not write_config_file(config_file, config):
                            return 1
            else:
                print(f"Mod: {mod.name} at latest version!")
    elif args.install:
        mod = Mod(args.install, args.game_version)
        if mod.exists():
            installed = mod.install(mod_path)
            if installed:
                config['mods'][args.install] = installed
                if not write_config_file(config_file, config):
                    return 1
        else:
            logger.error("Mod does not exist on Modrinth.")
    elif args.remove:
        if args.remove not in config['mods']:
            logger.error("Mod not installed")
            return 1
        mod = Mod(args.remove, args.game_version)
        try:
            Path(mod_path, config['mods'][args.remove]['file']).unlink()
        except FileNotFoundError:
            logger.warn("Mod's file already deleted.")
        except PermissionError:
            logger.critical("No permission to delete mod file.")
            return 1
        del config['mods'][args.remove]
        if not write_config_file(config_file, config):
            return 1
        print(f"Mod: {args.remove}, successfully removed")
    elif args.list:
        for mod in config['mods']:
            print(f"{config['mods'][mod]['name']}\n\tVersion: {config['mods'][mod]['version']}\n\tFile: {config['mods'][mod]['file']}")
    else:
        parser.print_help()

    return 0 # Return 0 if all good
