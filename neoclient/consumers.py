from dataclasses import dataclass
from typing import Any, Mapping, Sequence, Union

from httpx import Cookies, Headers, QueryParams, Timeout

from . import converters
from .errors import CompositionError
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
)

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


class Consumer:
    def consume(self, target: Union[PreRequest, ClientOptions], /) -> None:
        if isinstance(target, PreRequest):
            self.consume_request(target)
        elif isinstance(target, ClientOptions):
            self.consume_client(target)
        else:
            raise CompositionError(
                f"Consumer {type(self).__name__!r} does not support consumption of type {type(target)}"
            )

    def consume_request(self, _: PreRequest, /) -> None:
        raise CompositionError(
            f"Consumer {type(self).__name__!r} does not support consumption of type {PreRequest}"
        )

    def consume_client(self, _: ClientOptions, /) -> None:
        raise CompositionError(
            f"Consumer {type(self).__name__!r} does not support consumption of type {ClientOptions}"
        )


@dataclass(init=False)
class QueryConsumer(Consumer):
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
class HeaderConsumer(Consumer):
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
class CookieConsumer(Consumer):
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
class PathConsumer(Consumer):
    key: str
    value: str

    def __init__(self, key: str, value: PathTypes) -> None:
        self.key = key
        self.value = converters.convert_path_param(value)

    def consume_request(self, request: PreRequest, /) -> None:
        request.path_params[self.key] = self.value


@dataclass(init=False)
class QueriesConsumer(Consumer):
    params: QueryParams

    def __init__(self, params: QueriesTypes, /) -> None:
        self.params = converters.convert_query_params(params)

    def consume_request(self, request: PreRequest, /) -> None:
        request.params = request.params.merge(self.params)

    def consume_client(self, client: ClientOptions, /) -> None:
        client.params = client.params.merge(self.params)


@dataclass(init=False)
class HeadersConsumer(Consumer):
    headers: Headers

    def __init__(self, headers: HeaderTypes, /) -> None:
        self.headers = converters.convert_headers(headers)

    def consume_request(self, request: PreRequest, /) -> None:
        request.headers.update(self.headers)

    def consume_client(self, client: ClientOptions, /) -> None:
        client.headers.update(self.headers)


@dataclass(init=False)
class CookiesConsumer(Consumer):
    cookies: Cookies

    def __init__(self, cookies: CookieTypes, /) -> None:
        self.cookies = converters.convert_cookies(cookies)

    def consume_request(self, request: PreRequest, /) -> None:
        request.cookies.update(self.cookies)

    def consume_client(self, client: ClientOptions, /) -> None:
        client.cookies.update(self.cookies)


@dataclass(init=False)
class PathsConsumer(Consumer):
    path_params: Mapping[str, str]

    def __init__(self, path_params: PathsTypes, /) -> None:
        self.path_params = converters.convert_path_params(path_params)

    def consume_request(self, request: PreRequest, /) -> None:
        request.path_params.update(self.path_params)


@dataclass
class ContentConsumer(Consumer):
    content: RequestContent

    def consume_request(self, request: PreRequest, /) -> None:
        request.content = self.content


@dataclass
class DataConsumer(Consumer):
    data: RequestData

    def consume_request(self, request: PreRequest, /) -> None:
        request.data = self.data


@dataclass
class FilesConsumer(Consumer):
    files: RequestFiles

    def consume_request(self, request: PreRequest, /) -> None:
        request.files = self.files


@dataclass
class JsonConsumer(Consumer):
    json: JsonTypes

    def consume_request(self, request: PreRequest, /) -> None:
        request.json = self.json


@dataclass(init=False)
class TimeoutConsumer(Consumer):
    timeout: Timeout

    def __init__(self, timeout: TimeoutTypes, /) -> None:
        self.timeout = converters.convert_timeout(timeout)

    def consume_request(self, request: PreRequest, /) -> None:
        request.timeout = self.timeout

    def consume_client(self, client: ClientOptions, /) -> None:
        client.timeout = self.timeout


@dataclass
class StateConsumer(Consumer):
    key: str
    value: Any

    def consume_request(self, request: PreRequest, /) -> None:
        request.state[self.key] = self.value
