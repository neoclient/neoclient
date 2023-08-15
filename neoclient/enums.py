from enum import Enum, auto
from typing import Sequence

__all__: Sequence[str] = (
    "Entity",
    "HTTPMethod",
    "HTTPHeader",
)


class HiddenValueEnum(Enum):
    def __repr__(self) -> str:
        return f"<{type(self).__name__}.{self.name}>"


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class Entity(HiddenValueEnum):
    MIDDLEWARE = auto()
    RESPONSE = auto()
    REQUEST_DEPENDENCY = auto()
    RESPONSE_DEPENDENCY = auto()


class HTTPMethod(HiddenValueEnum, StrEnum):
    CONNECT = "CONNECT"
    DELETE = "DELETE"
    GET = "GET"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    POST = "POST"
    PUT = "PUT"
    TRACE = "TRACE"


class HTTPHeader(HiddenValueEnum, StrEnum):
    ACCEPT = "Accept"
    ACCEPT_ENCODING = "Accept-Encoding"
    ACCEPT_LANGUAGE = "Accept-Language"
    AUTHORIZATION = "Authorization"
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
