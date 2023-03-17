from types import MethodType

import pytest

from neoclient import get, middleware, service_middleware
from neoclient.client import Client
from neoclient.models import ClientOptions
from neoclient.operation import Operation, get_operation
from neoclient.service import Service


def some_middleware(call_next, request):
    return call_next(request)


class SomeService(Service):
    @middleware(some_middleware)
    @get("/foo")
    def foo(self):
        ...

    @service_middleware
    def some_service_middleware(self, call_next, request):
        return call_next(request)


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
