from http import cookies
from typing import Any
from fastapi import FastAPI, Response, Request

app = FastAPI()


@app.get("/ip")
def get_ip() -> dict:
    return {"origin": "1.2.3.4"}


@app.get("/header")
def get_header() -> Response:
    return Response(headers={"X-Powered-By": "Muffins!"})


@app.get("/query")
def get_query(message: str) -> dict:
    return {"message": message}


@app.get("/path/{value}")
def get_path(value: str) -> dict:
    return {"value": value}


@app.get("/cookie")
def get_cookie() -> Response:
    return Response(headers={"set-cookie": "CONSENT=yes"})


@app.get("/headers")
def get_headers() -> Response:
    return Response(headers={"X-Powered-By": "Muffins!"})


@app.get("/cookies")
def get_cookies() -> Response:
    return Response(headers={"set-cookie": "CONSENT=yes"})


@app.get("/queries")
def get_queries(request: Request) -> dict:
    return {"queries": request.query_params}
