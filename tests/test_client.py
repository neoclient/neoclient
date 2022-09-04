from typing import Optional, Protocol

import pytest
from fastclient import Path, Query, Body, FastClient, get, post
from fastclient.models import RequestOptions
from pydantic import BaseModel


class Model(BaseModel):
    id: int
    name: str


class User(Model):
    pass


class Item(Model):
    pass


@pytest.fixture
def client() -> FastClient:
    return FastClient(base_url="http://localhost:8080/")


def test_query_not_required_omitted(client: FastClient):
    class Service(Protocol):
        @get("get")
        def get(
            self, q: Optional[str] = Query(default=None, required=False)
        ) -> RequestOptions:
            ...

    service: Service = client.create(Service)  # type: ignore

    assert service.get() == RequestOptions(
        method="GET",
        url="get",
    )


def test_query_required_not_omitted(client: FastClient):
    class Service(Protocol):
        @get("get")
        def get(
            self, q: Optional[str] = Query(default=None, required=True)
        ) -> RequestOptions:
            ...

    service: Service = client.create(Service)  # type: ignore

    assert service.get() == RequestOptions(
        method="GET",
        url="get",
        params={"q": None},
        headers={},
        json=None,
        cookies={},
    )


def test_error_if_missing_path_param(client: FastClient):
    with pytest.raises(ValueError):

        class Service(Protocol):
            @get("/users/{id}")
            def get(self) -> RequestOptions:
                ...


def test_error_if_extra_path_param(client: FastClient):
    with pytest.raises(ValueError):

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
        params={},
        headers={},
        json={"id": 1, "name": "item"},
        cookies={},
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
        params={},
        headers={},
        json={
            "user": {"id": 1, "name": "user"},
            "item": {"id": 1, "name": "item"},
        },
        cookies={},
    )
