import inspect
from typing import Optional

from di.api.providers import DependencyProvider
from httpx import URL, Cookies, Headers, QueryParams, Request

from neoclient.di.dependencies import DEPENDENCIES
from neoclient.di.enums import Profile
from neoclient.models import RequestOpts

# # TODO: Support names like "request_headers"
# NAME_LOOKUP = {
#     "headers": Headers,
#     "params": QueryParams,
#     "cookies": Cookies,
#     # "request": RequestOpts or Request?
#     # "response"
#     "url": URL,
#     "request_opts": RequestOpts,
# }

# NAME_LOOKUP_REQUEST = {
#     "request": RequestOpts,
# }
# NAME_LOOKUP_RESPONSE = {
#     "request": Request,
# }


# def _infer_by_name(name: str, profile: Profile) -> Optional[DependencyProvider]:
#     dependencies = DEPENDENCIES[profile]
#     lookups = {
#         Profile.REQUEST: NAME_LOOKUP_REQUEST,
#         Profile.RESPONSE: NAME_LOOKUP_RESPONSE,
#     }
#     name_lookup = {**NAME_LOOKUP, **lookups[profile]}

#     if name in name_lookup:
#         typ = name_lookup[name]

#         if typ in dependencies:
#             return dependencies[typ]
        
#     return None


def infer_dependency(
    parameter: inspect.Parameter, profile: Profile
) -> Optional[DependencyProvider]:
    # No inference:
    # * Parameter metadata exists, use that. (e.g. headers = Headers())
    # Inference:
    # 1. Parameter name matches a path parameter, assume a path param
    # 2. Type is a known dependency (e.g. headers: Headers), no inference needed.
    # 3. Type indicates a body parameter (e.g. user: User), treat as body parameter.
    # 4. Assume query parameter
    # Don't do:
    # * Infer by name? Only do if not typed? Only do for select few? (FastAPI doesn't do this.)

    # Infer by parameter name (deprecated)
    # if provider := _infer_by_name(parameter.name, profile):
    #     return provider

    # 1.

    return None



def my_response(name):
    ...