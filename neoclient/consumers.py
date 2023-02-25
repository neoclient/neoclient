from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from httpx import Cookies, Headers, QueryParams, Timeout

from . import converters
from .models import RequestOptions
from .types import (
    CookieTypes,
    HeaderTypes,
    JsonTypes,
    PathsTypes,
    PathTypes,
    QueriesTypes,
    QueryTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    TimeoutTypes,
)
from .typing import RequestConsumer

__all__: Sequence[str] = (
    "QueryConsumer",
    "HeaderConsumer",
    "CookieConsumer",
    "PathConsumer",
    "QueriesConsumer",
    "HeadersConsumer",
    "CookiesConsumer",
    "PathsConsumer",
    "ContentConsumer",
    "DataConsumer",
    "FilesConsumer",
    "JsonConsumer",
    "TimeoutConsumer",
)


@dataclass(init=False)
class QueryConsumer(RequestConsumer):
    key: str
    value: str

    def __init__(self, key: str, value: QueryTypes) -> None:
        self.key = key
        self.value = converters.convert_query_param(value)

    def __call__(self, request: RequestOptions, /) -> None:
        request.params = request.params.set(self.key, self.value)


@dataclass(init=False)
class HeaderConsumer(RequestConsumer):
    key: str
    value: str

    def __init__(self, key: str, value: HeaderTypes) -> None:
        self.key = key
        self.value = converters.convert_header(value)

    def __call__(self, request: RequestOptions, /) -> None:
        request.headers[self.key] = self.value


@dataclass(init=False)
class CookieConsumer(RequestConsumer):
    key: str
    value: str

    def __init__(self, key: str, value: CookieTypes) -> None:
        self.key = key
        self.value = converters.convert_cookie(value)

    def __call__(self, request: RequestOptions, /) -> None:
        request.cookies[self.key] = self.value


@dataclass(init=False)
class PathConsumer(RequestConsumer):
    key: str
    value: str

    def __init__(self, key: str, value: PathTypes) -> None:
        self.key = key
        self.value = converters.convert_path_param(value)

    def __call__(self, request: RequestOptions, /) -> None:
        request.path_params[self.key] = self.value


@dataclass(init=False)
class QueriesConsumer(RequestConsumer):
    params: QueryParams

    def __init__(self, params: QueriesTypes, /) -> None:
        self.params = converters.convert_query_params(params)

    def __call__(self, request: RequestOptions, /) -> None:
        request.params = request.params.merge(self.params)


@dataclass(init=False)
class HeadersConsumer(RequestConsumer):
    headers: Headers

    def __init__(self, headers: HeaderTypes, /) -> None:
        self.headers = converters.convert_headers(headers)

    def __call__(self, request: RequestOptions, /) -> None:
        request.headers.update(self.headers)


@dataclass(init=False)
class CookiesConsumer(RequestConsumer):
    cookies: Cookies

    def __init__(self, cookies: CookieTypes, /) -> None:
        self.cookies = converters.convert_cookies(cookies)

    def __call__(self, request: RequestOptions, /) -> None:
        request.cookies.update(self.cookies)


@dataclass(init=False)
class PathsConsumer(RequestConsumer):
    path_params: Mapping[str, str]

    def __init__(self, path_params: PathsTypes, /) -> None:
        self.path_params = converters.convert_path_params(path_params)

    def __call__(self, request: RequestOptions, /) -> None:
        request.path_params.update(self.path_params)


@dataclass
class ContentConsumer(RequestConsumer):
    content: RequestContent

    def __call__(self, request: RequestOptions, /) -> None:
        request.content = self.content


@dataclass
class DataConsumer(RequestConsumer):
    data: RequestData

    def __call__(self, request: RequestOptions, /) -> None:
        request.data = self.data


@dataclass
class FilesConsumer(RequestConsumer):
    files: RequestFiles

    def __call__(self, request: RequestOptions, /) -> None:
        request.files = self.files


@dataclass
class JsonConsumer(RequestConsumer):
    json: JsonTypes

    def __call__(self, request: RequestOptions, /) -> None:
        request.json = self.json


@dataclass(init=False)
class TimeoutConsumer(RequestConsumer):
    timeout: Timeout

    def __init__(self, timeout: TimeoutTypes, /) -> None:
        self.timeout = converters.convert_timeout(timeout)

    def __call__(self, request: RequestOptions, /) -> None:
        request.timeout = self.timeout


@dataclass
class StateConsumer(RequestConsumer):
    key: str
    value: Any

    def __call__(self, request: RequestOptions, /) -> None:
        request.state[self.key] = self.value
