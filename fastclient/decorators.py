from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Protocol, TypeVar

from httpx import Timeout
from loguru import logger
from pydantic import BaseModel

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


class BaseComposer(BaseModel, ABC):
    class Config:
        arbitrary_types_allowed: bool = True

    @abstractmethod
    def __call__(self, request: RequestOptions, /) -> None:
        ...


class QueryParamComposer(BaseComposer):
    key: str
    value: Any

    def __call__(self, request: RequestOptions, /) -> None:
        request.params = request.params.set(self.key, self.value)


class HeaderComposer(BaseComposer):
    key: str
    value: str

    def __call__(self, request: RequestOptions, /) -> None:
        request.headers[self.key] = self.value


class CookieComposer(BaseComposer):
    key: str
    value: str

    def __call__(self, request: RequestOptions, /) -> None:
        request.cookies[self.key] = self.value


class PathParamComposer(BaseComposer):
    key: str
    value: str

    def __call__(self, request: RequestOptions, /) -> None:
        request.path_params[self.key] = self.value


class QueryParamsComposer(BaseComposer):
    params: QueryParamTypes

    def __call__(self, request: RequestOptions, /) -> None:
        request.params = request.params.merge(self.params)


class HeadersComposer(BaseComposer):
    headers: HeaderTypes

    def __call__(self, request: RequestOptions, /) -> None:
        request.headers.update(self.headers)


class CookiesComposer(BaseComposer):
    cookies: CookieTypes

    def __call__(self, request: RequestOptions, /) -> None:
        request.cookies.update(self.cookies)


class PathParamsComposer(BaseComposer):
    path_params: Mapping[str, Any]

    def __call__(self, request: RequestOptions, /) -> None:
        request.path_params.update(self.path_params)


class ContentComposer(BaseComposer):
    content: RequestContent

    def __call__(self, request: RequestOptions, /) -> None:
        request.content = self.content


class DataComposer(BaseComposer):
    data: RequestData

    def __call__(self, request: RequestOptions, /) -> None:
        request.data = self.data


class FilesComposer(BaseComposer):
    files: RequestFiles

    def __call__(self, request: RequestOptions, /) -> None:
        request.files = self.files


class JsonComposer(BaseComposer):
    json: JsonTypes

    def __call__(self, request: RequestOptions, /) -> None:
        request.json = self.json


class TimeoutComposer(BaseComposer):
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
    return CompositionFacilitator(QueryParamComposer(key=key, value=value))


def header(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(HeaderComposer(key=key, value=value))


def cookie(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(CookieComposer(key=key, value=value))


def path(key: str, value: Any) -> Decorator:
    return CompositionFacilitator(PathParamComposer(key=key, value=value))


def query_params(params: QueryParamTypes, /) -> Decorator:
    return CompositionFacilitator(QueryParamsComposer(params=params))


def headers(headers: HeaderTypes, /) -> Decorator:
    return CompositionFacilitator(HeadersComposer(headers=headers))


def cookies(cookies: CookieTypes, /) -> Decorator:
    return CompositionFacilitator(CookiesComposer(cookies=cookies))


def path_params(path_params: Mapping[str, Any], /) -> Decorator:
    return CompositionFacilitator(PathParamsComposer(path_params=path_params))


def content(content: RequestContent, /) -> Decorator:
    return CompositionFacilitator(ContentComposer(content=content))


def data(data: RequestData, /) -> Decorator:
    return CompositionFacilitator(DataComposer(data=data))


def files(files: RequestFiles, /) -> Decorator:
    return CompositionFacilitator(FilesComposer(files=files))


def json(json: JsonTypes, /) -> Decorator:
    return CompositionFacilitator(JsonComposer(json=json))


def timeout(timeout: TimeoutTypes, /) -> Decorator:
    return CompositionFacilitator(TimeoutComposer(timeout=timeout))
