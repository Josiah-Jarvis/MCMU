"""Shared helper scripts for MCMU"""

from datetime import datetime, timedelta, UTC
from hashlib import sha512
from importlib.metadata import PackageNotFoundError, version
from json import load, dump, JSONDecodeError
from os import environ, getenv, listdir, replace
from pathlib import Path
from platform import system
from re import match
from requests import get
from . import logger

try:
    __version__ = version("mcmu")
except PackageNotFoundError:
    __version__ = "Version  Not Found"

USER_AGENT = f"Josiah-Jarvis/MCMU/{__version__} "
USER_AGENT += "(https://github.com/Josiah-Jarvis/MCMU)"


def query(
    endpoint: str = "",  # The API endpoint
    parameters: dict | None = None  # The parameters to pass the API
) -> dict:  # API json
    """Query's the Modrinth API
    Raises:
        DeprecationWarning: If response is 410
        UserWarning: If response is 400 or 404
    """
    response = get(
        url=f"https://api.modrinth.com/v2/{endpoint}",
        params=parameters,
        headers={'User-Agent': USER_AGENT},
        timeout=10
    )
    if response.status_code == 410:
        raise DeprecationWarning("Modrinth API deprecated")
    if response.status_code == 404:
        raise UserWarning(
            f"Endpoint: https://api.modrinth.com/v2/{endpoint} not found"
        )
    if response.status_code == 400:
        raise UserWarning("API request invalid")
    return response.json()


def get_file(
    file: str,  # The file to download
    path: Path,  # The file to write to
    hash_list: list  # The  hashs
) -> bool:  # True if success
    """Gets file from the CDN
    Raises:
        UserWarning: 404 code, hash's do not match
        PermissionError: No permission to write to file
    """
    response = get(
        file, stream=True, timeout=10, headers={'User-Agent': USER_AGENT}
    )
    if response.status_code == 404:
        raise UserWarning("Version file failed to download")
    try:
        hash_sha512 = sha512(usedforsecurity=False)
        with open(path, 'wb') as jar_file:  # Write to the jar file
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    jar_file.write(chunk)
                    hash_sha512.update(chunk)
        if hash_sha512.hexdigest() == hash_list['sha512']:
            return True
        raise UserWarning("Hash's do not match")
    except PermissionError as exc:
        raise PermissionError(f"No permission to write: {path}") from exc


class Mod:
    """Mod class"""
    def __init__(
        self,
        name: str,
        mod_version: str,
        file_name: Path,
        mod_folder: Path
    ):
        self.name = name
        self.version = mod_version
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
            self.enabled = True

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
            self.enabled = False


try:
    MOD_DIR = environ['MCMU_MOD_PATH']
    logger.info(
        "MCMU_MOD_PATH=%s",
        MOD_DIR
    )
except KeyError:
    if system() == "Darwin":
        MOD_DIR = Path(
            Path.home(), "Library/Application Support/minecraft/mods/"
        )
    elif system() == "Windows":
        MOD_DIR = Path(getenv('APPDATA'), ".minecraft\\mods\\")
    else:  # Should be linux or other unix like systems
        MOD_DIR = Path(Path.home(), ".minecraft/mods/")


class ModrinthData:
    """Gets different data about Modrinth"""
    def __init__(self, mod_dir: Path = MOD_DIR):
        self.cache_file = Path(mod_dir, ".mcmu_modrinth_cache")
        self.date_format = "%d/%m/%y %H:%M:%S.%f"
        self.cache = {}
        self.cache['expires'] = ""
        self.cache['categories'] = []
        self.cache['loaders'] = []
        self.cache['game_versions'] = []

    def get_categories(self) -> list:
        """Get a list of categories"""
        for category in query("tag/category"):
            if category['project_type'] == "mod":
                self.cache['categories'].append(category['name'])

    def get_loaders(self) -> list:
        """Get a list of loaders"""
        for loader in query("tag/loader"):
            if "mod" in loader['supported_project_types']:
                self.cache['loaders'].append(loader['name'])

    def get_game_versions(self) -> list:
        """Get a list of game versions"""
        for mod_version in query("tag/game_version"):
            if mod_version['version_type'] == "release":
                self.cache['game_versions'].append(mod_version['version'])

    def store_data(self, get_data: bool = True):
        """Store Modrinth Category Data"""
        if get_data:
            self.get_categories()
            self.get_loaders()
            self.get_game_versions()

        if self.cache['expires'] == "":
            expires_date = datetime.now(tz=UTC) + timedelta(days=30)
            self.cache['expires'] = expires_date.strftime(self.date_format)
        with open(self.cache_file, "w", encoding="UTF-8") as fp:
            dump(self.cache, fp, indent=4)
        logger.info("Cache file created")

    def load_data(self):
        """Loads the Modrinth data in"""
        try:
            with open(self.cache_file, "r", encoding="UTF-8") as fp:
                cache = load(fp)
                if datetime.strptime(
                    cache['expires'], self.date_format
                ).astimezone(UTC) < datetime.now(tz=UTC):
                    self.store_data()
                    logger.info("Updated Cache File")
                else:
                    new_data = False
                    try:
                        self.cache['categories'] = cache['categories']
                        if cache['categories'] == []:
                            raise KeyError()
                    except KeyError:
                        self.get_categories()
                        new_data = True
                    try:
                        self.cache['loaders'] = cache['loaders']
                        if cache['loaders'] == []:
                            raise KeyError()
                    except KeyError:
                        self.get_loaders()
                        new_data = True
                    try:
                        self.cache['game_versions'] = cache['game_versions']
                        if cache['game_versions'] == []:
                            raise KeyError()
                    except KeyError:
                        self.get_game_versions()
                        new_data = True
                    if new_data:
                        self.store_data(get_data=False)
        except FileNotFoundError:
            logger.warning("Cache file not found, creating...")
            self.store_data()
        except JSONDecodeError:
            logger.error("Cache file corrupted, deleting...")
            self.cache_file.unlink()


CachedData = ModrinthData()
CachedData.load_data()

try:
    GAME_VERSION = environ['MCMU_GAME_VERSION']
    if GAME_VERSION in CachedData.cache['game_versions']:
        logger.info(
            "MCMU_GAME_VERSION=%s",
            GAME_VERSION
        )
    else:
        logger.error(
            "Game version '%s' not a valid game version setting to default...",
            GAME_VERSION
        )
        raise ValueError("Game version not a valid game version")
except (KeyError, ValueError):
    GAME_VERSION = "26.3"

try:
    MOD_LOADER = environ['MCMU_MOD_LOADER']
    if MOD_LOADER in CachedData.cache['loaders']:
        logger.info(
            "MCMU_MOD_LOADER=%s",
            MOD_LOADER
        )
    else:
        logger.error(
            "Mod loader '%s' not a valid mod loader, setting to default...",
            MOD_LOADER
        )
        raise ValueError("Mod loader not a valid mod loader")
except (KeyError, ValueError):
    MOD_LOADER = "fabric"


def ask(question: str) -> bool:
    """Ask a question"""
    return input(f"{question} [Y/n]: ").lower() in ("y", "")


def get_latest_version(
    mod_name: str,  # The name of the mod on Modrinth
    mod_loader: str,  # The mod loader to get for
    game_version: str,
    channel: list  # The channel to get mods from
) -> dict:  # Modrinth mod object or False if already at latest version
    """Checks for mod update from Modrinth"""
    version_params = {
        'loaders': f'["{mod_loader}"]',
        'game_versions': f'["{game_version}"]',
        'include_changelog': 'false'
    }
    latest_version = {'version_number': "0"}
    for mod_version in query(f"project/{mod_name}/version", version_params):
        if mod_version['version_type'] in channel and mod_version["version_number"] > latest_version["version_number"]:
            latest_version = mod_version  # Set to latest version if newer
    return latest_version  # Return the latest version


def list_mods(mod_path: Path) -> dict[Mod]:
    """Gets a list of installed mods"""
    mods = {}
    for mod in listdir(mod_path):
        m = match(r'^(.*?)_version_(.*)\.(?:jar|jar.disabled)$', mod)
        try:
            mods[m.group(1)] = Mod(
                name=m.group(1),
                mod_version=m.group(2),
                file_name=mod,
                mod_folder=mod_path,
            )
        except AttributeError:
            ...

    return mods


def download_dependency_s(
    dependency_s: list,  # List of mods dependency's
    mods: list,  # List of installed mods
    mod_path: Path,  # Path to the mods folder
    mod_loader: str = MOD_LOADER,
    game_version: str = GAME_VERSION,
    channel: list = "release"
):
    """Download a mods dependency's"""
    for dependency in dependency_s:
        mod_data = query(f"project/{dependency['project_id']}")
        if mod_data['slug'] not in mods:
            if dependency['dependency_type'] == "required":
                latest_version = get_latest_version(
                    mod_data['slug'],
                    mod_loader,
                    game_version,
                    channel
                )
                jar_file = Path(
                    mod_path,
                    f"{mod_data['slug']}_version_{latest_version['version_number']}.jar"
                )
                get_file(
                    latest_version['files'][0]['url'],
                    jar_file,
                    latest_version['files'][0]['hashes']
                )
                logger.info("\tDownloaded %s successfully", jar_file)
            elif dependency['dependency_type'] == "optional":
                if ask(
                    f"Would you like to install optional dependency: {mod_data['slug']}?"
                ):
                    latest_version = get_latest_version(
                        mod_data['slug'],
                        mod_loader,
                        game_version,
                        channel
                    )
                    jar_file = Path(
                        mod_path,
                        f"{mod_data['slug']}_version_{latest_version['version_number']}.jar"
                    )
                    get_file(
                        latest_version['files'][0]['url'],
                        jar_file,
                        latest_version['files'][0]['hashes']
                    )
                    logger.info("\tDownloaded %s successfully", jar_file)
        elif (
            mod_data['slug'] in mods
        ) and (
            dependency['dependency_type'] == "incompatible"
        ):
            logger.warning(
                "Incompatible dependency: %s installed, please remove",
                mod_data['slug']
            )


def update_mods(
    mods: dict,  # A dict of mods
    mod_path: Path,  # The path to the mods
    game_version: str = GAME_VERSION,
    mod_loader: str = MOD_LOADER,
    channel: list = "release"
) -> bool:
    """Updates mods"""
    for mod_name, mod_class in mods.items():
        latest_version = get_latest_version(
            mod_name,
            mod_loader,
            game_version,
            channel
        )  # Check for update
        if latest_version["version_number"] <= mod_class.version:
            latest_version = False
        if latest_version:  # If latest version is a dict it should be True
            old_file = Path(
                mod_path,
                mod_class.file_name
            )  # Path to the old mod file
            additional_storage = latest_version['files'][0]['size'] - old_file.stat().st_size  # Calculate how much more storage will be taken up
            if ask(f"{mod_class.name} will take up: {additional_storage} additional bytes. Would you like to install?"):
                download_dependency_s(
                    latest_version['dependencies'],
                    mods,
                    mod_path,
                    mod_loader,
                    game_version,
                    channel
                )
                jar_file = Path(
                    mod_path,
                    f"{mod_name}_version_{latest_version['version_number']}.jar"
                )
                get_file(
                    latest_version['files'][0]['url'],
                    jar_file,
                    latest_version['files'][0]['hashes']
                )
                logger.info("Downloaded mod at %s successfully", jar_file)
                logger.info("Deleting old file: %s", old_file)
                try:
                    old_file.unlink()  # Delete old file
                except PermissionError:
                    logger.error("No permission to delete the file")
                    return False
            else:
                logger.info("Canceling")
        else:
            logger.info("Mod '%s' at latest version!", mod_name)
    return True


def install_mod(
        mod: str,  # The mod
        mods: dict,  # Dict of mods
        mod_path: Path,  # The path to the mods folder
        game_version: str = GAME_VERSION,
        mod_loader: str = MOD_LOADER,
        channel: list = "release"
) -> bool:
    """Installs a mod"""
    if mod in mods:  # If mod already installed exit
        logger.info("%s already installed", mod)
        return True
    mod = mod.split("==")
    if len(mod) > 1:
        latest_version = query(f"project/{mod[0]}/version/{mod[1]}")
        if latest_version["version_number"] == "0":
            latest_version = False
        if latest_version and (
            game_version not in latest_version['game_versions']
        ):
            latest_version = False
        if latest_version:
            logger.error(
                "%s does not support this game version",
                mod[1]
            )
            return False
        if ask(f"{mod[0]} will take up: {latest_version['files'][0]['size']} bytes. Would you like to install?"):
            download_dependency_s(
                latest_version['dependencies'],
                mods,
                mod_path,
                mod_loader,
                game_version,
                channel
            )
            jar_file = Path(
                mod_path,
                f"{mod[0]}_version_{latest_version['version_number']}.jar"
            )
            get_file(
                latest_version['files'][0]['url'],
                jar_file,
                latest_version['files'][0]['hashes']
                )
            logger.info("Downloaded mod at %s successfully", jar_file)
            return True
    latest_version = get_latest_version(
        mod[0],
        mod_loader,
        game_version,
        channel
    )
    if latest_version["version_number"] == "0":
        latest_version = False
    if latest_version and (
        game_version not in latest_version['game_versions']
    ):
        latest_version = False
    if latest_version:  # Should be True if it is a dict with items
        if ask(f"{mod[0]} will take up: {latest_version['files'][0]['size']} bytes. Would you like to install?"):
            download_dependency_s(
                latest_version['dependencies'],
                mods,
                mod_path,
                mod_loader,
                game_version
            )
            jar_file = Path(
                mod_path,
                f"{mod[0]}_version_{latest_version['version_number']}.jar"
            )
            get_file(
                latest_version['files'][0]['url'],
                jar_file,
                latest_version['files'][0]['hashes']
                )
            logger.info("Downloaded mod at %s successfully", jar_file)
        else:
            logger.info("Canceling")
            return True
    else:
        logger.error("Mod does not exist for that version and loader")
        return False
    return True
