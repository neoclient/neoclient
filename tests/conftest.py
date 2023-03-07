from pytest import fixture

from neoclient.models import Response

from . import utils


@fixture
def response() -> Response:
    return utils.build_response()
