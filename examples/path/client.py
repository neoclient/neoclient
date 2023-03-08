from neoclient import NeoClient

client: NeoClient = NeoClient("http://127.0.0.1:8000/")


@client.get("/greet/{name}")
def greet(name: str) -> str:
    ...
