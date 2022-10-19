from dataclasses import dataclass
from typing import Any, Mapping

from loguru import logger

from .composers import (
    QueryParamComposer,
    HeaderComposer,
    CookieComposer,
    PathParamComposer,
    QueryParamsComposer,
    HeadersComposer,
    CookiesComposer,
    PathParamsComposer,
    ContentComposer,
    DataComposer,
    FilesComposer,
    JsonComposer,
    TimeoutComposer,
)
from .typing import Decorator, Composer, C

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


@dataclass
class CompositionFacilitator(Decorator):
    composer: Composer

    def __call__(self, func: C, /) -> C:
        logger.info(f"Composing {func!r} using {self.composer!r}")

        # TODO: Use get_operation(...)
        self.composer(func.operation.specification.request)

        return func

def query(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(QueryParamComposer(key, value))


def header(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(HeaderComposer(key, value))


def cookie(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(CookieComposer(key, value))


def path(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(PathParamComposer(key, value))


def query_params(params: QueryParamTypes, /) -> Decorator:
    return CompositionFacilitator(QueryParamsComposer(params))


def headers(headers: HeaderTypes, /) -> Decorator:
    return CompositionFacilitator(HeadersComposer(headers))


def cookies(cookies: CookieTypes, /) -> Decorator:
    return CompositionFacilitator(CookiesComposer(cookies))


def path_params(path_params: Mapping[str, Any], /) -> Decorator:
    return CompositionFacilitator(PathParamsComposer(path_params))


def content(content: RequestContent, /) -> Decorator:
    return CompositionFacilitator(ContentComposer(content))


def data(data: RequestData, /) -> Decorator:
    return CompositionFacilitator(DataComposer(data))


def files(files: RequestFiles, /) -> Decorator:
    return CompositionFacilitator(FilesComposer(files))


def json(json: JsonTypes, /) -> Decorator:
    return CompositionFacilitator(JsonComposer(json))


def timeout(timeout: TimeoutTypes, /) -> Decorator:
    return CompositionFacilitator(TimeoutComposer(timeout))
