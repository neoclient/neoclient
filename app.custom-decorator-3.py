from neoclient.decorators.api import Decorator
from neoclient import get
from neoclient.operation import Operation

"""
from neoclient.decorator import Decorator, DecoratorException

from neoclient.decorators.api import Decorator
from neoclient.decorators import referer
"""


class MyDecorator(Decorator):
    def decorate_operation(self, operation: Operation, /) -> None:
        operation.pre_request.headers["x-message"] = "Hello, World!"


my_decorator: Decorator = MyDecorator()


@my_decorator
@get("https://httpbin.org/headers")
def headers():
    ...
