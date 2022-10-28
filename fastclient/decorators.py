from dataclasses import dataclass
from typing import Any, Mapping

from loguru import logger

from fastclient.models import RequestOptions

from .consumers import (
    ContentConsumer,
    CookieConsumer,
    CookiesConsumer,
    DataConsumer,
    FilesConsumer,
    HeaderConsumer,
    HeadersConsumer,
    JsonConsumer,
    PathParamConsumer,
    PathParamsConsumer,
    QueryParamConsumer,
    QueryParamsConsumer,
    TimeoutConsumer,
)
from .types import (
    CookieTypes,
    HeaderTypes,
    JsonTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    TimeoutTypes,
)
from .typing import C, Decorator, RequestConsumer


@dataclass
class CompositionFacilitator(Decorator):
    composer: RequestConsumer

    def __call__(self, func: C, /) -> C:
        # TODO: Use get_operation(...) (but avoid cyclic dependency!)
        request: RequestOptions = func.operation.specification.request

        logger.info(
            f"Composing {func!r} with request {request!r} using {self.composer!r}"
        )

        self.composer(request)

        return func


def query(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(QueryParamConsumer.parse(key, value))


def header(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(HeaderConsumer.parse(key, value))


def cookie(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(CookieConsumer.parse(key, value))


def path(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(PathParamConsumer.parse(key, value))


def query_params(params: QueryParamTypes, /) -> Decorator:
    return CompositionFacilitator(QueryParamsConsumer.parse(params))


def headers(headers: HeaderTypes, /) -> Decorator:
    return CompositionFacilitator(HeadersConsumer.parse(headers))


def cookies(cookies: CookieTypes, /) -> Decorator:
    return CompositionFacilitator(CookiesConsumer.parse(cookies))


def path_params(path_params: Mapping[str, Any], /) -> Decorator:
    return CompositionFacilitator(PathParamsConsumer.parse(path_params))


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
