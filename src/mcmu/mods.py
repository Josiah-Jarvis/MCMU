#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A Mod class"""

from os import replace
from pathlib import Path


class Mod:
    """Mod class"""
    def __init__(
        self,
        name: str,
        version: str,
        file_name: Path,
        mod_folder: Path
    ):
        self.name = name
        self.version = version
        self.file_name = file_name
        self.mod_folder = mod_folder
        self.file = Path(mod_folder, file_name)
        self.enabled = True
        if file_name.endswith(".disabled"):
            self.enabled = False

    def enable(self):
        """Enable the mod"""
        if not self.enabled:
            replace(
                Path(
                    self.mod_folder,
                    f"{self.name}_version_{self.version}.jar.disabled"
                ),
                Path(
                    self.mod_folder,
                    f"{self.name}_version_{self.version}.jar"
                )
            )

    def disable(self):
        """Disable mod"""
        if self.enabled:
            replace(
                Path(
                    self.mod_folder,
                    f"{self.name}_version_{self.version}.jar"
                ),
                Path(
                    self.mod_folder,
                    f"{self.name}_version_{self.version}.jar.disabled"
                )
            )

    def delete(self):
        """Delete a mod"""
        self.file.unlink()
