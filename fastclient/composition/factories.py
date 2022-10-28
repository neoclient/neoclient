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
class QueryParamConsumerFactory(RequestConsumer):
    entry: Entry[str, str]

    def __call__(self, request: RequestOptions, /) -> None:
        request.params = request.params.set(self.entry.key, self.entry.value)


@dataclass
class HeaderConsumerFactory(RequestConsumer):
    entry: Entry[str, str]

    def __call__(self, request: RequestOptions, /) -> None:
        request.headers[self.entry.key] = self.entry.value


@dataclass
class CookieConsumerFactory(RequestConsumer):
    entry: Entry[str, str]

    def __call__(self, request: RequestOptions, /) -> None:
        request.cookies[self.entry.key] = self.entry.value


@dataclass
class PathParamConsumerFactory(RequestConsumer):
    entry: Entry[str, str]

    def __call__(self, request: RequestOptions, /) -> None:
        request.path_params[self.entry.key] = self.entry.value


@dataclass
class QueryParamsConsumerFactory(RequestConsumer):
    params: QueryParams

    def __call__(self, request: RequestOptions, /) -> None:
        request.params = request.params.merge(self.params)


@dataclass
class HeadersConsumerFactory(RequestConsumer):
    headers: Headers

    def __call__(self, request: RequestOptions, /) -> None:
        request.headers.update(self.headers)


@dataclass
class CookiesConsumerFactory(RequestConsumer):
    cookies: Cookies

    def __call__(self, request: RequestOptions, /) -> None:
        request.cookies.update(self.cookies)


@dataclass
class PathParamsConsumerFactory(RequestConsumer):
    path_params: Mapping[str, str]

    def __call__(self, request: RequestOptions, /) -> None:
        request.path_params.update(self.path_params)


@dataclass
class ContentConsumerFactory(RequestConsumer):
    content: RequestContent

    def __call__(self, request: RequestOptions, /) -> None:
        request.content = self.content


@dataclass
class DataConsumerFactory(RequestConsumer):
    data: RequestData

    def __call__(self, request: RequestOptions, /) -> None:
        request.data = self.data


@dataclass
class FilesConsumerFactory(RequestConsumer):
    files: RequestFiles

    def __call__(self, request: RequestOptions, /) -> None:
        request.files = self.files


@dataclass
class JsonConsumerFactory(RequestConsumer):
    json: JsonTypes

    def __call__(self, request: RequestOptions, /) -> None:
        request.json = self.json


@dataclass
class TimeoutConsumerFactory(RequestConsumer):
    timeout: Timeout

    def __call__(self, request: RequestOptions, /) -> None:
        request.timeout = self.timeout
