import pytest

from neoclient import Request, Response
from neoclient.middlewares import ExpectedContentTypeMiddleware

from mediate.protocols import MiddlewareCallable

from neoclient.enums import HTTPHeader

from neoclient.errors import ExpectedContentTypeError

from . import utils


def test_ExpectedContentTypeMiddleware_no_suffix_no_parameters() -> None:
    def invoke_middleware(
        middleware: MiddlewareCallable[Request, Response],
        content_type: str,
    ) -> None:
        def call_next(request: Request, /) -> Response:
            return utils.build_response(
                request=request, headers={HTTPHeader.CONTENT_TYPE: content_type}
            )

        middleware(call_next, utils.build_request())

    middleware: MiddlewareCallable[Request, Response] = ExpectedContentTypeMiddleware(
        "application/json"
    )

    invoke_middleware(middleware, "application/json")  # ok
    invoke_middleware(middleware, "application/JSON")  # ok
    invoke_middleware(middleware, 'application/json; charset="utf-8"')  # ok
    invoke_middleware(middleware, "application/json+foo")  # ok
    invoke_middleware(middleware, 'application/json+foo; charset="utf-8"')  # ok

    with pytest.raises(ExpectedContentTypeError):
        invoke_middleware(middleware, "application/not-json")  # not ok


def test_ExpectedContentTypeMiddleware_suffix_no_parameters() -> None:
    def invoke_middleware(
        middleware: MiddlewareCallable[Request, Response],
        content_type: str,
    ) -> None:
        def call_next(request: Request, /) -> Response:
            return utils.build_response(
                request=request, headers={HTTPHeader.CONTENT_TYPE: content_type}
            )

        middleware(call_next, utils.build_request())

    middleware: MiddlewareCallable[Request, Response] = ExpectedContentTypeMiddleware(
        "application/json+opensearch", suffix=True
    )

    invoke_middleware(middleware, "application/json+opensearch")  # ok
    invoke_middleware(middleware, "application/JSON+OpenSearch")  # ok
    invoke_middleware(middleware, 'application/json+opensearch; charset="utf-8"')  # ok

    with pytest.raises(ExpectedContentTypeError):
        invoke_middleware(middleware, "application/not-json")  # not ok

    with pytest.raises(ExpectedContentTypeError):
        invoke_middleware(middleware, "application/json+not-opensearch")  # not ok

    with pytest.raises(ExpectedContentTypeError):
        invoke_middleware(
            middleware, 'application/json+not-opensearch; charset="utf-8"'
        )  # not ok


def test_ExpectedContentTypeMiddleware_suffix_parameters() -> None:
    def invoke_middleware(
        middleware: MiddlewareCallable[Request, Response],
        content_type: str,
    ) -> None:
        def call_next(request: Request, /) -> Response:
            return utils.build_response(
                request=request, headers={HTTPHeader.CONTENT_TYPE: content_type}
            )

        middleware(call_next, utils.build_request())

    middleware: MiddlewareCallable[Request, Response] = ExpectedContentTypeMiddleware(
        'application/json+opensearch; charset="utf-8"', suffix=True
    )

    invoke_middleware(middleware, 'application/json+opensearch; charset="utf-8"')  # ok
    invoke_middleware(middleware, 'application/JSON+OpenSearch; CharSet="UTF-8"')  # ok

    with pytest.raises(ExpectedContentTypeError):
        invoke_middleware(middleware, "application/not-json")  # not ok

    with pytest.raises(ExpectedContentTypeError):
        invoke_middleware(middleware, "application/json+not-opensearch")  # not ok

    with pytest.raises(ExpectedContentTypeError):
        invoke_middleware(
            middleware, 'application/json+opensearch; name="bob"'
        )  # not ok

    with pytest.raises(ExpectedContentTypeError):
        invoke_middleware(
            middleware, 'application/json+opensearch; charset="utf-9"'
        )  # not ok

    with pytest.raises(ExpectedContentTypeError):
        invoke_middleware(middleware, 'application/json; charset="utf-8"')  # not ok
