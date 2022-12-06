from neoclient import NeoClient, Header

client: NeoClient = NeoClient(base_url="http://127.0.0.1:8000/")


@client.get("/greet")
def greet(name: str = Header()) -> str:
    ...
