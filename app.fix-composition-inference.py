from dataclasses import dataclass
from fastclient import FastClient, Path, path


@dataclass
class Person:
    name: str


client: FastClient = FastClient(base_url="http://127.0.0.1:8000/")


@path("name", "sam")
@client.get("/greet/{name}")
def greet() -> str:
    ...


# print(greet("sam", "bob"))
print(greet())
