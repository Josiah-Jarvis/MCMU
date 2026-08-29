"""Package wide code"""

from importlib.metadata import version, PackageNotFoundError
from logging import getLogger

try:
    __version__ = version("mcmu")
except PackageNotFoundError:
    __version__ = "Version  Not Found"

USER_AGENT = "Josiah-Jarvis/MCMU/"
USER_AGENT += f"{__version__} "
USER_AGENT += "(https://github.com/Josiah-Jarvis/MCMU)"

logger = getLogger(__name__)
logger.setLevel(20)
