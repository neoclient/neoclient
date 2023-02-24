from enum import Enum, auto
from typing import Sequence

__all__: Sequence[str] = (
    "HttpMethod",
    "MethodKind",
    "HeaderName",
)


class HiddenValueEnum(Enum):
    def __repr__(self) -> str:
        return f"<{type(self).__name__}.{self.name}>"


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class HttpMethod(HiddenValueEnum, StrEnum):
    PUT = "PUT"
    GET = "GET"
    POST = "POST"
    HEAD = "HEAD"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"


class MethodKind(HiddenValueEnum):
    METHOD = auto()
    CLASS_METHOD = auto()
    STATIC_METHOD = auto()


class HeaderName(HiddenValueEnum, StrEnum):
    ACCEPT = "Accept"
    ACCEPT_ENCODING = "Accept-Encoding"
    ACCEPT_LANGUAGE = "Accept-Language"
    CACHE_CONTROL = "Cache-Control"
    CONNECTION = "Connection"
    CONTENT_TYPE = "Content-Type"
    COOKIE = "Cookie"
    DNT = "DNT"
    HOST = "Host"
    KEEP_ALIVE = "Keep-Alive"
    LOCATION = "Location"
    PRAGMA = "Pragma"
    PROXY_AUTHENTICATE = "Proxy-Authenticate"
    PROXY_AUTHORIZATION = "Proxy-Authorization"
    REFERER = "Referer"
    SERVER = "Server"
    TE = "TE"
    TRAILER = "Trailer"
    TRANSFER_ENCODING = "Transfer-Encoding"
    UPGRADE = "Upgrade"
    USER_AGENT = "User-Agent"
