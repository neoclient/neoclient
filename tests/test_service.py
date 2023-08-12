from types import MethodType

import pytest

from neoclient.client import Client
from neoclient.decorators import (
    get,
    middleware,
    request_depends,
    response_depends,
    service,
)
from neoclient.models import ClientOptions
from neoclient.operation import Operation, get_operation
from neoclient.services import Service


def some_middleware(call_next, request):
    return call_next(request)


def some_request_dependency():
    pass


def some_response_dependency():
    pass


class SomeService(Service):
    @response_depends(some_response_dependency)
    @request_depends(some_request_dependency)
    @middleware(some_middleware)
    @get("/foo")
    def foo(self):
        ...

    @service.middleware
    def some_service_middleware(self, call_next, request):
        return call_next(request)

    @service.request_depends
    def some_service_request_dependency(self):
        pass

    @service.response_depends
    def some_service_response_dependency(self):
        pass


def test_default_opts() -> None:
    assert SomeService._spec.options == ClientOptions()


@pytest.mark.skip(
    reason="`httpx.Client.__eq__` not suitable for comparing two identical clients"
)
def test_default_client() -> None:
    assert SomeService()._client == Client(client=ClientOptions().build())


def test_method_bound_to_instance() -> None:
    service: SomeService = SomeService()

    assert isinstance(service.foo, MethodType)
    assert service.foo.__self__ == service


def test_method_bound_to_client() -> None:
    service: SomeService = SomeService()

    operation: Operation = get_operation(service.foo)

    assert operation.func is service.foo
    assert operation.client == service._client.client


def test_service_middleware() -> None:
    service: SomeService = SomeService()

    assert service._client.middleware.record == [service.some_service_middleware]
    assert get_operation(service.foo).middleware.record == [
        some_middleware,
        service.some_service_middleware,
    ]


def test_service_response() -> None:
    class SomeService(Service):
        @get("/foo")
        def foo(self) -> str:
            ...

        @service.response
        def some_service_response(self) -> str:
            return "foo"

    some_service: SomeService = SomeService()

    assert some_service._client.default_response == some_service.some_service_response
    assert (
        get_operation(some_service.foo).response == some_service.some_service_response
    )


def test_service_request_dependencies() -> None:
    service: SomeService = SomeService()

    assert service._client.request_dependencies == [
        service.some_service_request_dependency
    ]
    assert get_operation(service.foo).request_dependencies == [
        some_request_dependency,
        service.some_service_request_dependency,
    ]


def test_service_response_dependencies() -> None:
    service: SomeService = SomeService()

    assert service._client.response_dependencies == [
        service.some_service_response_dependency
    ]
    assert get_operation(service.foo).response_dependencies == [
        some_response_dependency,
        service.some_service_response_dependency,
    ]
