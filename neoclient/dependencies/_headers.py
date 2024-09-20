from dataclasses import dataclass
from typing import Callable, Optional

from neoclient.enums import HTTPHeader

from ..models import Headers

__all__ = ("header", "location", "server")


@dataclass
class HeaderDependency:
    key: str

    def __call__(self, headers: Headers, /) -> Optional[str]:
        return headers.get(self.key)


def header(key: str, /) -> Callable[..., Optional[str]]:
    return HeaderDependency(key)


location: Callable[..., Optional[str]] = header(HTTPHeader.LOCATION)
server: Callable[..., Optional[str]] = header(HTTPHeader.SERVER)
