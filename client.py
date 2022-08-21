from fastclient import FastClient, get, Body
from typing import Protocol
from pprint import pprint as pp
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


class Httpbin(Protocol):
    @get("/str")
    def get_str(self, value: str = Body(), /) -> str:
        ...

    @get("/int")
    def get_int(self, value: int = Body(), /) -> int:
        ...

    @get("/bool")
    def get_bool(self, value: bool = Body(), /) -> bool:
        ...

    @get("/float")
    def get_float(self, value: float = Body(), /) -> float:
        ...

    @get("/list")
    def get_list(self, value: list = Body(), /) -> list:
        ...

    @get("/none")
    def get_none(self, value: None = Body(required=True), /) -> None:
        ...

    @get("/tuple")
    def get_tuple(self, value: tuple = Body(), /) -> tuple:
        ...

    @get("/set")
    def get_set(self, value: set = Body(), /) -> set:
        ...

    @get("/dict")
    def get_dict(self, value: dict = Body(), /) -> dict:
        ...

    @get("/bytes")
    def get_bytes(self, value: bytes = Body(), /) -> bytes:
        ...

    @get("/dataclass")
    def get_dataclass(self, value: User = Body(), /) -> User:
        ...

    @get("/model")
    def get_model(self, value: Item = Body(), /) -> Item:
        ...

    @get("/enum")
    def get_enum(self, value: Animal = Body(), /) -> Animal:
        ...


httpbin: Httpbin = FastClient("http://localhost:8000/").create(Httpbin)  # type: ignore

r_str = httpbin.get_str("abc")
r_int = httpbin.get_int(123)
r_bool = httpbin.get_bool(True)
r_float = httpbin.get_float(1.23)
r_list = httpbin.get_list([123, "abc", True, 1.23])
r_none = httpbin.get_none(None)
r_tuple = httpbin.get_tuple((123, "abc", True))
r_set = httpbin.get_set({123, "abc", True})
r_dict = httpbin.get_dict({"abc": 123, True: 1.23})
r_bytes = httpbin.get_bytes(b"abc")
r_dataclass = httpbin.get_dataclass(User(123, "abc"))
r_model = httpbin.get_model(Item(id=123, name="abc"))
r_enum = httpbin.get_enum(Animal.DOG)
