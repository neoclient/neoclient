from neoclient import NeoClient, header, param, params

client = NeoClient(
    "https://httpbin.org/",
    headers={"x-name": "client"},
    params={"sort": "desc"},
)


@param("sort", "asc", overwrite=False)
@params({"sort": "bob"})
@header("x-name", "request")
@client.get("/get")
def get(): ...
