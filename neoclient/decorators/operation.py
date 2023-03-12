from typing import Callable, Sequence
from typing_extensions import TypeAlias

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
from ..typing import Decorator
from .api import ConsumerDecorator

__all__: Sequence[str] = (
    "content",
    "data",
    "files",
    "json",
    "mount",
    "path",
    "path_params",
)

OperationDecorator: TypeAlias = Decorator[Callable]


def content(content: RequestContent, /) -> OperationDecorator:
    return ConsumerDecorator(ContentConsumer(content))


def data(data: RequestData, /) -> OperationDecorator:
    return ConsumerDecorator(DataConsumer(data))


def files(files: RequestFiles, /) -> OperationDecorator:
    return ConsumerDecorator(FilesConsumer(files))


def json(json: JsonTypes, /) -> OperationDecorator:
    return ConsumerDecorator(JsonConsumer(json))


def mount(path: str, /) -> OperationDecorator:
    return ConsumerDecorator(MountConsumer(path))


def path(key: str, value: PathTypes) -> OperationDecorator:
    return ConsumerDecorator(PathConsumer(key, value))


def path_params(path_params: PathsTypes, /) -> OperationDecorator:
    return ConsumerDecorator(PathsConsumer(path_params))
