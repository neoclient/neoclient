from dataclasses import dataclass
from typing import Any, List, Protocol, TypeVar

from loguru import logger

from fastclient.models import RequestOptions

from ..operations import CallableWithOperation
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
from .consumers import (
    ContentConsumer,
    CookieConsumer,
    CookiesConsumer,
    DataConsumer,
    FilesConsumer,
    HeaderConsumer,
    HeadersConsumer,
    JsonConsumer,
    PathConsumer,
    PathsConsumer,
    QueriesConsumer,
    QueryConsumer,
    RequestConsumer,
    TimeoutConsumer,
)

__all__: List[str] = [
    "query",
    "header",
    "cookie",
    "path",
    "query_params",
    "headers",
    "cookies",
    "path_params",
    "content",
    "data",
    "files",
    "json",
    "timeout",
]

C = TypeVar("C", bound=CallableWithOperation)


class Decorator(Protocol):
    def __call__(self, func: C, /) -> C:
        ...


@dataclass
class CompositionFacilitator(Decorator):
    composer: RequestConsumer

    def __call__(self, func: C, /) -> C:
        request: RequestOptions = func.operation.specification.request

        logger.info(
            f"Composing {func!r} with request {request!r} using {self.composer!r}"
        )

        self.composer(request)

        return func


def query(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(QueryConsumer.parse(key, value))


def header(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(HeaderConsumer.parse(key, value))


def cookie(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(CookieConsumer.parse(key, value))


def path(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(PathConsumer.parse(key, value))


def query_params(params: QueriesTypes, /) -> Decorator:
    return CompositionFacilitator(QueriesConsumer.parse(params))


def headers(headers: HeadersTypes, /) -> Decorator:
    return CompositionFacilitator(HeadersConsumer.parse(headers))


def cookies(cookies: CookiesTypes, /) -> Decorator:
    return CompositionFacilitator(CookiesConsumer.parse(cookies))


def path_params(path_params: PathsTypes, /) -> Decorator:
    return CompositionFacilitator(PathsConsumer.parse(path_params))


def content(content: RequestContent, /) -> Decorator:
    return CompositionFacilitator(ContentConsumer(content))


def data(data: RequestData, /) -> Decorator:
    return CompositionFacilitator(DataConsumer(data))


def files(files: RequestFiles, /) -> Decorator:
    return CompositionFacilitator(FilesConsumer(files))


def json(json: JsonTypes, /) -> Decorator:
    return CompositionFacilitator(JsonConsumer(json))


def timeout(timeout: TimeoutTypes, /) -> Decorator:
    return CompositionFacilitator(TimeoutConsumer.parse(timeout))
