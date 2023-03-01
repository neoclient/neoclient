from types import MethodType
from typing import Type

import pytest
from pytest import fixture

from neoclient import get
from neoclient.client import Client
from neoclient.models import ClientOptions
from neoclient.operation import Operation, get_operation
from neoclient.service import Service


class SomeService(Service):
    @get("/foo")
    def foo(self):
        ...


def test_default_opts() -> None:
    assert SomeService._opts == ClientOptions()


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

    assert operation.func == service.foo
    assert operation.client == service._client.client
