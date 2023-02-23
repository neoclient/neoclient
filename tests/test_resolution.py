from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Mapping, Union

from httpx import Request, Response
from pydantic import BaseModel

from neoclient.enums import HttpMethod
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
