from typing import Callable, Optional, Protocol

import pytest
from httpx import Headers, Request, Response
from pydantic import BaseModel, Required

from neoclient import Body, NeoClient, Queries, Query
from neoclient.methods import get, post, request
from neoclient.middleware import RequestMiddleware
from neoclient.models import OperationSpecification, RequestOptions
from neoclient.operation import get_operation


class Model(BaseModel):
    id: int
    name: str


class User(Model):
    pass


class Item(Model):
    pass


@pytest.fixture
def client() -> NeoClient:
    return NeoClient()


def test_bind(client: NeoClient) -> None:
    method: str = "METHOD"
    endpoint: str = "/endpoint"
    response: Callable = lambda: None

    @request(method, endpoint, response=response)
    def foo():
        ...

    bound_foo: Callable = client.bind(foo)

    assert get_operation(bound_foo).client == client.client


def test_request(client: NeoClient) -> None:
    method: str = "METHOD"
    endpoint: str = "/endpoint"
    response: Callable = lambda: None

    @client.request(method, endpoint, response=response)
    def foo():
        ...

    assert get_operation(foo).specification == OperationSpecification(
        request=RequestOptions(
            method=method,
            url=endpoint,
        ),
        response=response,
    )
    assert get_operation(foo).client == client.client


def test_query_not_required_omitted(client: NeoClient) -> None:
    class Service(Protocol):
        @get("get")
        def get(self, q: Optional[str] = Query(default=None)) -> RequestOptions:
            ...

    service: Service = client.create(Service)  # type: ignore

    assert service.get() == RequestOptions(
        method="GET",
        url="get",
    )


def test_query_required_not_omitted(client: NeoClient) -> None:
    class Service(Protocol):
        @get("get")
        def get(self, q: Optional[str] = Query(default=Required)) -> RequestOptions:
            ...

    service: Service = client.create(Service)  # type: ignore

    assert service.get("foo") == RequestOptions(
        method="GET",
        url="get",
        params={"q": "foo"},
    )


def test_single_body_param(client: NeoClient) -> None:
    class Service(Protocol):
        @post("/items/")
        def create_item(self, item: Item = Body()) -> RequestOptions:
            ...

    service: Service = client.create(Service)  # type: ignore

    assert service.create_item(Item(id=1, name="item")) == RequestOptions(
        method="POST",
        url="/items/",
        json={"id": 1, "name": "item"},
    )


def test_multiple_body_params(client: NeoClient) -> None:
    class Service(Protocol):
        @post("/items/")
        def create_item(
            self, user: User = Body(), item: Item = Body()
        ) -> RequestOptions:
            ...

    service: Service = client.create(Service)  # type: ignore

    assert service.create_item(
        User(id=1, name="user"), Item(id=1, name="item")
    ) == RequestOptions(
        method="POST",
        url="/items/",
        json={
            "user": {"id": 1, "name": "user"},
            "item": {"id": 1, "name": "item"},
        },
    )


def test_multiple_body_params_embedded(client: NeoClient) -> None:
    class Service(Protocol):
        @post("/items/")
        def create_item(
            self, user: User = Body(embed=True), item: Item = Body(embed=True)
        ) -> RequestOptions:
            ...

    service: Service = client.create(Service)  # type: ignore

    assert service.create_item(
        User(id=1, name="user"), Item(id=1, name="item")
    ) == RequestOptions(
        method="POST",
        url="/items/",
        json={
            "user": {"id": 1, "name": "user"},
            "item": {"id": 1, "name": "item"},
        },
    )


def test_single_query_param(client: NeoClient) -> None:
    class Service(Protocol):
        @get("/items/")
        def create_item(self, sort: str = Query()) -> RequestOptions:
            ...

    service: Service = client.create(Service)  # type: ignore

    assert service.create_item("ascending") == RequestOptions(
        method="GET",
        url="/items/",
        params={
            "sort": "ascending",
        },
    )


def test_multiple_query_params(client: NeoClient) -> None:
    class Service(Protocol):
        @get("/items/")
        def create_item(self, params: dict = Queries()) -> RequestOptions:
            ...

    service: Service = client.create(Service)  # type: ignore

    assert service.create_item({"sort": "ascending"}) == RequestOptions(
        method="GET",
        url="/items/",
        params={
            "sort": "ascending",
        },
    )


def test_client_middleware(client: NeoClient) -> None:
    @client.middleware
    def some_middleware(_: RequestMiddleware, request: Request) -> Response:
        request.headers["name"] = "sam"

        # As a mock HTTP server is not currently being used, the response is faked
        return Response(
            200,
            headers=Headers({"food": "pizza"}),
            text="Hello!",
            request=request,
        )

    @client.get("/foo")
    def foo() -> Response:
        ...

    response: Response = foo()

    assert response.request.headers.get("name") == "sam"
    assert response.headers.get("food") == "pizza"
