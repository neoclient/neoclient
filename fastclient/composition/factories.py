from dataclasses import dataclass
from typing import Mapping

from httpx import (
    QueryParams,
    Headers,
    Cookies,
    Timeout
)

from .models import Entry
from .typing import RequestConsumer

from ..models import RequestOptions
from ..types import (
    JsonTypes,
    RequestContent,
    RequestData,
    RequestFiles,
)


@dataclass
class QueryParamComposer(RequestConsumer):
    entry: Entry[str, str]

    def __call__(self, request: RequestOptions, /) -> None:
        request.params = request.params.set(self.entry.key, self.entry.value)


@dataclass
class HeaderComposer(RequestConsumer):
    entry: Entry[str, str]

    def __call__(self, request: RequestOptions, /) -> None:
        request.headers[self.entry.key] = self.entry.value


@dataclass
class CookieComposer(RequestConsumer):
    entry: Entry[str, str]

    def __call__(self, request: RequestOptions, /) -> None:
        request.cookies[self.entry.key] = self.entry.value


@dataclass
class PathParamComposer(RequestConsumer):
    entry: Entry[str, str]

    def __call__(self, request: RequestOptions, /) -> None:
        request.path_params[self.entry.key] = self.entry.value


@dataclass
class QueryParamsComposer(RequestConsumer):
    params: QueryParams

    def __call__(self, request: RequestOptions, /) -> None:
        request.params = request.params.merge(self.params)


@dataclass
class HeadersComposer(RequestConsumer):
    headers: Headers

    def __call__(self, request: RequestOptions, /) -> None:
        request.headers.update(self.headers)


@dataclass
class CookiesComposer(RequestConsumer):
    cookies: Cookies

    def __call__(self, request: RequestOptions, /) -> None:
        request.cookies.update(self.cookies)


@dataclass
class PathParamsComposer(RequestConsumer):
    path_params: Mapping[str, str]

    def __call__(self, request: RequestOptions, /) -> None:
        request.path_params.update(self.path_params)


@dataclass
class ContentComposer(RequestConsumer):
    content: RequestContent

    def __call__(self, request: RequestOptions, /) -> None:
        request.content = self.content


@dataclass
class DataComposer(RequestConsumer):
    data: RequestData

    def __call__(self, request: RequestOptions, /) -> None:
        request.data = self.data


@dataclass
class FilesComposer(RequestConsumer):
    files: RequestFiles

    def __call__(self, request: RequestOptions, /) -> None:
        request.files = self.files


@dataclass
class JsonComposer(RequestConsumer):
    json: JsonTypes

    def __call__(self, request: RequestOptions, /) -> None:
        request.json = self.json


@dataclass
class TimeoutComposer(RequestConsumer):
    timeout: Timeout

    def __call__(self, request: RequestOptions, /) -> None:
        request.timeout = self.timeout
