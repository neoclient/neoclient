from fastapi import FastAPI

app = FastAPI()

@app.get("/ip")
def root() -> dict:
    return {"origin": "1.2.3.4"}