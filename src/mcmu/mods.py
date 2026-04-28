#!/usr/bin/env python3

"""A Mod class"""

from os import replace
from pathlib import Path


class ModEnabledError(Exception):
    """Enable mod exception"""


class ModDisabledError(Exception):
    """Disable mod exception"""


class Mod:
    """Mod class"""
    def __init__(self, name, version, file_name, mod_folder):
        self.name = name
        self.version = version
        self.file_name = file_name
        self.mod_folder = mod_folder
        self.file = Path(mod_folder, file_name)

    def enable(self):
        """Enable the mod"""
        if str(self.file_name).endswith(".disabled"):
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
        else:
            raise ModEnabledError(f"Mod: {self.name} already enabled.")

    def disable(self):
        """Disable mod"""
        if str(self.file_name).endswith(".jar"):
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
        else:
            raise ModDisabledError(f"Mod: {self.name} already disabled.")

    def delete(self):
        """Delete a mod"""
        self.file.unlink()
