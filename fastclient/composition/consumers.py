from dataclasses import dataclass
from typing import Any, List, Mapping

from httpx import Cookies, Headers, QueryParams, Timeout

from .. import converters
from ..models import RequestOptions
from ..types import (
    CookiesTypes,
    HeadersTypes,
    JsonTypes,
    PathsTypes,
    QueriesTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    TimeoutTypes,
)
from ..typing import RequestConsumer

__all__: List[str] = [
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
]


@dataclass
class QueryConsumer(RequestConsumer):
    key: str
    value: str

    def __call__(self, request: RequestOptions, /) -> None:
        request.params = request.params.set(self.key, self.value)

    @classmethod
    def parse(cls, key: str, value: Any) -> "QueryConsumer":
        return cls(
            key,
            converters.convert_query_param(value),
        )


@dataclass
class HeaderConsumer(RequestConsumer):
    key: str
    value: str

    def __call__(self, request: RequestOptions, /) -> None:
        request.headers[self.key] = self.value

    @classmethod
    def parse(cls, key: str, value: Any) -> "HeaderConsumer":
        return cls(
            key,
            converters.convert_header(value),
        )


@dataclass
class CookieConsumer(RequestConsumer):
    key: str
    value: str

    def __call__(self, request: RequestOptions, /) -> None:
        request.cookies[self.key] = self.value

    @classmethod
    def parse(cls, key: str, value: Any) -> "CookieConsumer":
        return cls(
            key,
            converters.convert_cookie(value),
        )


@dataclass
class PathConsumer(RequestConsumer):
    key: str
    value: str

    def __call__(self, request: RequestOptions, /) -> None:
        request.path_params[self.key] = self.value

    @classmethod
    def parse(cls, key: str, value: Any) -> "PathConsumer":
        return cls(
            key,
            converters.convert_path_param(value),
        )


@dataclass
class QueriesConsumer(RequestConsumer):
    params: QueryParams

    def __call__(self, request: RequestOptions, /) -> None:
        request.params = request.params.merge(self.params)

    @classmethod
    def parse(cls, params: QueriesTypes) -> "QueriesConsumer":
        return cls(converters.convert_query_params(params))


@dataclass
class HeadersConsumer(RequestConsumer):
    headers: Headers

    def __call__(self, request: RequestOptions, /) -> None:
        request.headers.update(self.headers)

    @classmethod
    def parse(cls, headers: HeadersTypes) -> "HeadersConsumer":
        return cls(converters.convert_headers(headers))


@dataclass
class CookiesConsumer(RequestConsumer):
    cookies: Cookies

    def __call__(self, request: RequestOptions, /) -> None:
        request.cookies.update(self.cookies)

    @classmethod
    def parse(cls, cookies: CookiesTypes) -> "CookiesConsumer":
        return cls(converters.convert_cookies(cookies))


@dataclass
class PathsConsumer(RequestConsumer):
    path_params: Mapping[str, str]

    def __call__(self, request: RequestOptions, /) -> None:
        request.path_params.update(self.path_params)

    @classmethod
    def parse(cls, path_params: PathsTypes) -> "PathsConsumer":
        return cls(converters.convert_path_params(path_params))


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


@dataclass
class TimeoutConsumer(RequestConsumer):
    timeout: Timeout

    def __call__(self, request: RequestOptions, /) -> None:
        request.timeout = self.timeout

    @classmethod
    def parse(cls, timeout: TimeoutTypes) -> "TimeoutConsumer":
        return cls(converters.convert_timeout(timeout))
