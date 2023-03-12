from typing import Sequence

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
from .api import CompositionDecorator, Decorator

__all__: Sequence[str] = (
    "content",
    "data",
    "files",
    "json",
    "mount",
    "path",
    "path_params",
)


def content(content: RequestContent, /) -> Decorator:
    return CompositionDecorator(ContentConsumer(content))


def data(data: RequestData, /) -> Decorator:
    return CompositionDecorator(DataConsumer(data))


def files(files: RequestFiles, /) -> Decorator:
    return CompositionDecorator(FilesConsumer(files))


def json(json: JsonTypes, /) -> Decorator:
    return CompositionDecorator(JsonConsumer(json))


def mount(path: str, /) -> Decorator:
    return CompositionDecorator(MountConsumer(path))


def path(key: str, value: PathTypes) -> Decorator:
    return CompositionDecorator(PathConsumer(key, value))


def path_params(path_params: PathsTypes, /) -> Decorator:
    return CompositionDecorator(PathsConsumer(path_params))
