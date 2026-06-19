#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gets choices for certain CLI arguments"""

from .shared import ModAPI


def get_categories() -> list:
    response = ModAPI.query("tag/category")
    categories = []
    for category in response:
        if category['project_type'] == "mod":
            categories.append(category['name'])
    return categories

def get_loaders() -> list:
    response = ModAPI.query("tag/loader")
    loaders = []
    for loader in response:
        if "mod" in loader['supported_project_types']:
            loaders.append(loader['name'])
    return loaders

def get_game_versions() -> list:
    response = ModAPI.query("tag/game_version")
    versions = []
    for version in response:
        versions.append(version['version'])
    return versions
