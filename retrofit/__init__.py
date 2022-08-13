from dataclasses import dataclass
from typing import Any, Callable, List, Tuple, TypeVar, Type
import annotate
from .enums import HttpMethod
from .sentinels import Specification
from .models import RequestSpecification
from types import MethodType
import urllib.parse
import inspect
import httpx

T = TypeVar("T")

client = httpx.Client()


@dataclass
class Retrofit:
    base_url: str

    def create(self, protocol: Type[T], /) -> T:
        members: List[Tuple[str, Any]] = inspect.getmembers(protocol)

        attributes: dict = {}

        member_name: str
        member: Any
        for member_name, member in members:
            annotations: dict = annotate.get_annotations(member)

            if Specification not in annotations:
                continue

            spec: RequestSpecification = annotations[Specification]

            attributes[member_name] = self._method(spec)

        return type(protocol.__name__, (object,), attributes)()

    def _url(self, endpoint: str, /) -> str:
        return urllib.parse.urljoin(self.base_url, endpoint)

    def _method(self, specification: RequestSpecification, /) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return client.request(specification.method, self._url(specification.endpoint)).json()

        return wrapper


def method(verb: HttpMethod, /):
    def proxy(endpoint: str, /):
        def decorate(method: MethodType, /):
            annotate.annotate(
                method,
                annotate.Annotation(
                    Specification, RequestSpecification(method=verb.value, endpoint=endpoint)
                ),
            )

            return method

        return decorate

    return proxy


get = method(HttpMethod.GET)
