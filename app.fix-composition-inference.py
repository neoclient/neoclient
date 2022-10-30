from dataclasses import dataclass
from fastclient import FastClient, Path


@dataclass
class Person:
    name: str


client: FastClient = FastClient(base_url="http://127.0.0.1:8000/")


@client.get("/greet/{name}")
def greet(a: str = Path(alias="name"), b: str = Path(alias="name")) -> str:
    ...


print(greet("sam", "bob"))
