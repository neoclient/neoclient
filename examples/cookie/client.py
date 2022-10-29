from fastclient import FastClient, Cookie

client: FastClient = FastClient(base_url="http://127.0.0.1:8000/")


@client.get("/greet")
def greet(name: str = Cookie()) -> str:
    ...
