from fastapi import FastAPI, Header

app: FastAPI = FastAPI()


@app.get("/greet")
def greet(name: str = Header()) -> str:
    return f"Hello, {name}"
