from dataclasses import dataclass
from typing import Mapping

from httpx import (
    QueryParams,
    Headers,
    Cookies,
    Timeout
)

from .typing import Composer

from ..models import RequestOptions
from ..types import (
    JsonTypes,
    RequestContent,
    RequestData,
    RequestFiles,
)


@dataclass
class QueryParamComposer(Composer):
    key: str
    value: str

    def __call__(self, request: RequestOptions, /) -> None:
        request.params = request.params.set(self.key, self.value)


@dataclass
class HeaderComposer(Composer):
    key: str
    value: str

    def __call__(self, request: RequestOptions, /) -> None:
        request.headers[self.key] = self.value


@dataclass
class CookieComposer(Composer):
    key: str
    value: str

    def __call__(self, request: RequestOptions, /) -> None:
        request.cookies[self.key] = self.value


@dataclass
class PathParamComposer(Composer):
    key: str
    value: str

    def __call__(self, request: RequestOptions, /) -> None:
        request.path_params[self.key] = self.value


@dataclass
class QueryParamsComposer(Composer):
    params: QueryParams

    def __call__(self, request: RequestOptions, /) -> None:
        request.params = request.params.merge(self.params)


@dataclass
class HeadersComposer(Composer):
    headers: Headers

    def __call__(self, request: RequestOptions, /) -> None:
        request.headers.update(self.headers)


@dataclass
class CookiesComposer(Composer):
    cookies: Cookies

    def __call__(self, request: RequestOptions, /) -> None:
        request.cookies.update(self.cookies)


@dataclass
class PathParamsComposer(Composer):
    path_params: Mapping[str, str]

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
    timeout: Timeout

    def __call__(self, request: RequestOptions, /) -> None:
        request.timeout = self.timeout
