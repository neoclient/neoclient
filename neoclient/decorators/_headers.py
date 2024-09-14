from ._common import header
from ..enums import HTTPHeader

__all__ = ("accept", "host", "referer", "user_agent")

# TODO: Type responses


def accept(*content_types: str):
    return header(HTTPHeader.ACCEPT, ",".join(content_types))


def host(host: str, /):
    return header(HTTPHeader.HOST, host)


def referer(referer: str, /):
    return header(HTTPHeader.REFERER, referer)


def user_agent(user_agent: str, /):
    return header(HTTPHeader.USER_AGENT, user_agent)
