from typing import Mapping, Sequence

from ..consumers import (
    ContentConsumer,
    DataConsumer,
    FilesConsumer,
    JsonConsumer,
    MountConsumer,
    PathConsumer,
    PathParamsConsumer,
)
from ..converters import convert_path_param, convert_path_params
from ..types import (
    JsonTypes,
    PathParamsTypes,
    PathTypes,
    RequestContent,
    RequestData,
    RequestFiles,
)
from .api import OperationConsumerDecorator, OperationDecorator

__all__: Sequence[str] = (
    "content",
    "data",
    "files",
    "json",
    "mount",
    "path",
    "path_params",
)

def content(content: RequestContent, /) -> OperationDecorator:
    return OperationConsumerDecorator(ContentConsumer(content))


def data(data: RequestData, /) -> OperationDecorator:
    return OperationConsumerDecorator(DataConsumer(data))


def files(files: RequestFiles, /) -> OperationDecorator:
    return OperationConsumerDecorator(FilesConsumer(files))


def json(json: JsonTypes, /) -> OperationDecorator:
    return OperationConsumerDecorator(JsonConsumer(json))


def mount(path: str, /) -> OperationDecorator:
    return OperationConsumerDecorator(MountConsumer(path))


def path(
    key: str,
    value: PathTypes,
    *,
    delimiter: str = "/",
) -> OperationDecorator:
    converted_value: str = convert_path_param(value, delimiter=delimiter)

    return OperationConsumerDecorator(PathConsumer(key, converted_value))


def path_params(
    path_params: PathParamsTypes,
    /,
    *,
    delimiter: str = "/",
) -> OperationDecorator:
    converted_path_params: Mapping[str, str] = convert_path_params(
        path_params, delimiter=delimiter
    )

    return OperationConsumerDecorator(PathParamsConsumer(converted_path_params))
