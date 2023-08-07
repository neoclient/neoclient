from dataclasses import dataclass
from typing import Any, Mapping, Sequence, Tuple

import httpx
from httpx import URL, Cookies, Headers, Timeout

from . import converters
from .models import ClientOptions, PreRequest
from .types import (
    CookiesTypes,
    CookieTypes,
    HeadersTypes,
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
from .typing import SupportsConsumeClient, SupportsConsumeRequest

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
class QueryConsumer(SupportsConsumeClient, SupportsConsumeRequest):
    key: str
    values: Sequence[str]

    def __init__(self, key: str, value: QueryTypes) -> None:
        self.key = key
        self.values = converters.convert_query_param(value)

    def consume_request(self, request: PreRequest, /) -> None:
        request.params = self._apply(request.params)

    def consume_client(self, client: ClientOptions, /) -> None:
        client.params = self._apply(client.params)

    def _apply(self, params: QueryParams, /) -> QueryParams:
        # If there's only one value, set the query param and overwrite any
        # existing entries for this key
        if len(self.values) == 1:
            return params.set(self.key, self.values[0])

        # Otherwise, update the query params and maintain any existing entries for
        # this key
        value: str
        for value in self.values:
            params = params.add(self.key, value)

        return params


@dataclass(init=False)
class HeaderConsumer(SupportsConsumeRequest, SupportsConsumeClient):
    key: str
    values: Sequence[str]

    def __init__(self, key: str, value: HeaderTypes) -> None:
        self.key = key
        self.values = converters.convert_header(value)

    def consume_request(self, request: PreRequest, /) -> None:
        self._apply(request.headers)

    def consume_client(self, client: ClientOptions, /) -> None:
        self._apply(client.headers)

    def _apply(self, headers: Headers, /) -> None:
        # If there's only one value, set the header and overwrite any existing
        # entries for this key
        if len(self.values) == 1:
            headers[self.key] = self.values[0]
        # Otherwise, update the headers and maintain any existing entries for this
        # key
        else:
            values: Sequence[Tuple[str, str]] = [
                (self.key, value) for value in self.values
            ]

            headers.update(values)


@dataclass(init=False)
class CookieConsumer(SupportsConsumeRequest, SupportsConsumeClient):
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
class PathConsumer(SupportsConsumeRequest):
    key: str
    value: str

    def __init__(self, key: str, value: PathTypes) -> None:
        self.key = key
        self.value = converters.convert_path_param(value)

    def consume_request(self, request: PreRequest, /) -> None:
        request.path_params[self.key] = self.value


@dataclass(init=False)
class QueriesConsumer(SupportsConsumeRequest, SupportsConsumeClient):
    params: QueryParams

    def __init__(self, params: QueriesTypes, /) -> None:
        self.params = converters.convert_query_params(params)

    def consume_request(self, request: PreRequest, /) -> None:
        request.params = request.params.merge(self.params)

    def consume_client(self, client: ClientOptions, /) -> None:
        client.params = client.params.merge(self.params)


@dataclass(init=False)
class HeadersConsumer(SupportsConsumeRequest, SupportsConsumeClient):
    headers: Headers

    def __init__(self, headers: HeadersTypes, /) -> None:
        self.headers = converters.convert_headers(headers)

    def consume_request(self, request: PreRequest, /) -> None:
        request.headers.update(self.headers)

    def consume_client(self, client: ClientOptions, /) -> None:
        client.headers.update(self.headers)


@dataclass(init=False)
class CookiesConsumer(SupportsConsumeRequest, SupportsConsumeClient):
    cookies: Cookies

    def __init__(self, cookies: CookiesTypes, /) -> None:
        self.cookies = converters.convert_cookies(cookies)

    def consume_request(self, request: PreRequest, /) -> None:
        request.cookies.update(self.cookies)

    def consume_client(self, client: ClientOptions, /) -> None:
        client.cookies.update(self.cookies)


@dataclass(init=False)
class PathsConsumer(SupportsConsumeRequest):
    path_params: Mapping[str, str]

    def __init__(self, path_params: PathsTypes, /) -> None:
        self.path_params = converters.convert_path_params(path_params)

    def consume_request(self, request: PreRequest, /) -> None:
        request.path_params.update(self.path_params)


@dataclass
class ContentConsumer(SupportsConsumeRequest):
    content: RequestContent

    def consume_request(self, request: PreRequest, /) -> None:
        request.content = self.content


@dataclass
class DataConsumer(SupportsConsumeRequest):
    data: RequestData

    def consume_request(self, request: PreRequest, /) -> None:
        request.data = self.data


@dataclass
class FilesConsumer(SupportsConsumeRequest):
    files: RequestFiles

    def consume_request(self, request: PreRequest, /) -> None:
        request.files = self.files


@dataclass
class JsonConsumer(SupportsConsumeRequest):
    json: JsonTypes

    def consume_request(self, request: PreRequest, /) -> None:
        request.json = self.json


@dataclass(init=False)
class TimeoutConsumer(SupportsConsumeRequest, SupportsConsumeClient):
    timeout: Timeout

    def __init__(self, timeout: TimeoutTypes, /) -> None:
        self.timeout = converters.convert_timeout(timeout)

    def consume_request(self, request: PreRequest, /) -> None:
        request.timeout = self.timeout

    def consume_client(self, client: ClientOptions, /) -> None:
        client.timeout = self.timeout


@dataclass
class StateConsumer(SupportsConsumeRequest):
    key: str
    value: Any

    def consume_request(self, request: PreRequest, /) -> None:
        request.state[self.key] = self.value


@dataclass
class MountConsumer(SupportsConsumeRequest):
    path: str

    def consume_request(self, request: PreRequest, /) -> None:
        request.url = request.url.copy_with(path=self.path + request.url.path)


@dataclass
class BaseURLConsumer(SupportsConsumeClient):
    base_url: str

    def consume_client(self, client: ClientOptions, /) -> None:
        client.base_url = URL(self.base_url)


@dataclass
class VerifyConsumer(SupportsConsumeClient):
    verify: VerifyTypes

    def consume_client(self, client: ClientOptions, /) -> None:
        client.verify = self.verify
