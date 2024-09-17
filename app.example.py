from neoclient import get


@get("https://httpbin.org/ip")
def ip():
    ...
