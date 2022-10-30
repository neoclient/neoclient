from typing import Mapping

from fastapi import FastAPI, Request

app: FastAPI = FastAPI()


@app.get("/echo")
def echo(request: Request) -> Mapping[str, str]:
    return request.headers
