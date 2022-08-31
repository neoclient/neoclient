from typing import Optional, Protocol

import pytest
from fastclient import Path, Query, Body, FastClient, get, post
from fastclient.models import Request
from pydantic import BaseModel


class Model(BaseModel):
    id: int
    name: str


class User(Model):
    pass


class Item(Model):
    pass


@pytest.fixture
def fast_client() -> FastClient:
    return FastClient(base_url="http://localhost:8080/")


def test_query_not_required_omitted(fast_client: FastClient):
    class Service(Protocol):
        @get("get")
        def get(
            self, q: Optional[str] = Query(default=None, required=False)
        ) -> Request:
            ...

    service: Service = fast_client.create(Service)  # type: ignore

    assert service.get() == Request(
        method="GET",
        url="get",
        params={},
        headers={},
        json=None,
        cookies={},
    )


def test_query_required_not_omitted(fast_client: FastClient):
    class Service(Protocol):
        @get("get")
        def get(self, q: Optional[str] = Query(default=None, required=True)) -> Request:
            ...

    service: Service = fast_client.create(Service)  # type: ignore

    assert service.get() == Request(
        method="GET",
        url="get",
        params={"q": None},
        headers={},
        json=None,
        cookies={},
    )


def test_error_if_missing_path_param(fast_client: FastClient):
    with pytest.raises(ValueError):

        class Service(Protocol):
            @get("/users/{id}")
            def get(self) -> Request:
                ...


def test_error_if_extra_path_param(fast_client: FastClient):
    with pytest.raises(ValueError):

        class Service(Protocol):
            @get("/users/")
            def get(self, id: str = Path()) -> Request:
                ...


def test_single_body_param(fast_client: FastClient):
    class Service(Protocol):
        @post("/items/")
        def create_item(self, item: Item = Body()) -> Request:
            ...

    service: Service = fast_client.create(Service)  # type: ignore

    assert service.create_item(Item(id=1, name="item")) == Request(
        method="POST",
        url="/items/",
        params={},
        headers={},
        json={"id": 1, "name": "item"},
        cookies={},
    )


def test_multiple_body_params(fast_client: FastClient):
    class Service(Protocol):
        @post("/items/")
        def create_item(self, user: User = Body(), item: Item = Body()) -> Request:
            ...

    service: Service = fast_client.create(Service)  # type: ignore

    assert service.create_item(
        User(id=1, name="user"), Item(id=1, name="item")
    ) == Request(
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
