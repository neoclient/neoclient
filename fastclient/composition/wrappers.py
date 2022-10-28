from typing import Any, Mapping

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
from . import bundlers
from .factories import (
    ContentConsumerFactory,
    CookieConsumerFactory,
    CookiesConsumerFactory,
    DataConsumerFactory,
    FilesConsumerFactory,
    HeaderConsumerFactory,
    HeadersConsumerFactory,
    JsonConsumerFactory,
    PathParamConsumerFactory,
    PathParamsConsumerFactory,
    QueryParamConsumerFactory,
    QueryParamsConsumerFactory,
    TimeoutConsumerFactory,
)
from .typing import RequestConsumer


def query(key: str, value: Any) -> RequestConsumer:
    return QueryParamConsumerFactory(bundlers.query(key, value))


def header(key: str, value: Any) -> RequestConsumer:
    return HeaderConsumerFactory(bundlers.header(key, value))


def cookie(key: str, value: Any) -> RequestConsumer:
    return CookieConsumerFactory(bundlers.cookie(key, value))


def path(key: str, value: Any) -> RequestConsumer:
    return PathParamConsumerFactory(bundlers.path(key, value))


def query_params(params: QueryParamTypes, /) -> RequestConsumer:
    return QueryParamsConsumerFactory(bundlers.query_params(params))


def headers(headers: HeaderTypes, /) -> RequestConsumer:
    return HeadersConsumerFactory(bundlers.headers(headers))


def cookies(cookies: CookieTypes, /) -> RequestConsumer:
    return CookiesConsumerFactory(bundlers.cookies(cookies))


def path_params(path_params: Mapping[str, Any], /) -> RequestConsumer:
    return PathParamsConsumerFactory(bundlers.path_params(path_params))


def content(content: RequestContent, /) -> RequestConsumer:
    return ContentConsumerFactory(bundlers.content(content))


def data(data: RequestData, /) -> RequestConsumer:
    return DataConsumerFactory(bundlers.data(data))


def files(files: RequestFiles, /) -> RequestConsumer:
    return FilesConsumerFactory(bundlers.files(files))


def json(json: JsonTypes, /) -> RequestConsumer:
    return JsonConsumerFactory(bundlers.json(json))


def timeout(timeout: TimeoutTypes, /) -> RequestConsumer:
    return TimeoutConsumerFactory(bundlers.timeout(timeout))
