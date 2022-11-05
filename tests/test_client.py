from typing import Optional, Protocol

import pytest
from pydantic import BaseModel, Required

from fastclient import Body, FastClient, Path, Query, get, post
from fastclient.errors import IncompatiblePathParameters
from fastclient.models import RequestOptions
from fastclient import Queries


class Model(BaseModel):
    id: int
    name: str


class User(Model):
    pass


class Item(Model):
    pass


@pytest.fixture
def client() -> FastClient:
    return FastClient()


def test_query_not_required_omitted(client: FastClient):
    class Service(Protocol):
        @get("get")
        def get(self, q: Optional[str] = Query()) -> RequestOptions:
            ...

    service: Service = client.create(Service)  # type: ignore

    assert service.get() == RequestOptions(
        method="GET",
        url="get",
    )


def test_query_required_not_omitted(client: FastClient):
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


# TODO: Stop skipping this test
@pytest.mark.skip(reason="Functionality temporarily removed, needs to be re-added")
def test_error_if_extra_path_param(client: FastClient):
    with pytest.raises(IncompatiblePathParameters):

        class Service(Protocol):
            @get("/users/")
            def get(self, id: str = Path()) -> RequestOptions:
                ...


def test_single_body_param(client: FastClient):
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


def test_multiple_body_params(client: FastClient):
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


def test_multiple_body_params_embedded(client: FastClient):
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


def test_single_query_param(client: FastClient):
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


def test_multiple_query_params(client: FastClient):
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
