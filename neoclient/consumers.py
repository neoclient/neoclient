from dataclasses import dataclass
from typing import Any, Mapping, Sequence, Tuple

from httpx import URL, Cookies, Headers, QueryParams, Timeout

from . import converters
from .models import ClientOptions, RequestOpts
from .types import (
    CookiesTypes,
    CookieTypes,
    HeadersTypes,
    HeaderTypes,
    JsonTypes,
    PathTypes,
    QueryParamsTypes,
    QueryTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    TimeoutTypes,
    VerifyTypes,
)
from .typing import SupportsConsumeClient, SupportsConsumeRequest

__all__ = (
    "QueryConsumer",
    "HeaderConsumer",
    "CookieConsumer",
    "PathConsumer",
    "QueryParamsConsumer",
    "HeadersConsumer",
    "CookiesConsumer",
    "PathParamsConsumer",
    "ContentConsumer",
    "DataConsumer",
    "FilesConsumer",
    "JsonConsumer",
    "TimeoutConsumer",
    "MountConsumer",
    "BaseURLConsumer",
    "VerifyConsumer",
    "FollowRedirectsConsumer",
)


@dataclass(init=False)
class QueryConsumer(SupportsConsumeClient, SupportsConsumeRequest):
    key: str
    values: Sequence[str]

    def __init__(self, key: str, value: QueryTypes) -> None:
        self.key = key
        self.values = converters.convert_query_param(value)

    def consume_request(self, request: RequestOpts, /) -> None:
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

    def consume_request(self, request: RequestOpts, /) -> None:
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

    def consume_request(self, request: RequestOpts, /) -> None:
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

    def consume_request(self, request: RequestOpts, /) -> None:
        request.path_params[self.key] = self.value


@dataclass(init=False)
class QueryParamsConsumer(SupportsConsumeRequest, SupportsConsumeClient):
    params: QueryParams

    def __init__(self, params: QueryParamsTypes, /) -> None:
        self.params = converters.convert_query_params(params)

    def consume_request(self, request: RequestOpts, /) -> None:
        request.params = request.params.merge(self.params)

    def consume_client(self, client: ClientOptions, /) -> None:
        client.params = client.params.merge(self.params)


@dataclass(init=False)
class HeadersConsumer(SupportsConsumeRequest, SupportsConsumeClient):
    headers: Headers

    def __init__(self, headers: HeadersTypes, /) -> None:
        self.headers = converters.convert_headers(headers)

    def consume_request(self, request: RequestOpts, /) -> None:
        request.headers.update(self.headers)

    def consume_client(self, client: ClientOptions, /) -> None:
        client.headers.update(self.headers)


@dataclass(init=False)
class CookiesConsumer(SupportsConsumeRequest, SupportsConsumeClient):
    cookies: Cookies

    def __init__(self, cookies: CookiesTypes, /) -> None:
        self.cookies = converters.convert_cookies(cookies)

    def consume_request(self, request: RequestOpts, /) -> None:
        request.cookies.update(self.cookies)

    def consume_client(self, client: ClientOptions, /) -> None:
        client.cookies.update(self.cookies)


@dataclass
class PathParamsConsumer(SupportsConsumeRequest):
    path_params: Mapping[str, str]

    def consume_request(self, request: RequestOpts, /) -> None:
        request.path_params.update(self.path_params)


@dataclass
class ContentConsumer(SupportsConsumeRequest):
    content: RequestContent

    def consume_request(self, request: RequestOpts, /) -> None:
        request.content = self.content


@dataclass
class DataConsumer(SupportsConsumeRequest):
    data: RequestData

    def consume_request(self, request: RequestOpts, /) -> None:
        request.data = self.data


@dataclass
class FilesConsumer(SupportsConsumeRequest):
    files: RequestFiles

    def consume_request(self, request: RequestOpts, /) -> None:
        request.files = self.files


@dataclass
class JsonConsumer(SupportsConsumeRequest):
    json: JsonTypes

    def consume_request(self, request: RequestOpts, /) -> None:
        request.json = self.json


@dataclass(init=False)
class TimeoutConsumer(SupportsConsumeRequest, SupportsConsumeClient):
    timeout: Timeout

    def __init__(self, timeout: TimeoutTypes, /) -> None:
        self.timeout = converters.convert_timeout(timeout)

    def consume_request(self, request: RequestOpts, /) -> None:
        request.timeout = self.timeout

    def consume_client(self, client: ClientOptions, /) -> None:
        client.timeout = self.timeout


@dataclass
class StateConsumer(SupportsConsumeRequest):
    key: str
    value: Any

    def consume_request(self, request: RequestOpts, /) -> None:
        request.state[self.key] = self.value


@dataclass
class MountConsumer(SupportsConsumeRequest):
    path: str

    def consume_request(self, request: RequestOpts, /) -> None:
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


@dataclass
class FollowRedirectsConsumer(SupportsConsumeRequest, SupportsConsumeClient):
    follow_redirects: bool

    def consume_request(self, request: RequestOpts, /) -> None:
        request.follow_redirects = self.follow_redirects

    def consume_client(self, client: ClientOptions, /) -> None:
        client.follow_redirects = self.follow_redirects
