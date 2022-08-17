from typing import Optional, Protocol

import pytest
from retrofit import Path, Query, Retrofit, get
from retrofit.converters import IdentityConverter, IdentityResolver
from retrofit.models import Request


@pytest.fixture
def retrofit() -> Retrofit:
    return Retrofit(
        base_url="http://localhost:8080/",
        resolver=IdentityResolver(),
        converter=IdentityConverter(),
    )


def test_query_not_required_omitted(retrofit: Retrofit):
    class Service(Protocol):
        @get("get")
        def get(
            self, q: Optional[str] = Query(default=None, required=False)
        ) -> Request:
            ...

    service: Service = retrofit.create(Service)  # type: ignore

    assert service.get() == Request(
        method="GET",
        url="http://localhost:8080/get",
        params={},
        headers={},
        body={},
        cookies={},
    )


def test_query_required_not_omitted(retrofit: Retrofit):
    class Service(Protocol):
        @get("get")
        def get(self, q: Optional[str] = Query(default=None, required=True)) -> Request:
            ...

    service: Service = retrofit.create(Service)  # type: ignore

    assert service.get() == Request(
        method="GET",
        url="http://localhost:8080/get",
        params={"q": None},
        headers={},
        body={},
        cookies={},
    )


def test_error_if_missing_path_param(retrofit: Retrofit):
    with pytest.raises(ValueError):

        class Service(Protocol):
            @get("/users/{id}")
            def get(self) -> Request:
                ...


def test_error_if_extra_path_param(retrofit: Retrofit):
    with pytest.raises(ValueError):

        class Service(Protocol):
            @get("/users/")
            def get(self, id: str = Path()) -> Request:
                ...
