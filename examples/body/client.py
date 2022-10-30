from models import Person

from fastclient import FastClient

client: FastClient = FastClient(base_url="http://127.0.0.1:8000/")


@client.post("/greet")
def greet(person: Person) -> str:
    ...
