from retrofit.models import Query
from retrofit.enums import FieldType
from sentinel import Missing


def test_field_no_default() -> None:
    param: Query[int] = Query("foo")

    assert param.type == FieldType.QUERY
    assert param.name == "foo"
    assert param.default == Missing
    assert not param.has_default()


def test_field_default_static() -> None:
    param: Query[int] = Query("foo", default=123)

    assert param.type == FieldType.QUERY
    assert param.name == "foo"
    assert param.default == 123
    assert param.has_default()


def test_field_default_factory() -> None:
    param: Query[int] = Query("foo", default_factory=lambda: 123)

    assert param.type == FieldType.QUERY
    assert param.name == "foo"
    assert param.default == 123
    assert param.has_default()
