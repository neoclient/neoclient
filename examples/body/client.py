from dataclasses import dataclass

from neoclient import FastClient


@dataclass
class Person:
    name: str


client: FastClient = FastClient(base_url="http://127.0.0.1:8000/")


@client.post("/greet")
def greet(person: Person) -> str:
    ...
