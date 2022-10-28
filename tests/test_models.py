from pydantic.fields import Undefined

from fastclient.enums import ParamType
from fastclient.parameters import Query


def test_field_no_default() -> None:
    param: Query = Query(alias="foo")

    assert param.type == ParamType.QUERY
    assert param.alias == "foo"
    assert not param.has_default()
    assert param.get_default() is Undefined


def test_field_default_static() -> None:
    param: Query = Query(alias="foo", default=123)

    assert param.type == ParamType.QUERY
    assert param.alias == "foo"
    assert param.get_default() == 123
    assert param.has_default()
