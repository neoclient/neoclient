from neoclient.decorators.api3 import Decorator
from neoclient import get
from neoclient.operation import Operation


class MyDecorator(Decorator):
    def decorate_operation(self, operation: Operation, /) -> None:
        operation.pre_request.headers["x-message"] = "Hello, World!"


my_decorator: Decorator = MyDecorator()


@my_decorator
@get("https://httpbin.org/headers")
def headers(): ...
