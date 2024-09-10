from neoclient import NeoClient, header, query

client = NeoClient(
    "https://httpbin.org/",
    headers={"x-name": "client"},
    params={"sort": "desc"},
)


@query("sort", "asc")
# @query("op", ["a", "b"])
@header("x-name", ["a", "b"])
@client.get("/get")
def get(): ...
