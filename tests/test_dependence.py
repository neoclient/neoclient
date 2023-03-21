from http import HTTPStatus

import pytest
from httpx import Headers
from pydantic import BaseConfig
from pydantic.fields import ModelField

from neoclient import Cookie
from neoclient.dependence import DependencyParameter, DependencyResolver, get_fields
from neoclient.enums import HTTPMethod
from neoclient.errors import ResolutionError
from neoclient.models import Request, Response
from neoclient.params import (
    BodyParameter,
    CookieParameter,
    HeadersParameter,
    QueryParameter,
)


def test_get_fields() -> None:
    def foo(query: str, body: dict, headers: Headers, cookie: int = Cookie()) -> None:
        ...

    assert get_fields(foo) == {
        "query": (str, QueryParameter(alias="query")),
        "body": (dict, BodyParameter(alias="body")),
        "headers": (Headers, HeadersParameter(alias="headers")),
        "cookie": (int, CookieParameter(alias="cookie")),
    }


def test_dependency_resolver_() -> None:
    def dependency(response: Response, /) -> Response:
        return response

    response: Response = Response(
        HTTPStatus.OK, request=Request(HTTPMethod.GET, "https://foo.com/")
    )

    assert DependencyResolver(dependency)(response) == response


def test_dependency_parameter_resolve() -> None:
    def dependency(response: Response, /) -> Response:
        return response

    response: Response = Response(
        HTTPStatus.OK, request=Request(HTTPMethod.GET, "https://foo.com/")
    )

    dependency_parameter_with_dependency: DependencyParameter = DependencyParameter(
        dependency=dependency
    )
    dependency_parameter_without_dependency: DependencyParameter = DependencyParameter(
        dependency=None
    )

    assert dependency_parameter_with_dependency.resolve(response) == response

    with pytest.raises(ResolutionError):
        dependency_parameter_without_dependency.resolve(response)


def test_dependency_parameter_prepare() -> None:
    def some_dependency(response: Response, /) -> Response:
        return response

    class SomeDependency:
        response: Response

        def __init__(self, response: Response) -> None:
            self.response = response

    class Config(BaseConfig):
        arbitrary_types_allowed: bool = True

    model_field: ModelField = ModelField(
        name="some_field",
        type_=SomeDependency,
        class_validators=None,
        model_config=Config,
    )

    dependency_parameter_with_dependency: DependencyParameter = DependencyParameter(
        dependency=some_dependency
    )
    dependency_parameter_without_dependency: DependencyParameter = DependencyParameter(
        dependency=None
    )

    dependency_parameter_with_dependency.prepare(model_field)

    assert dependency_parameter_with_dependency.dependency is some_dependency

    dependency_parameter_without_dependency.prepare(model_field)

    assert dependency_parameter_without_dependency.dependency == SomeDependency
