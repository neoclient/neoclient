from ..param_functions import Request
from ._common import request_depends
from .api import CS

__all__ = ("persist_pre_request",)


def _persist_pre_request_dependency(request=Request()):
    # TOOO: `request` is currently un-typed due to bug #136
    request.state.pre_request = request


def persist_pre_request(target: CS, /) -> CS:
    return request_depends(_persist_pre_request_dependency)(target)
