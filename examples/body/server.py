from fastapi import FastAPI

from models import Person

app: FastAPI = FastAPI()


@app.post("/greet")
def greet(person: Person) -> str:
    return f"Hello, {person.name}"
