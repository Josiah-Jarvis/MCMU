#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from re import match
from os import listdir
from pathlib import Path


class Mod:
    def __init__(self, mod_path: Path):
        self.mod_path = mod_path

    def list_mods(self):
        mods = {}
        for mod in listdir(self.mod_path):
            pattern = r'^(.*?)_version_(.*)\.jar$'
            m = match(pattern, mod)
            mods[m.group(1)] = {
                "name": m.group(1),
                "version": m.group(2),
                "file": mod
            }

        return mods
