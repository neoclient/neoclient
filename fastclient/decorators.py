from dataclasses import dataclass
from typing import Any, Callable, Mapping, Protocol, TypeVar

from httpx import Timeout
from loguru import logger

from .models import RequestOptions
from .operations import Operation, get_operation
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

C = TypeVar("C", bound=Callable)


class Decorator(Protocol):
    def __call__(self, func: C, /) -> C:
        ...


class Composer(Protocol):
    def __call__(self, request: RequestOptions, /) -> None:
        ...


@dataclass
class QueryParamComposer(Composer):
    key: str
    value: Any

    def __call__(self, request: RequestOptions, /) -> None:
        request.params = request.params.set(self.key, self.value)


@dataclass
class HeaderComposer(Composer):
    key: str
    value: str

    def __call__(self, request: RequestOptions, /) -> None:
        request.headers[self.key] = self.value


@dataclass
class CookieComposer(Composer):
    key: str
    value: str

    def __call__(self, request: RequestOptions, /) -> None:
        request.cookies[self.key] = self.value


@dataclass
class PathParamComposer(Composer):
    key: str
    value: str

    def __call__(self, request: RequestOptions, /) -> None:
        request.path_params[self.key] = self.value

@dataclass
class QueryParamsComposer(Composer):
    params: QueryParamTypes

    def __call__(self, request: RequestOptions, /) -> None:
        request.params = request.params.merge(self.params)


@dataclass
class HeadersComposer(Composer):
    headers: HeaderTypes

    def __call__(self, request: RequestOptions, /) -> None:
        request.headers.update(self.headers)


@dataclass
class CookiesComposer(Composer):
    cookies: CookieTypes

    def __call__(self, request: RequestOptions, /) -> None:
        request.cookies.update(self.cookies)


@dataclass
class PathParamsComposer(Composer):
    path_params: Mapping[str, Any]

    def __call__(self, request: RequestOptions, /) -> None:
        request.path_params.update(self.path_params)


@dataclass
class ContentComposer(Composer):
    content: RequestContent

    def __call__(self, request: RequestOptions, /) -> None:
        request.content = self.content


@dataclass
class DataComposer(Composer):
    data: RequestData

    def __call__(self, request: RequestOptions, /) -> None:
        request.data = self.data


@dataclass
class FilesComposer(Composer):
    files: RequestFiles

    def __call__(self, request: RequestOptions, /) -> None:
        request.files = self.files


@dataclass
class JsonComposer(Composer):
    json: JsonTypes

    def __call__(self, request: RequestOptions, /) -> None:
        request.json = self.json


@dataclass
class TimeoutComposer(Composer):
    timeout: TimeoutTypes

    def __call__(self, request: RequestOptions, /) -> None:
        request.timeout = Timeout(self.timeout)


@dataclass
class CompositionFacilitator(Decorator):
    composer: Composer

    def __call__(self, func: C, /) -> C:
        logger.info(f"Composing {func!r} using {self.composer!r}")

        operation: Operation = get_operation(func)

        self.composer(operation.specification.request)

        return func


def query(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(QueryParamComposer(key, value))


def header(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(HeaderComposer(key, str(value)))


def cookie(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(CookieComposer(key, str(value)))


def path(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(PathParamComposer(key, str(value)))


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
