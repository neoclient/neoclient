from neoclient.param_functions import AllRequestState, AllResponseState, AllState
from neoclient.params import (
    AllRequestStateParameter,
    AllResponseStateParameter,
    AllStateParameter,
)


def test_AllRequestState() -> None:
    assert AllRequestState() == AllRequestStateParameter()


def test_AllResponseState() -> None:
    assert AllResponseState() == AllResponseStateParameter()


def test_AllState() -> None:
    assert AllState() == AllStateParameter()
