from typing import Callable, Optional

import pytest
from httpx import Headers
from pydantic import BaseModel, Required

from neoclient import Body, NeoClient, Queries, Query
from neoclient.decorators import request
from neoclient.middlewares import RequestMiddleware
from neoclient.models import PreRequest, Request, Response
from neoclient.operation import Operation, get_operation


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

    def response() -> None:
        pass

    def middleware(call_next, request):
        pass

    def request_dependency() -> None:
        pass

    def response_dependency() -> None:
        pass

    @request(method, endpoint, response=response)
    def foo():
        ...

    unbound_operation: Operation = get_operation(foo)

    unbound_operation.middleware.add(middleware)
    unbound_operation.request_dependencies.append(request_dependency)
    unbound_operation.response_dependencies.append(response_dependency)

    bound_foo: Callable = client.bind(foo)

    bound_operation: Operation = get_operation(bound_foo)

    assert bound_operation.func != foo
    assert bound_operation.client == client.client
    assert bound_operation.middleware.record == [middleware]
    assert bound_operation.response == response
    assert bound_operation.request_dependencies == [request_dependency]
    assert bound_operation.response_dependencies == [response_dependency]


def test_request(client: NeoClient) -> None:
    method: str = "METHOD"
    endpoint: str = "/endpoint"

    def response() -> None:
        return None

    @client.request(method, endpoint, response=response)
    def foo():
        ...

    assert get_operation(foo).request_options == PreRequest(
        method=method,
        url=endpoint,
    )
    assert get_operation(foo).response is response
    assert get_operation(foo).client == client.client


def test_query_not_required_omitted(client: NeoClient) -> None:
    @client.get("get")
    def get(query: Optional[str] = Query(default=None)) -> PreRequest:
        ...

    assert get() == PreRequest(
        method="GET",
        url="get",
    )


def test_query_required_not_omitted(client: NeoClient) -> None:
    @client.get("get")
    def get(query: Optional[str] = Query(default=Required)) -> PreRequest:
        ...

    assert get("foo") == PreRequest(
        method="GET",
        url="get",
        params={"query": "foo"},
    )


def test_single_body_param(client: NeoClient) -> None:
    @client.post("/items/")
    def create_item(item: Item = Body()) -> PreRequest:
        ...

    assert create_item(Item(id=1, name="item")) == PreRequest(
        method="POST",
        url="/items/",
        json={"id": 1, "name": "item"},
    )


def test_multiple_body_params(client: NeoClient) -> None:
    @client.post("/items/")
    def create_item(user: User = Body(), item: Item = Body()) -> PreRequest:
        ...

    assert create_item(User(id=1, name="user"), Item(id=1, name="item")) == PreRequest(
        method="POST",
        url="/items/",
        json={
            "user": {"id": 1, "name": "user"},
            "item": {"id": 1, "name": "item"},
        },
    )


def test_multiple_body_params_embedded(client: NeoClient) -> None:
    @client.post("/items/")
    def create_item(
        user: User = Body(embed=True), item: Item = Body(embed=True)
    ) -> PreRequest:
        ...

    assert create_item(User(id=1, name="user"), Item(id=1, name="item")) == PreRequest(
        method="POST",
        url="/items/",
        json={
            "user": {"id": 1, "name": "user"},
            "item": {"id": 1, "name": "item"},
        },
    )


def test_single_query_param(client: NeoClient) -> None:
    @client.get("/items/")
    def create_item(sort: str = Query()) -> PreRequest:
        ...

    assert create_item("ascending") == PreRequest(
        method="GET",
        url="/items/",
        params={
            "sort": "ascending",
        },
    )


def test_multiple_query_params(client: NeoClient) -> None:
    @client.get("/items/")
    def create_item(params: dict = Queries()) -> PreRequest:
        ...

    assert create_item({"sort": "ascending"}) == PreRequest(
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


def test_client_request_dependencies(client: NeoClient) -> None:
    @client.request_depends
    def request_dependency(headers=Headers()) -> None:
        headers["name"] = "sam"

    assert client.request_dependencies == [request_dependency]

    @client.get("/foo")
    def foo():
        ...

    assert get_operation(foo).request_dependencies == [request_dependency]


def test_client_response_dependencies(client: NeoClient) -> None:
    @client.response_depends
    def response_dependency():
        ...

    assert client.response_dependencies == [response_dependency]

    @client.get("/foo")
    def foo():
        ...

    assert get_operation(foo).response_dependencies == [response_dependency]
