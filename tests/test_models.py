from neoclient.models import State
import pytest


def test_State_init() -> None:
    assert State() == State()
    assert State({"name": "sam", "age": 43}) == State(name="sam", age=43)
    assert State(name="sam", age=43) == State(name="sam", age=43)
    assert State({"name": "bob", "age": 43}, name="sam") == State(name="sam", age=43)


def test_State_set_attr() -> None:
    state: State = State()

    state.name = "sam"
    state.age = 43

    assert state == State(name="sam", age=43)


def test_State_set_item() -> None:
    state: State = State()

    state["name"] = "sam"
    state["age"] = 43

    assert state == State(name="sam", age=43)


def test_State_get_attr() -> None:
    state: State = State(name="sam", age=43)

    assert state.name == "sam"
    assert state.age == 43

    with pytest.raises(AttributeError):
        state.missing


def test_State_get_item() -> None:
    state: State = State(name="sam", age=43)

    assert state["name"] == "sam"
    assert state["age"] == 43

    with pytest.raises(KeyError):
        state["missing"]


def test_State_del_attr() -> None:
    state: State = State(name="sam", age=43)

    del state.name

    assert state == State(age=43)

    with pytest.raises(AttributeError):
        del state.missing

def test_State_del_item() -> None:
    state: State = State(name="sam", age=43)

    del state["name"]

    assert state == State(age=43)

    with pytest.raises(KeyError):
        del state["missing"]