from .common import header
from ..enums import HTTPHeader

__all__ = ("accept", "referer", "user_agent")

# TODO: Type responses


def accept(*content_types: str):
    return header(HTTPHeader.ACCEPT, ",".join(content_types))


def referer(referer: str, /):
    return header(HTTPHeader.REFERER, referer)


def user_agent(user_agent: str, /):
    return header(HTTPHeader.USER_AGENT, user_agent)
