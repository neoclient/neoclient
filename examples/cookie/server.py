from fastapi import FastAPI, Cookie

app: FastAPI = FastAPI()


@app.get("/greet")
def greet(name: str = Cookie()) -> str:
    return f"Hello, {name}"
