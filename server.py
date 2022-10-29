from dataclasses import dataclass
from typing import Dict
from fastapi import FastAPI, Body


@dataclass
class Person:
    name: str


app: FastAPI = FastAPI()


@app.post("/greet")
def greet(people: Dict[str, Person] = Body()) -> str:
    print(people)

    return "Hello, " + " and ".join(repr(person) for _, person in people.items())
