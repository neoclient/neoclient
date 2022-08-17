from retrofit import utils
import pytest


def test_get_path_params() -> None:
    assert utils.get_path_params("http://foo.com/") == set()
    assert utils.get_path_params("http://foo.com/{bar}") == {"bar"}
    assert utils.get_path_params("http://foo.com/{bar}/{bar}") == {"bar"}
    assert utils.get_path_params("http://foo.com/{bar}/{baz}") == {"bar", "baz"}

    with pytest.raises(ValueError):
        utils.get_path_params("http://foo.com/{}")

    with pytest.raises(ValueError):
        utils.get_path_params("http://foo.com/{0}")

    with pytest.raises(ValueError):
        utils.get_path_params("http://foo.com/{bar }")
