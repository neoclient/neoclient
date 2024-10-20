from httpx import URL

from neoclient.decorators.api import client_decorator
from neoclient.specification import ClientSpecification

__all__ = ("base_url",)

# TODO: Type responses


def base_url(base_url: str, /):
    @client_decorator
    def decorate(client: ClientSpecification, /) -> None:
        client.options.base_url = URL(base_url)

    return decorate
