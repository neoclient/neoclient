from typing import Any, Callable, Mapping, Sequence, TypeVar

from ..converters import convert_path_param, convert_path_params

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


def path(
    key: str,
    value: PathTypes,
    *,
    delimiter: str = "/",
) -> Callable[[C], C]:
    converted_value: str = convert_path_param(value, delimiter=delimiter)

    return OperationConsumerDecorator(PathConsumer(key, converted_value))


def path_params(
    path_params: PathsTypes,
    /,
    *,
    delimiter: str = "/",
) -> Callable[[C], C]:
    converted_path_params: Mapping[str, str] = convert_path_params(
        path_params, delimiter=delimiter
    )

    return OperationConsumerDecorator(PathsConsumer(converted_path_params))
