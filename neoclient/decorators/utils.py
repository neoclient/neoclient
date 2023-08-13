from typing import Any, Callable, Sequence, Type, TypeVar

from neoclient.services import Service

from ..param_functions import Request
from .common import request_depends

__all__: Sequence[str] = ("persist_pre_request",)

CS = TypeVar("CS", Callable[..., Any], Type[Service])


def _persist_pre_request_dependency(request=Request()):
    # TOOO: `request` is currently un-typed due to bug #136
    request.state.pre_request = request


def persist_pre_request(target: CS, /) -> CS:
    return request_depends(_persist_pre_request_dependency)(target)
