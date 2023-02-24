from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Mapping, Optional, Union

from httpx import Request, Response
from pydantic import BaseModel

from neoclient import Depends, Query
from neoclient.enums import HttpMethod
from neoclient.params import QueryParameter
from neoclient.resolution import resolve


def test_resolve_infer_query() -> None:
    def func(name: str, age: int, is_cool: bool) -> Mapping[str, Union[str, int, bool]]:
        return {
            "name": name,
            "age": age,
            "is_cool": is_cool,
        }

    response: Response = Response(
        HTTPStatus.OK,
        request=Request(
            HttpMethod.GET,
            "https://foo.com/",
            params={
                "name": "sam",
                "age": "43",
                "is_cool": "true",
            },
        ),
    )

    resolved: Any = resolve(func, response)

    assert resolved == {"name": "sam", "age": 43, "is_cool": True}


def test_resolve_infer_body() -> None:
    class SomePydanticModel(BaseModel):
        name: str
        age: int

    @dataclass
    class SomeDataclass:
        name: str
        age: int

    def func(
        body_dict: dict, body_pydantic: SomePydanticModel, body_dataclass: SomeDataclass
    ) -> Mapping[str, Union[dict, SomePydanticModel, SomeDataclass]]:
        return {
            "body_dict": body_dict,
            "body_pydantic": body_pydantic,
            "body_dataclass": body_dataclass,
        }

    response: Response = Response(
        HTTPStatus.OK,
        request=Request(HttpMethod.GET, "https://foo.com/"),
        json={
            "name": "sam",
            "age": 43,
        },
    )

    resolved: Any = resolve(func, response)

    assert resolved == {
        "body_dict": {
            "name": "sam",
            "age": 43,
        },
        "body_pydantic": SomePydanticModel(
            name="sam",
            age=43,
        ),
        "body_dataclass": SomeDataclass(
            name="sam",
            age=43,
        ),
    }


def test_resolve_caching() -> None:
    class Counter:
        count: int = 0

    counter: Counter = Counter()

    class SpyingQuery(QueryParameter):
        resolution_counter: Counter = counter

        def resolve(self, response: Response, /) -> Optional[str]:
            self.resolution_counter.count += 1

            return super().resolve(response)

    query_name_spy: SpyingQuery = SpyingQuery("name")
    p_query_name_spy: str = query_name_spy  # type: ignore

    def dependency(
        name_1: str = p_query_name_spy, name_2: str = p_query_name_spy
    ) -> Mapping[str, Any]:
        return {
            "name_1": name_1,
            "name_2": name_2,
        }

    def func(
        name_1: str = p_query_name_spy,
        name_2: str = p_query_name_spy,
        dependency: Mapping[str, Any] = Depends(dependency),
    ) -> Mapping[str, Any]:
        return {
            "name_1": name_1,
            "name_2": name_2,
            "dependency": dependency,
        }

    response: Response = Response(
        HTTPStatus.OK,
        request=Request(
            HttpMethod.GET,
            "https://foo.com/",
            params={
                "name": "sam",
            },
        ),
    )

    assert resolve(func, response) == {
        "name_1": "sam",
        "name_2": "sam",
        "dependency": {
            "name_1": "sam",
            "name_2": "sam",
        },
    }
    assert query_name_spy.resolution_counter.count == 1


def test_resolve_default() -> None:
    def func(foo: str = Query("foo", default="default")) -> str:
        return foo

    response: Response = Response(
        HTTPStatus.OK,
        request=Request(HttpMethod.GET, "https://foo.com/"),
    )

    resolved: Any = resolve(func, response)

    assert resolved == "default"
