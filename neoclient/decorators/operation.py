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

C = TypeVar("C", bound=Callable[..., Any])


def content(content: RequestContent, /) -> Callable[[C], C]:
    return ConsumerDecorator(ContentConsumer(content))


def data(data: RequestData, /) -> Callable[[C], C]:
    return ConsumerDecorator(DataConsumer(data))


def files(files: RequestFiles, /) -> Callable[[C], C]:
    return ConsumerDecorator(FilesConsumer(files))


def json(json: JsonTypes, /) -> Callable[[C], C]:
    return ConsumerDecorator(JsonConsumer(json))


def mount(path: str, /) -> Callable[[C], C]:
    return ConsumerDecorator(MountConsumer(path))


def path(key: str, value: PathTypes) -> Callable[[C], C]:
    return ConsumerDecorator(PathConsumer(key, value))


def path_params(path_params: PathsTypes, /) -> Callable[[C], C]:
    return ConsumerDecorator(PathsConsumer(path_params))
