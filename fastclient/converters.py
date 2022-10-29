from typing import (
    Any,
    MutableMapping,
)

from httpx import Cookies, Headers, QueryParams, Timeout
from httpx._utils import primitive_value_to_str

from .types import (
    CookieTypes,
    HeaderTypes,
    PathParamValueTypes,
    QueryParamTypes,
    TimeoutTypes,
    PathParamTypes,
    Primitive,
)


def convert_query_param(value: Any, /) -> str:
    return primitive_value_to_str(value)


def convert_header(value: Any, /) -> str:
    return primitive_value_to_str(value)


def convert_cookie(value: Any, /) -> str:
    return primitive_value_to_str(value)


def convert_path_param(value: PathParamValueTypes, /) -> str:
    if isinstance(value, (str, int, float, bool, type(None))):
        return primitive_value_to_str(value)
    else:
        return "/".join(primitive_value_to_str(v) for v in value)


def convert_query_params(value: QueryParamTypes, /) -> QueryParams:
    return QueryParams(value)


def convert_headers(value: HeaderTypes, /) -> Headers:
    return Headers(value)


def convert_cookies(value: CookieTypes, /) -> Cookies:
    return Cookies(value)


def convert_path_params(path_params: PathParamTypes, /) -> MutableMapping[str, str]:
    return {
        key: convert_path_param(value)
        for key, value in path_params.items()
    }

    # path_parameters: MutableMapping[str, str] = {}

    # key: str
    # value: Union[Primitive, Sequence[Primitive]]
    # for key, value in path_params.items():
    #     # primitive_value: Primitive

    #     # if utils.is_primitive(value):
    #     if isinstance(value, (str, int, float, bool, type(None))):
    #         path_parameters[key] = primitive_value_to_str(value)
    #     else:
    #         path_parameters[key] = "/".join(primitive_value_to_str(v) for v in value)

    # return path_parameters


# def convert_path_params(path_params: PathParamTypes, /) -> PathParams:
#     # return PathParams(value)

#     if isinstance(path_params, PathParams):
#         return path_params
#     elif isinstance(path_params, Mapping):
#         return PathParams(
#             kwargs={
#                 key: primitive_value_to_str(value)
#                 for key, value in path_params.items()
#             },
#         )
#     elif isinstance(path_params, Collection):
#         return PathParams(
#             args=[
#                 primitive_value_to_str(value)
#                 for value in path_params
#             ],
#         )
#     else:
#         raise ValueError(f"Failed to convert path params {path_params!r}, unsupported type.")


def convert_timeout(value: TimeoutTypes, /) -> Timeout:
    return Timeout(value)
