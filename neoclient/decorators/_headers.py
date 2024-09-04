from neoclient.decorators.api import header_decorator
from ..enums import HTTPHeader

__all__ = ("accept", "referer", "user_agent")

# TODO: Type function responses

def accept(*content_types: str):
    return header_decorator(HTTPHeader.ACCEPT, ",".join(content_types))


def referer(referer: str, /):
    return header_decorator(HTTPHeader.REFERER, referer)


def user_agent(user_agent: str, /):
    return header_decorator(HTTPHeader.USER_AGENT, user_agent)
