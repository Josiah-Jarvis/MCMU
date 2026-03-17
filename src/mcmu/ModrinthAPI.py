#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Modrinth API utils
"""

from requests import get


class ModrinthAPI:
    def __init__(self, UserAgent: str):
        self.headers = {
            'User-Agent': UserAgent
        }

    def search(self, query: str, facets: str) -> [dict, int]:
        """Search's Mod on Modrinth: https://docs.modrinth.com/api/operations/searchprojects/

        Arguments:
            query -- The query string
            facets -- Used to limit the search results see Modrinth API documentation

        Returns:
            dict: Response data
            int:
                410: API deprecated
                400: Search invalid
        """
        parameters = {
            'query': query,
            'facets': facets,
            'limit': "100"
        }
        response = get(url="https://api.modrinth.com/v2/search", params=parameters, headers=self.headers)
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()

    def project(self, slug: str) -> [dict, int]:
        """Get data about a project: https://docs.modrinth.com/api/operations/getproject/

        Arguments:
            slug -- The slug of the project

        Returns:
            dict: Project data
            int:
                410: API deprecated
                404: Project not found
        """
        response = get(url=f"https://api.modrinth.com/v2/project/{slug}", headers=self.headers)
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()

    def project_dependencies(self, slug: str) -> [dict, int]:
        """Get a list of a projects dependencies: https://docs.modrinth.com/api/operations/getdependencies/

        Arguments:
            slug -- The slug of the project

        Returns:
            dict: Dependency information
            int:
                410: API deprecated
                404: Project not found
        """
        response = get(url=f"https://api.modrinth.com/v2/project/{slug}/dependencies", headers=self.headers)
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()

    def project_version(self, slug: str, loaders: str, game_version: str) -> [dict, int]:
        """List a projects versions: https://docs.modrinth.com/api/operations/getprojectversions/

        Arguments:
            slug -- The slug of the project
            loaders -- Loaders to filter for
            game_version -- Game versions to filter for

        Returns:
            dict: Project version data
            int:
                410: API deprecated
                404: Project not found
        """
        parameters = {
            'loaders': loaders,
            'game_versions': game_version,
            'include_changelog': 'false'
        }
        response = get(url=f"https://api.modrinth.com/v2/project/{slug}/version", params=parameters, headers=self.headers)
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()
