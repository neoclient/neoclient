from dataclasses import dataclass

from neoclient import NeoClient


@dataclass
class Person:
    name: str


client: NeoClient = NeoClient("http://127.0.0.1:8000/")


@client.post("/greet")
def greet(person: Person) -> str: ...
