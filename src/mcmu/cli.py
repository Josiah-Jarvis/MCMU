#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CLI UI"""
from logging import DEBUG
from argparse import ArgumentParser

from . import __version__, logger, GAME_VERSION, MOD_DIR, MOD_LOADER
from .shared import update_mods, install_mod, list_mods, ModAPI, ask


class CLI:
    """CLI Commands class"""
    def __init__(self):
        """Init"""
        self.args = {}
        self.mods = {}
        self.channel = ["release"]

    def update(self) -> int:
        """CLI function to update mod"""
        if not update_mods(
            self.mods,
            self.args.mod_dir,
            self.args.game_version,
            self.args.loader,
            self.channel
        ):
            return 1
        return 0

    def remove(self) -> int:
        """CLI function to remove mod"""
        try:
            if ask(f"Would you like to remove {self.mods[self.args.mod].name}? This operation will clear {self.mods[self.args.mod].file.stat().st_size} bytes."):
                self.mods[self.args.mod].delete()
                logger.info("Mod '%s' successfully deleted", self.args.mod)
        except KeyError:
            logger.error("Mod '%s' not installed", self.args.mod)
            return 1
        except PermissionError:
            logger.error(
                "No permission to delete '%s'",
                self.mods[self.args.mod].file_name
            )
            return 1
        except FileNotFoundError:
            logger.warning(
                "Mod file '%s' does not exist.",
                self.mods[self.args.mod].file_name
            )
            return 1
        return 0

    def install(self) -> int:
        """CLI function to install mod"""
        try:
            if not install_mod(
                self.args.mod,
                self.mods,
                self.args.mod_dir,
                self.args.game_version,
                self.args.loader,
                self.channel
            ):
                return 1
        except UserWarning:
            logger.error("Mod '%s' does not exist on Modrinth", self.args.mod)
            return 1
        return 0

    def list(self) -> int:
        """CLI function to list mod"""
        for name, mod in self.mods.items():  # Iterate over all installed mods
            print(
                f"{name}\n\tVersion: {mod.version}\n\tFile: {mod.file_name}"
            )
        return 0

    def search(self) -> int:
        """CLI function to search mods"""
        facets = f"[[\"categories:{self.args.loader}\"],[\"project_type:mod\"]]"
        response = ModAPI.search(self.args.term, facets)
        for mod in response['hits']:  # Iterate over and list all the mods
            search = f"""{mod['title']}:
    Description: {mod['description']}
    Author: {mod['author']}
    Downloads: {mod['downloads']}
    Latest Version: {mod['latest_version']}

"""
            print(search)
        return 0

    def info(self) -> int:
        """CLI function to get info on a mod"""
        try:
            response = ModAPI.project(self.args.mod)
            print(f"""{response['slug']}
    Title: {response['title']}
    Description: {response['description']}
    Client Side: {response['client_side']}
""")
            print("Dependency's:")
            dependencies = ModAPI.project_dependencies(self.args.mod)
            dependency_text = ""
            for mod in dependencies['projects']:
                dependency_text += f"""\t{mod['title']}"""
            print(dependency_text)
            return 0
        except UserWarning:
            logger.error("Mod '%s' does not exist on Modrinth", self.args.mod)
            return 1

    def enable(self) -> int:
        """CLI function to enable mod"""
        try:
            self.mods[self.args.mod].enable()
            logger.info("Successfully enabled mod '%s'", self.args.mod)
        except KeyError:
            logger.error(
                "Mod '%s' not installed so can't enable",
                self.args.mod
            )
        return 0

    def disable(self) -> int:
        """CLI function to disable mod"""
        try:
            self.mods[self.args.mod].disable()
            logger.info("Successfully disabled mod '%s'", self.args.mod)
        except KeyError:
            logger.error(
                "Mod '%s' not installed so can't disable",
                self.args.mod
            )
        return 0

    def cli(self) -> dict:
        """Parses command line arguments"""
        parser = ArgumentParser(
            description="A robust package to install, update, and manage Minecraft mods",
            epilog="Try 'mcmu COMMAND --help'"
        )
        parser.add_argument(
            "-v",
            "--version",
            help="Display the version",
            action="version",
            version=__version__
        )
        parser.add_argument(
            "--verbose",
            help="Increase logging level",
            action="store_true"
        )
        parser.add_argument(
            "-l",
            "--loader",
            default=MOD_LOADER,
            choices=[
                'fabric',
                'forge',
                'neoforge',
                'babric',
                'quilt',
                'bukkit',
                'folia',
                'paper',
                'purpur',
                'spigot',
                'sponge'
            ],
            help="The mod loader to target for"
        )
        parser.add_argument(
            "-c",
            "--channel",
            default="release",
            choices=["release", "beta", "alpha"],
            help="The channel to get mods from"
        )
        parser.add_argument(
            "--mod-dir",
            default=MOD_DIR,
            help="Path to the Minecraft mods folder"
        )
        parser.add_argument(
            "--game-version",
            default=GAME_VERSION,
            help="The game version to use to install mods"
        )
        subparsers = parser.add_subparsers(
            description="The function to run",
            dest="command",
        )
        update_parser = subparsers.add_parser("update", help="Update mods")
        update_parser.set_defaults(func=self.update)
        remove_parser = subparsers.add_parser("remove", help="Remove a mod")
        remove_parser.add_argument("mod", help="The mod to remove")
        remove_parser.set_defaults(func=self.remove)
        install_parser = subparsers.add_parser("install", help="Install a mod")
        install_parser.add_argument("mod", help="Install a mod")
        install_parser.set_defaults(func=self.install)
        list_parser = subparsers.add_parser("list", help="List mods")
        list_parser.set_defaults(func=self.list)
        search_parser = subparsers.add_parser("search", help="Search mods")
        search_parser.add_argument("term", help="The term to search for")
        search_parser.set_defaults(func=self.search)
        info_parser = subparsers.add_parser("info", help="Get info on a mod")
        info_parser.add_argument("mod", help="Get info on a mod")
        info_parser.set_defaults(func=self.info)
        enable_parser = subparsers.add_parser("enable", help="Enable a mod")
        enable_parser.add_argument("mod", help="The mod to enable")
        enable_parser.set_defaults(func=self.enable)
        disable_parser = subparsers.add_parser("disable", help="Disable a mod")
        disable_parser.add_argument("mod", help="The mod to disable")
        disable_parser.set_defaults(func=self.disable)
        self.args = parser.parse_args()  # Parse the arguments
        if self.args.verbose:
            logger.setLevel(DEBUG)
        try:
            self.mods = list_mods(self.args.mod_dir)
        except FileNotFoundError:
            logger.error("Mod folder '%s' does not exist", self.args.mod_dir)
            return 1
        if self.args.command is None:
            parser.print_help()
            return 0

        if self.args.channel == "beta":
            self.channel = ["release", "beta"]
        elif self.args.channel == "alpha":
            self.channel = ["release", "beta", "alpha"]

        return self.args.func()  # Run the function
