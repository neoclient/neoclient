from typing import Mapping

from neoclient.decorators.api import request_options_decorator
from neoclient.models import RequestOptions

from ..converters import convert_path_param, convert_path_params
from ..types import (
    JsonTypes,
    PathParamsTypes,
    PathTypes,
    RequestContent,
    RequestData,
    RequestFiles,
)

__all__ = (
    "content",
    "data",
    "files",
    "json",
    "mount",
    "path",
    "path_params",
)

# TODO: Type responses


def content(content: RequestContent, /):
    @request_options_decorator
    def decorate(request_options: RequestOptions, /) -> None:
        request_options.content = content

    return decorate


def data(data: RequestData, /):
    @request_options_decorator
    def decorate(request_options: RequestOptions, /) -> None:
        request_options.data = data

    return decorate


def files(files: RequestFiles, /):
    @request_options_decorator
    def decorate(request_options: RequestOptions, /) -> None:
        request_options.files = files

    return decorate


def json(json: JsonTypes, /):
    @request_options_decorator
    def decorate(request_options: RequestOptions, /) -> None:
        request_options.json = json

    return decorate


def mount(path: str, /):
    @request_options_decorator
    def decorate(request_options: RequestOptions, /) -> None:
        request_options.url = request_options.url.copy_with(
            path=path + request_options.url.path
        )

    return decorate


def path(
    key: str,
    value: PathTypes,
    *,
    delimiter: str = "/",
):
    @request_options_decorator
    def decorate(request_options: RequestOptions, /) -> None:
        converted_value: str = convert_path_param(value, delimiter=delimiter)

        request_options.path_params[key] = converted_value

    return decorate


def path_params(
    path_params: PathParamsTypes,
    /,
    *,
    delimiter: str = "/",
):
    @request_options_decorator
    def decorate(request_options: RequestOptions, /) -> None:
        converted_path_params: Mapping[str, str] = convert_path_params(
            path_params, delimiter=delimiter
        )

        request_options.path_params.update(converted_path_params)

    return decorate
