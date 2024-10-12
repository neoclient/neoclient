import inspect
from typing import Mapping, Optional

from di.api.providers import DependencyProvider

from neoclient.di.dependencies import request_headers, request_params

NAME_LOOKUP: Mapping[str, DependencyProvider] = {
    "headers": request_headers,
    "params": request_params,
}


def infer_dependency(parameter: inspect.Parameter, /) -> Optional[DependencyProvider]:
    if parameter.name in NAME_LOOKUP:
        return NAME_LOOKUP[parameter.name]

    return None
