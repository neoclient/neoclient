import inspect
from typing import Optional

from di.api.providers import DependencyProvider
from httpx import Cookies, Headers, QueryParams

from neoclient.di.dependencies import DEPENDENCIES
from neoclient.di.enums import Profile

# TODO: Support names like "request_headers"
NAME_LOOKUP = {
    "headers": Headers,
    "params": QueryParams,
    "cookies": Cookies,
}


def infer_dependency(
    parameter: inspect.Parameter, profile: Profile
) -> Optional[DependencyProvider]:
    dependencies = DEPENDENCIES[profile]

    if parameter.name in NAME_LOOKUP:
        typ = NAME_LOOKUP[parameter.name]

        if typ in dependencies:
            return dependencies[typ]

    return None
