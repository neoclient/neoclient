from dataclasses import dataclass
from typing import Any, Protocol, TypeVar

from loguru import logger

from fastclient.models import RequestOptions

from ..operations import CallableWithOperation
from ..types import (
    CookieTypes,
    HeaderTypes,
    JsonTypes,
    PathParamTypes,
    QueryParamTypes,
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


def query_params(params: QueryParamTypes, /) -> Decorator:
    return CompositionFacilitator(QueriesConsumer.parse(params))


def headers(headers: HeaderTypes, /) -> Decorator:
    return CompositionFacilitator(HeadersConsumer.parse(headers))


def cookies(cookies: CookieTypes, /) -> Decorator:
    return CompositionFacilitator(CookiesConsumer.parse(cookies))


def path_params(path_params: PathParamTypes, /) -> Decorator:
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
