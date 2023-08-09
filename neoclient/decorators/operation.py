from typing import Any, Callable, Sequence, TypeVar

from ..consumers import (
    ContentConsumer,
    DataConsumer,
    FilesConsumer,
    JsonConsumer,
    MountConsumer,
    PathConsumer,
    PathsConsumer,
)
from ..types import (
    JsonTypes,
    PathsTypes,
    PathTypes,
    RequestContent,
    RequestData,
    RequestFiles,
)
from .api import OperationConsumerDecorator

__all__: Sequence[str] = (
    "content",
    "data",
    "files",
    "json",
    "mount",
    "path",
    "path_params",
)

C = TypeVar("C", bound=Callable[..., Any])


def content(content: RequestContent, /) -> Callable[[C], C]:
    return OperationConsumerDecorator(ContentConsumer(content))


def data(data: RequestData, /) -> Callable[[C], C]:
    return OperationConsumerDecorator(DataConsumer(data))


def files(files: RequestFiles, /) -> Callable[[C], C]:
    return OperationConsumerDecorator(FilesConsumer(files))


def json(json: JsonTypes, /) -> Callable[[C], C]:
    return OperationConsumerDecorator(JsonConsumer(json))


def mount(path: str, /) -> Callable[[C], C]:
    return OperationConsumerDecorator(MountConsumer(path))


def path(key: str, value: PathTypes) -> Callable[[C], C]:
    return OperationConsumerDecorator(PathConsumer(key, value))


def path_params(path_params: PathsTypes, /) -> Callable[[C], C]:
    return OperationConsumerDecorator(PathsConsumer(path_params))
