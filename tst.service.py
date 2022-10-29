from typing import Protocol

from fastclient import FastClient, get


class Httpbin(Protocol):
    @get("/get")
    def get1(self, message: str) -> dict:
        ...

    @classmethod
    @get("/get")
    def get2(cls, message: str) -> dict:
        ...

    @staticmethod
    @get("/get")
    def get3(message: str) -> dict:
        ...


httpbin: Httpbin = FastClient("https://httpbin.org/").create(Httpbin)  # type: ignore
