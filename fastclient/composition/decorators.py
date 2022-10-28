from dataclasses import dataclass
from typing import Any, Callable, Mapping, TypeVar
from typing_extensions import ParamSpec

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
from .factories import (
    ContentComposer,
    DataComposer,
    FilesComposer,
    JsonComposer,
)
from .typing import C, Decorator, RequestConsumer, RequestConsumerFactory

PS = ParamSpec("PS")
RT = TypeVar("RT")


@dataclass
class CompositionFacilitator(Decorator):
    composer: RequestConsumer

    def __call__(self, func: C, /) -> C:
        logger.info(f"Composing {func!r} using {self.composer!r}")

        # TODO: Use get_operation(...)
        self.composer(func.operation.specification.request)

        return func

# DEPRECATED?
def _deprecated_composition_facilitator(
    request_consumer_factory: RequestConsumerFactory[RT],
    bundler: Callable[PS, RT],
):
    def wrapper(*args: PS.args, **kwargs: PS.kwargs) -> Callable[[C], C]:
        bundled: RT = bundler(*args, **kwargs)

        composer: RequestConsumer = request_consumer_factory(bundled)

        def decorate(func: C, /) -> C:
            logger.info(f"Composing {func!r} using {composer!r}")

            # TODO: Use get_operation(...)
            composer(func.operation.specification.request)

            return func

        return decorate

    return wrapper

def query(key: str, value: Any) -> Decorator:
    consumer: RequestConsumer = wrappers.query(key, value)

    return CompositionFacilitator(consumer)


def header(key: str, value: Any) -> Decorator:
    consumer: RequestConsumer = wrappers.header(key, value)

    return CompositionFacilitator(consumer)


def cookie(key: str, value: Any) -> Decorator:
    consumer: RequestConsumer = wrappers.cookie(key, value)

    return CompositionFacilitator(consumer)


def path(key: str, value: Any) -> Decorator:
    consumer: RequestConsumer = wrappers.path(key, value)

    return CompositionFacilitator(consumer)


def query_params(params: QueryParamTypes, /) -> Decorator:
    consumer: RequestConsumer = wrappers.query_params(params)

    return CompositionFacilitator(consumer)


def headers(headers: HeaderTypes, /) -> Decorator:
    consumer: RequestConsumer = wrappers.headers(headers)

    return CompositionFacilitator(consumer)


def cookies(cookies: CookieTypes, /) -> Decorator:
    consumer: RequestConsumer = wrappers.cookies(cookies)

    return CompositionFacilitator(consumer)


def path_params(path_params: Mapping[str, Any], /) -> Decorator:
    consumer: RequestConsumer = wrappers.path_params(path_params)

    return CompositionFacilitator(consumer)


def content(content: RequestContent, /) -> Decorator:
    consumer: RequestConsumer = ContentComposer(content)

    return CompositionFacilitator(consumer)


def data(data: RequestData, /) -> Decorator:
    consumer: RequestConsumer = DataComposer(data)

    return CompositionFacilitator(consumer)


def files(files: RequestFiles, /) -> Decorator:
    consumer: RequestConsumer = FilesComposer(files)

    return CompositionFacilitator(consumer)


def json(json: JsonTypes, /) -> Decorator:
    consumer: RequestConsumer = JsonComposer(json)

    return CompositionFacilitator(consumer)


def timeout(timeout: TimeoutTypes, /) -> Decorator:
    consumer: RequestConsumer = wrappers.timeout(timeout)

    return CompositionFacilitator(consumer)
