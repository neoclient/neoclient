from dataclasses import dataclass

from fastapi import FastAPI


@dataclass
class Person:
    name: str


app: FastAPI = FastAPI()


@app.post("/greet")
def greet(person: Person) -> str:
    return f"Hello, {person.name}!"
