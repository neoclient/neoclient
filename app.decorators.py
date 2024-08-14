# from neoclient import get
# from neoclient.decorators import accept


# @accept("application/json")
# @get("https://httpbin.org/ip")
# def ip(): ...

from httpx import get


def ip():
    return get("https://httpbin.org/ip", headers={"accept": "application/json"})
