from dataclasses import dataclass
from typing import Callable, Protocol, Sequence, Type, TypeVar

from mediate.protocols import MiddlewareCallable

from .consumers import (
    Consumer,
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
    TimeoutConsumer,
)
from .enums import HeaderName
from .models import ClientOptions, PreRequest, Request, Response
from .operation import OperationSpecification, get_operation
from .service import Service
from .types import (
    CookiesTypes,
    CookieTypes,
    HeadersTypes,
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
from .typing import RequestConsumer

__all__: Sequence[str] = (
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
)

C = TypeVar("C", bound=Callable)
# S = TypeVar("S", bound=Type[Service])
T = TypeVar("T", Callable, Type[Service])


class Decorator(Protocol):
    def __call__(self, func: C, /) -> C:
        ...


@dataclass
class CompositionFacilitator(Decorator):
    composer: RequestConsumer

    def __call__(self, func: C, /) -> C:
        request: PreRequest = get_operation(func).specification.request

        self.composer(request)

        return func


def query(key: str, value: QueryTypes):
    consumer: Consumer = QueryConsumer(key, value)

    def decorate(target: T, /) -> T:
        if isinstance(target, type):
            if not issubclass(target, Service):
                raise Exception("cls must be a service")

            client: ClientOptions = target._opts

            consumer.consume_client(client)
        elif callable(target):
            request: PreRequest = get_operation(target).specification.request

            consumer.consume_request(request)
        else:
            raise Exception("Expected target to be either Type[Service] or Callable")

        return target
            
    return decorate


def header(key: str, value: HeaderTypes) -> Decorator:
    return CompositionFacilitator(HeaderConsumer(key, value))


def cookie(key: str, value: CookieTypes) -> Decorator:
    return CompositionFacilitator(CookieConsumer(key, value))


def path(key: str, value: PathTypes) -> Decorator:
    return CompositionFacilitator(PathConsumer(key, value))


def query_params(params: QueriesTypes, /) -> Decorator:
    return CompositionFacilitator(QueriesConsumer(params))


def headers(headers: HeadersTypes, /) -> Decorator:
    return CompositionFacilitator(HeadersConsumer(headers))


def cookies(cookies: CookiesTypes, /) -> Decorator:
    return CompositionFacilitator(CookiesConsumer(cookies))


def path_params(path_params: PathsTypes, /) -> Decorator:
    return CompositionFacilitator(PathsConsumer(path_params))


def content(content: RequestContent, /) -> Decorator:
    return CompositionFacilitator(ContentConsumer(content))


def data(data: RequestData, /) -> Decorator:
    return CompositionFacilitator(DataConsumer(data))


def files(files: RequestFiles, /) -> Decorator:
    return CompositionFacilitator(FilesConsumer(files))


def json(json: JsonTypes, /) -> Decorator:
    return CompositionFacilitator(JsonConsumer(json))


def timeout(timeout: TimeoutTypes, /) -> Decorator:
    return CompositionFacilitator(TimeoutConsumer(timeout))


def middleware(*middleware: MiddlewareCallable[Request, Response]) -> Decorator:
    def decorate(func: C, /) -> C:
        specification: OperationSpecification = get_operation(func).specification

        middleware_callable: MiddlewareCallable[Request, Response]
        for middleware_callable in middleware:
            specification.middleware.add(middleware_callable)

        return func

    return decorate


def user_agent(user_agent: str, /) -> Decorator:
    return header(HeaderName.USER_AGENT, user_agent)


def accept(*content_types: str) -> Decorator:
    return header(HeaderName.ACCEPT, ",".join(content_types))


def referer(referer: str, /) -> Decorator:
    return header(HeaderName.REFERER, referer)
