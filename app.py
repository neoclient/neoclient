from neoclient import NeoClient, header

client = NeoClient("https://httpbin.org/", headers={"x-name": "client"})


@header("x-name", ["a", "b"])
@client.get("/headers")
def headers(): ...
