import pydantic.fields

from neoclient import sentinels


def test_Required() -> None:
    assert sentinels.Required is pydantic.fields.Required


def test_Undefined() -> None:
    assert sentinels.Undefined is pydantic.fields.Undefined
