"""Package wide code"""

from logging import basicConfig, getLogger

logger = getLogger(__name__)
basicConfig(format="%(levelname)s:%(name)s %(message)s", level=20)
