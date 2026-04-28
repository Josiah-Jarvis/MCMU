#!/usr/bin/env python3

"""ModrinthAPI class"""

from pathlib import Path
from requests import get
from importlib.metadata import version as get_version


class ModrinthAPI:
    """Modrinth API class"""
    def __init__(self):
        self.headers = {
            'User-Agent': f"Josiah-Jarvis/MCMU/{get_version(__package__)} (https://github.com/Josiah-Jarvis/MCMU)"
        }

    def query(
        self,
        endpoint: str = "https://api.modrinth.com/v2/",  # The API endpoint
        parameters: dict = None  # The parameters to pass the API
    ) -> dict:  # API json
        """Query's the Modrinth API

        Raises:
            DeprecationWarning: If response is 410
            UserWarning: If response is 400 or 404
        """
        response = get(
            url=f"https://api.modrinth.com/v2/{endpoint}",
            params=parameters,
            headers=self.headers,
            timeout=10
        )
        if response.status_code == 410:
            raise DeprecationWarning("API deprecated")
        if response.status_code == 404:
            raise UserWarning(f"Mod: {endpoint} not found")
        if response.status_code == 400:
            raise UserWarning("API request invalid")
        return response.json()

    def search(
        self,
        query: str,  # The query string
        facets: str  # Used to limit the search results see
    ) -> [dict]:  # Response data
        """Search's Mod on Modrinth"""
        parameters = {
            'query': query,
            'facets': facets,
            'limit': "100"
        }
        return self.query("search", parameters)

    def project(
        self,
        slug: str  # The slug of the project
    ) -> [dict]:  # Project data
        """Get data about a project"""
        return self.query(f"project/{slug}")

    def project_dependencies(
        self,
        slug: str  # The slug of the project
    ) -> [dict]:  # Dependency information
        """Get a list of a projects dependencies"""
        return self.query(f"project/{slug}/dependencies")

    def project_version(
        self,
        slug: str,  # The slug of the project
        loaders: str,  # Loaders to filter for
        version: str  # Game versions to filter for
    ) -> [dict]:  # Project version data
        """List a projects versions"""
        parameters = {
            'loaders': loaders,
            'game_versions': version,
            'include_changelog': 'false'
        }
        return self.query(f"project/{slug}/version", parameters)

    def get_project_version(
        self,
        slug: str,  # The name of the project
        version_number: str  # The specific version of the project
    ) -> [dict]:  # The query's json
        """Get a specific version from a mod"""
        return self.query(f"project/{slug}/version/{version_number}")

    def get_file(
        self,
        file: str,  # The file to download
        path: Path  # The file to write to
    ) -> bool:  # True if success
        """Gets file from the CDN
        Raises:
            UserWarning: 404 code
        """
        response = get(file, stream=True, timeout=10, headers=self.headers)
        if response.status_code == 404:
            raise UserWarning("Version file failed to download")
        try:
            with open(path, 'wb') as jar_file:  # Write to the jar file
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        jar_file.write(chunk)
        except PermissionError as exc:
            raise PermissionError(f"No permission to write: {path}") from exc
        return True
