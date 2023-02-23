from http import HTTPStatus

from httpx import Headers, Request, Response
from pydantic import Required, BaseConfig
from pydantic.fields import ModelField
import pytest

from neoclient import Cookie
from neoclient.dependencies import DependencyParameter, DependencyResolver, get_fields
from neoclient.enums import HttpMethod
from neoclient.errors import ResolutionError, PreparationError
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
        "query": (str, QueryParameter(alias="query", default=Required)),
        "body": (dict, BodyParameter(alias="body", default=Required)),
        "headers": (Headers, HeadersParameter(alias="headers", default=Required)),
        "cookie": (int, CookieParameter(alias="cookie", default=Required)),
    }


def test_DependencyResolver() -> None:
    def dependency(response: Response, /) -> Response:
        return response

    response: Response = Response(
        HTTPStatus.OK, request=Request(HttpMethod.GET, "https://foo.com/")
    )

    assert DependencyResolver(dependency)(response) == response


def test_DependencyParameter_resolve() -> None:
    def dependency(response: Response, /) -> Response:
        return response

    response: Response = Response(
        HTTPStatus.OK, request=Request(HttpMethod.GET, "https://foo.com/")
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


def test_DependencyParameter_prepare() -> None:
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

    assert dependency_parameter_with_dependency.dependency == some_dependency

    dependency_parameter_without_dependency.prepare(model_field)

    assert dependency_parameter_without_dependency.dependency == SomeDependency
