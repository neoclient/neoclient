from neoclient import Cookie, NeoClient

client: NeoClient = NeoClient("http://127.0.0.1:8000/")


@client.get("/greet")
def greet(name: str = Cookie()) -> str:
    ...
