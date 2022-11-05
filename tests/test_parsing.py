from typing import Union, Mapping

from fastclient.parsing import parse_obj_as
from httpx import QueryParams


def test_parse_obj_as() -> None:
    assert parse_obj_as(str, "123") == "123"
    assert parse_obj_as(str, 123) == "123"
    assert parse_obj_as(Union[str, int], "abc") == "abc"  # type: ignore
    assert parse_obj_as(Mapping[str, str], QueryParams({"name": "sam", "age": "43"})) == QueryParams({"name": "sam", "age": "43"})  # type: ignore
