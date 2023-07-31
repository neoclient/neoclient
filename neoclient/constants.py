from typing import Final

from . import __version__

PACKAGE_NAME: Final[str] = __package__
PACKAGE_VERSION: Final[str] = __version__
USER_AGENT: Final[str] = f"{PACKAGE_NAME}/{PACKAGE_VERSION}"