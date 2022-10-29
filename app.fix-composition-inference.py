from dataclasses import dataclass
from fastclient import FastClient


@dataclass
class Person:
    name: str


client: FastClient = FastClient(base_url="http://127.0.0.1:8000/")


@client.post("/greet")
def greet(sam: Person, bob: Person) -> str:
    ...


print(greet(
    Person(name="sam"),
    Person(name="bob"),
))
