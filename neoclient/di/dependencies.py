import inspect
from typing import Any, Callable, MutableMapping, NoReturn, TypeVar

from di.api.providers import DependencyProviderType
from httpx import Cookies, Headers, QueryParams

from neoclient.models import RequestOpts

C = TypeVar("C", bound=Callable[..., Any])

DEPENDENCIES: MutableMapping[type, DependencyProviderType[type]] = {}


def dependency(func: C, /) -> C:
    annotation: Any = inspect.signature(func).return_annotation

    assert isinstance(annotation, type)

    DEPENDENCIES[annotation] = func

    return func


# def not_wirable() -> NoReturn:
#     raise Exception("Not wirable")  # TODO: Raise appropriate exception
#     # Spring throws:
#     # NoSuchBeanDefinitionException:
#     #   No qualifying bean of type [com.baeldung.packageB.BeanB]
#     #       found for dependency:
#     #   expected at least 1 bean which qualifies as
#     #       autowire candidate for this dependency.


@dependency
def request_headers(request: RequestOpts, /) -> Headers:
    return request.headers


@dependency
def request_params(request: RequestOpts, /) -> QueryParams:
    return request.params

@dependency
def request_cookies(request: RequestOpts, /) -> Cookies:
    return request.cookies