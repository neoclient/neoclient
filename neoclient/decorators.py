from dataclasses import dataclass
from typing import Any, Callable, Optional, Protocol, Sequence, Type, TypeVar

from httpx import URL
from mediate.protocols import MiddlewareCallable

from .consumers import (
    BaseURLConsumer,
    Consumer,
    ContentConsumer,
    CookieConsumer,
    CookiesConsumer,
    DataConsumer,
    FilesConsumer,
    HeaderConsumer,
    HeadersConsumer,
    JsonConsumer,
    MountConsumer,
    PathConsumer,
    PathsConsumer,
    QueriesConsumer,
    QueryConsumer,
    TimeoutConsumer,
)
from .enums import HeaderName
from .errors import CompositionError
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
    "service",
)

S = TypeVar("S", bound=Type[Service])
T = TypeVar("T", Callable, Type[Service])


class Decorator(Protocol):
    def __call__(self, target: T, /) -> T:
        ...


@dataclass
class CompositionDecorator(Decorator):
    consumer: Consumer

    def __call__(self, target: T, /) -> T:
        if isinstance(target, type):
            if not issubclass(target, Service):
                raise CompositionError(f"Target class is not a subclass of {Service}")

            client: ClientOptions = target._spec.options

            self.consumer.consume_client(client)
        elif callable(target):
            request: PreRequest = get_operation(target).specification.request

            self.consumer.consume_request(request)
        else:
            raise CompositionError(f"Target of unsupported type {type(target)}")

        return target


def query(key: str, value: QueryTypes) -> Decorator:
    return CompositionDecorator(QueryConsumer(key, value))


def header(key: str, value: HeaderTypes) -> Decorator:
    return CompositionDecorator(HeaderConsumer(key, value))


def cookie(key: str, value: CookieTypes) -> Decorator:
    return CompositionDecorator(CookieConsumer(key, value))


def path(key: str, value: PathTypes) -> Decorator:
    return CompositionDecorator(PathConsumer(key, value))


def query_params(params: QueriesTypes, /) -> Decorator:
    return CompositionDecorator(QueriesConsumer(params))


def headers(headers: HeadersTypes, /) -> Decorator:
    return CompositionDecorator(HeadersConsumer(headers))


def cookies(cookies: CookiesTypes, /) -> Decorator:
    return CompositionDecorator(CookiesConsumer(cookies))


def path_params(path_params: PathsTypes, /) -> Decorator:
    return CompositionDecorator(PathsConsumer(path_params))


def content(content: RequestContent, /) -> Decorator:
    return CompositionDecorator(ContentConsumer(content))


def data(data: RequestData, /) -> Decorator:
    return CompositionDecorator(DataConsumer(data))


def files(files: RequestFiles, /) -> Decorator:
    return CompositionDecorator(FilesConsumer(files))


def json(json: JsonTypes, /) -> Decorator:
    return CompositionDecorator(JsonConsumer(json))


def timeout(timeout: TimeoutTypes, /) -> Decorator:
    return CompositionDecorator(TimeoutConsumer(timeout))


def mount(path: str, /) -> Decorator:
    return CompositionDecorator(MountConsumer(path))


def base_url(base_url: str, /) -> Decorator:
    return CompositionDecorator(BaseURLConsumer(base_url))


def middleware(*middleware: MiddlewareCallable[Request, Response]) -> Decorator:
    def decorate(target: T, /) -> T:
        if isinstance(target, type) and issubclass(target, Service):
            raise CompositionError(
                "Middleware decorator currently unsupported for service classes"
            )

        specification: OperationSpecification = get_operation(target).specification

        specification.middleware.add_all(middleware)

        return target

    return decorate


def user_agent(user_agent: str, /) -> Decorator:
    return header(HeaderName.USER_AGENT, user_agent)


def accept(*content_types: str) -> Decorator:
    return header(HeaderName.ACCEPT, ",".join(content_types))


def referer(referer: str, /) -> Decorator:
    return header(HeaderName.REFERER, referer)


def service(
    base_url: Optional[str] = None,
    *,
    middleware: Optional[Sequence[MiddlewareCallable[Request, Response]]] = None,
    default_response: Optional[Callable[..., Any]] = None,
):
    def decorate(target: S, /) -> S:
        if base_url is not None:
            target._spec.options.base_url = URL(base_url)
        if middleware is not None:
            target._spec.middleware.add_all(middleware)
        if default_response is not None:
            target._spec.default_response = default_response

        return target

    return decorate
