from typing import Optional, Sequence

from httpx import Timeout, URL

from .types import (
    AuthTypes,
    CookiesTypes,
    DefaultEncodingTypes,
    EventHooks,
    HeadersTypes,
    QueriesTypes,
    TimeoutTypes,
    URLTypes,
)

__all__: Sequence[str] = (
    "DEFAULT_BASE_URL",
    "DEFAULT_AUTH",
    "DEFAULT_PARAMS",
    "DEFAULT_HEADERS",
    "DEFAULT_COOKIES",
    "DEFAULT_TIMEOUT",
    "DEFAULT_FOLLOW_REDIRECTS",
    "DEFAULT_MAX_REDIRECTS",
    "DEFAULT_EVENT_HOOKS",
    "DEFAULT_TRUST_ENV",
    "DEFAULT_ENCODING",
)

DEFAULT_BASE_URL: URLTypes = URL()
DEFAULT_AUTH: Optional[AuthTypes] = None
DEFAULT_PARAMS: Optional[QueriesTypes] = None
DEFAULT_HEADERS: Optional[HeadersTypes] = None
DEFAULT_COOKIES: Optional[CookiesTypes] = None
DEFAULT_TIMEOUT: TimeoutTypes = Timeout(5.0)
DEFAULT_FOLLOW_REDIRECTS: bool = False
DEFAULT_MAX_REDIRECTS: int = 20
DEFAULT_EVENT_HOOKS: Optional[EventHooks] = None
DEFAULT_TRUST_ENV: bool = True
DEFAULT_ENCODING: DefaultEncodingTypes = "utf-8"