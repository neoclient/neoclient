from typing import TypeVar
from ..models import RequestOpts, Response
from di.api.providers import DependencyProviderType

T = TypeVar("T")


def inject_response(dependency: DependencyProviderType[T], response: Response) -> T:
    raise NotImplementedError


def inject_request(dependency: DependencyProviderType[T], request: RequestOpts) -> T:
    raise NotImplementedError


"""
# inject, solve, execute, resolve, handle
from neoclient.di import inject_request
from neoclient import Request

my_request = Request("GET", "/")

def my_referer_dependency(request: Request) -> str:
  return request.headers["referer"]

referer = inject_request(my_referer_dependency, my_request)
"""
