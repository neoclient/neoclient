from fastapi import Cookie, FastAPI

app: FastAPI = FastAPI()


@app.get("/greet")
def greet(name: str = Cookie()) -> str:
    return f"Hello, {name}"
