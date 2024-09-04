from httpx import get


def ip() -> str:
    return get("https://httpbin.org/ip").json()["origin"]


from neoclient import get


@get("https://httpbin.org/ip")
def ip():
    ...
