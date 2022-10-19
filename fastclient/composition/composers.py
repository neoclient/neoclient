from dataclasses import dataclass
from typing import Any, Mapping

from httpx import Timeout

from .typing import Composer

from ..models import RequestOptions
from ..types import (
    CookieTypes,
    HeaderTypes,
    JsonTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    TimeoutTypes,
)


@dataclass
class QueryParamComposer(Composer):
    key: str
    value: Any

    def __call__(self, request: RequestOptions, /) -> None:
        request.params = request.params.set(self.key, self.value)


@dataclass
class HeaderComposer(Composer):
    key: str
    value: Any

    def __call__(self, request: RequestOptions, /) -> None:
        request.headers[self.key] = str(self.value)


@dataclass
class CookieComposer(Composer):
    key: str
    value: Any

    def __call__(self, request: RequestOptions, /) -> None:
        request.cookies[self.key] = str(self.value)


@dataclass
class PathParamComposer(Composer):
    key: str
    value: Any

    def __call__(self, request: RequestOptions, /) -> None:
        request.path_params[self.key] = str(self.value)


@dataclass
class QueryParamsComposer(Composer):
    params: QueryParamTypes

    def __call__(self, request: RequestOptions, /) -> None:
        request.params = request.params.merge(self.params)


@dataclass
class HeadersComposer(Composer):
    headers: HeaderTypes

    def __call__(self, request: RequestOptions, /) -> None:
        request.headers.update(self.headers)


@dataclass
class CookiesComposer(Composer):
    cookies: CookieTypes

    def __call__(self, request: RequestOptions, /) -> None:
        request.cookies.update(self.cookies)


@dataclass
class PathParamsComposer(Composer):
    path_params: Mapping[str, Any]

    def __call__(self, request: RequestOptions, /) -> None:
        request.path_params.update(self.path_params)


@dataclass
class ContentComposer(Composer):
    content: RequestContent

    def __call__(self, request: RequestOptions, /) -> None:
        request.content = self.content


@dataclass
class DataComposer(Composer):
    data: RequestData

    def __call__(self, request: RequestOptions, /) -> None:
        request.data = self.data


@dataclass
class FilesComposer(Composer):
    files: RequestFiles

    def __call__(self, request: RequestOptions, /) -> None:
        request.files = self.files


@dataclass
class JsonComposer(Composer):
    json: JsonTypes

    def __call__(self, request: RequestOptions, /) -> None:
        request.json = self.json


@dataclass
class TimeoutComposer(Composer):
    timeout: TimeoutTypes

    def __call__(self, request: RequestOptions, /) -> None:
        request.timeout = Timeout(self.timeout)
