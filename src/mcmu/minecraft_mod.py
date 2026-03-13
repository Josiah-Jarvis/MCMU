#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

class Mod:
    def __init__(self, mod_name: str, game_version: str):
        self.name = mod_name
        self.version = game_version
        self.parameters = {
            "loaders": ["fabric"],
            "game_versions": [self.version],
            "include_changelog": "false"
        }

    def check_update(self, current_version: str) -> bool:
        response = requests.get(f"https://api.modrinth.com/v2/project/{self.name}/version", params=self.parameters)
        if response.status_code == 404:
            print("404 Mod not found")
            return False

        project_info = response.json()
        latest_version = None
        for version in project_info:
            if self.version in version["game_versions"] and "fabric" in version["loaders"]:
                if latest_version is None or version["version_number"] > latest_version["version_number"]:
                    latest_version = version

        if latest_version is not None and latest_version["version_number"] != current_version:
            return True
        return False

    def exists(self) -> bool:
        response = requests.get(f"https://api.modrinth.com/v2/project/{self.name}/version", params=self.parameters)
        if response.status_code == 404:
            return False
        else:
            return True

    def install(self, mod_path) -> [bool, dict]:
        response = requests.get(f"https://api.modrinth.com/v2/project/{self.name}/version", params=self.parameters)
        if response.status_code != 200:
            print(f"Failed to retrieve project information. Status code: {response.status_code}")
            return False

        project_info = response.json()
        latest_version = None
        for version in project_info:
            if self.version in version["game_versions"] and "fabric" in version["loaders"]:
                if latest_version is None or version["version_number"] > latest_version["version_number"]:
                    latest_version = version

        if latest_version is None:
            print("No version found for the specified game version and loader.")
            return False

        response = requests.get(latest_version['files'][0]['url'], stream=True)
        if response.status_code != 200:
            print(f"Failed to download the mod. Status code: {response.status_code}")
            return False
        with open(f"{mod_path}/{latest_version['files'][0]['filename']}", 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

        print(f"Downloaded {latest_version['files'][0]['filename']} successfully.")
        return {'file': latest_version['files'][0]['filename'], 'version': latest_version['version_number'], 'name': self.name}
