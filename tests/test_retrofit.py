from retrofit import Retrofit, Query, get
from retrofit.models import Request
from retrofit.converters import IdentityConverter, IdentityResolver
from typing import Protocol, Optional
import pytest


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
