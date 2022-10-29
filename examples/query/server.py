from fastapi import FastAPI

app: FastAPI = FastAPI()


@app.get("/greet")
def greet(name: str) -> str:
    return f"Hello, {name}"
