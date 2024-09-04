# from httpx import Headers
# from neoclient.decorators import HeaderDecorator


# def referer(referer: str, /):
#     return HeaderDecorator("referer", referer)


# --------------

# from neoclient.decorators.api import header_decorator

# def referer(referer: str, /):
#     return header_decorator("referer", referer)

# def referer2(referer: str, /):
#     def decorate(headers: Headers, /):
#         headers["referer"] = referer

#     return headers_decorator(decorate)

# --------------

from neoclient.decorators.api import header_decorator, headers_decorator, operation_decorator
from neoclient import get
from httpx import Headers

from neoclient.operation import Operation

# google_referer = HeadersDecorator2(
#     lambda headers: headers.update({"referer": "https://www.google.com/"})
# )

@operation_decorator
def log_operation(operation: Operation, /) -> None:
    print("Operation:", operation)

@headers_decorator
def google_referer(headers: Headers, /) -> None:
    headers["referer"] = "https://www.google.com/"

@header_decorator("name", "sam")
@log_operation
@google_referer
@get("https://httpbin.org/headers")
def headers(): ...
