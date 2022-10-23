from dataclasses import dataclass
from typing import Any, Mapping

from loguru import logger

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
from . import wrappers
from .factories import ContentComposer, DataComposer, FilesComposer, JsonComposer
from .typing import C, Composer, Decorator


@dataclass
class CompositionFacilitator(Decorator):
    composer: Composer

    def __call__(self, func: C, /) -> C:
        logger.info(f"Composing {func!r} using {self.composer!r}")

        # TODO: Use get_operation(...)
        self.composer(func.operation.specification.request)

        return func


def query(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(wrappers.query(key, value))


def header(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(wrappers.header(key, value))


def cookie(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(wrappers.cookie(key, value))


def path(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(wrappers.path(key, value))


def query_params(params: QueryParamTypes, /) -> Decorator:
    return CompositionFacilitator(wrappers.query_params(params))


def headers(headers: HeaderTypes, /) -> Decorator:
    return CompositionFacilitator(wrappers.headers(headers))


def cookies(cookies: CookieTypes, /) -> Decorator:
    return CompositionFacilitator(wrappers.cookies(cookies))


def path_params(path_params: Mapping[str, Any], /) -> Decorator:
    return CompositionFacilitator(wrappers.path_params(path_params))


def content(content: RequestContent, /) -> Decorator:
    return CompositionFacilitator(ContentComposer(content))


def data(data: RequestData, /) -> Decorator:
    return CompositionFacilitator(DataComposer(data))


def files(files: RequestFiles, /) -> Decorator:
    return CompositionFacilitator(FilesComposer(files))


def json(json: JsonTypes, /) -> Decorator:
    return CompositionFacilitator(JsonComposer(json))


def timeout(timeout: TimeoutTypes, /) -> Decorator:
    return CompositionFacilitator(wrappers.timeout(timeout))
