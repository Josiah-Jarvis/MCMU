"""Package wide code"""

from logging import getLogger, basicConfig, INFO

logger = getLogger(__name__)
basicConfig(format="%(levelname)s:%(name)s %(message)s", level=INFO)
