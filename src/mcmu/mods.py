#!/usr/bin/env python3

from os import replace
from pathlib import Path


class ModEnabled(Exception):
    pass


class ModDisabled(Exception):
    pass


class Mod:
    def __init__(self, name, version, file_name, mod_folder):
        self.name = name
        self.version = version
        self.file_name = file_name
        self.mod_folder = mod_folder

    def enable(self):
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
            raise ModEnabled(f"Mod: {self.name} already enabled.")

    def disable(self):
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
            raise ModDisabled(f"Mod: {self.name} already disabled.")

    def delete(self):
        self.file_name.unlink()
