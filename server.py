from fastapi import FastAPI, Body
from dataclasses import dataclass
from pydantic import BaseModel
from enum import Enum, auto

@dataclass
class User:
    id: int
    name: str

class Item(BaseModel):
    id: int
    name: str

class Animal(Enum):
    CAT = auto()
    DOG = auto()

app = FastAPI()

@app.get("/str")
def get_str(value: str = Body(...)) -> str:
    return value

@app.get("/int")
def get_int(value: int = Body(...)) -> int:
    return value

@app.get("/bool")
def get_bool(value: bool = Body(...)) -> bool:
    return value

@app.get("/float")
def get_float(value: float = Body(...)) -> float:
    return value

@app.get("/list")
def get_list(value: list = Body(...)) -> list:
    return value

@app.get("/none")
def get_none(value: None = Body(...)) -> None:
    return value

@app.get("/tuple")
def get_tuple(value: tuple = Body(...)) -> tuple:
    return value

@app.get("/set")
def get_set(value: set = Body(...)) -> set:
    return value

@app.get("/dict")
def get_dict(value: dict = Body(...)) -> dict:
    return value

@app.get("/bytes")
def get_bytes(value: bytes = Body(...)) -> bytes:
    return value

@app.get("/dataclass")
def get_dataclass(value: User = Body(...)) -> User:
    return value

@app.get("/model")
def get_model(value: Item = Body(...)) -> Item:
    return value

@app.get("/enum")
def get_enum(value: Animal = Body(...)) -> Animal:
    return value