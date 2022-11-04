from fastclient import FastClient

from .models import Person

client: FastClient = FastClient(base_url="http://127.0.0.1:8000/")


@client.post("/greet")
def greet(person: Person) -> str:
    ...
