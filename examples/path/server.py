from fastapi import FastAPI, Path

app: FastAPI = FastAPI()


@app.get("/greet/{name}")
def greet(name: str = Path()) -> str:
    return f"Hello, {name}"
