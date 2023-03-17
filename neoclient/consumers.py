from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from httpx import URL, Cookies, Headers, QueryParams, Timeout

from . import converters
from .models import ClientOptions, PreRequest
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
    VerifyTypes,
)
from .typing import SupportsClientConsumer, SupportsRequestConsumer

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
    "MountConsumer",
    "BaseURLConsumer",
    "VerifyConsumer",
)


@dataclass(init=False)
class QueryConsumer(SupportsClientConsumer, SupportsRequestConsumer):
    key: str
    value: str

    def __init__(self, key: str, value: QueryTypes) -> None:
        self.key = key
        self.value = converters.convert_query_param(value)

    def consume_request(self, request: PreRequest, /) -> None:
        request.params = request.params.set(self.key, self.value)

    def consume_client(self, client: ClientOptions, /) -> None:
        client.params = client.params.set(self.key, self.value)


@dataclass(init=False)
class HeaderConsumer(SupportsRequestConsumer, SupportsClientConsumer):
    key: str
    value: str

    def __init__(self, key: str, value: HeaderTypes) -> None:
        self.key = key
        self.value = converters.convert_header(value)

    def consume_request(self, request: PreRequest, /) -> None:
        request.headers[self.key] = self.value

    def consume_client(self, client: ClientOptions, /) -> None:
        client.headers[self.key] = self.value


@dataclass(init=False)
class CookieConsumer(SupportsRequestConsumer, SupportsClientConsumer):
    key: str
    value: str

    def __init__(self, key: str, value: CookieTypes) -> None:
        self.key = key
        self.value = converters.convert_cookie(value)

    def consume_request(self, request: PreRequest, /) -> None:
        request.cookies[self.key] = self.value

    def consume_client(self, client: ClientOptions, /) -> None:
        client.cookies[self.key] = self.value


@dataclass(init=False)
class PathConsumer(SupportsRequestConsumer):
    key: str
    value: str

    def __init__(self, key: str, value: PathTypes) -> None:
        self.key = key
        self.value = converters.convert_path_param(value)

    def consume_request(self, request: PreRequest, /) -> None:
        request.path_params[self.key] = self.value


@dataclass(init=False)
class QueriesConsumer(SupportsRequestConsumer, SupportsClientConsumer):
    params: QueryParams

    def __init__(self, params: QueriesTypes, /) -> None:
        self.params = converters.convert_query_params(params)

    def consume_request(self, request: PreRequest, /) -> None:
        request.params = request.params.merge(self.params)

    def consume_client(self, client: ClientOptions, /) -> None:
        client.params = client.params.merge(self.params)


@dataclass(init=False)
class HeadersConsumer(SupportsRequestConsumer, SupportsClientConsumer):
    headers: Headers

    def __init__(self, headers: HeaderTypes, /) -> None:
        self.headers = converters.convert_headers(headers)

    def consume_request(self, request: PreRequest, /) -> None:
        request.headers.update(self.headers)

    def consume_client(self, client: ClientOptions, /) -> None:
        client.headers.update(self.headers)


@dataclass(init=False)
class CookiesConsumer(SupportsRequestConsumer, SupportsClientConsumer):
    cookies: Cookies

    def __init__(self, cookies: CookieTypes, /) -> None:
        self.cookies = converters.convert_cookies(cookies)

    def consume_request(self, request: PreRequest, /) -> None:
        request.cookies.update(self.cookies)

    def consume_client(self, client: ClientOptions, /) -> None:
        client.cookies.update(self.cookies)


@dataclass(init=False)
class PathsConsumer(SupportsRequestConsumer):
    path_params: Mapping[str, str]

    def __init__(self, path_params: PathsTypes, /) -> None:
        self.path_params = converters.convert_path_params(path_params)

    def consume_request(self, request: PreRequest, /) -> None:
        request.path_params.update(self.path_params)


@dataclass
class ContentConsumer(SupportsRequestConsumer):
    content: RequestContent

    def consume_request(self, request: PreRequest, /) -> None:
        request.content = self.content


@dataclass
class DataConsumer(SupportsRequestConsumer):
    data: RequestData

    def consume_request(self, request: PreRequest, /) -> None:
        request.data = self.data


@dataclass
class FilesConsumer(SupportsRequestConsumer):
    files: RequestFiles

    def consume_request(self, request: PreRequest, /) -> None:
        request.files = self.files


@dataclass
class JsonConsumer(SupportsRequestConsumer):
    json: JsonTypes

    def consume_request(self, request: PreRequest, /) -> None:
        request.json = self.json


@dataclass(init=False)
class TimeoutConsumer(SupportsRequestConsumer, SupportsClientConsumer):
    timeout: Timeout

    def __init__(self, timeout: TimeoutTypes, /) -> None:
        self.timeout = converters.convert_timeout(timeout)

    def consume_request(self, request: PreRequest, /) -> None:
        request.timeout = self.timeout

    def consume_client(self, client: ClientOptions, /) -> None:
        client.timeout = self.timeout


@dataclass
class StateConsumer(SupportsRequestConsumer):
    key: str
    value: Any

    def consume_request(self, request: PreRequest, /) -> None:
        request.state[self.key] = self.value


@dataclass
class MountConsumer(SupportsRequestConsumer):
    path: str

    def consume_request(self, request: PreRequest, /) -> None:
        request.url = request.url.copy_with(path=self.path + request.url.path)


@dataclass
class BaseURLConsumer(SupportsClientConsumer):
    base_url: str

    def consume_client(self, client: ClientOptions, /) -> None:
        client.base_url = URL(self.base_url)


@dataclass
class VerifyConsumer(SupportsClientConsumer):
    verify: VerifyTypes

    def consume_client(self, client: ClientOptions, /) -> None:
        client.verify = self.verify
