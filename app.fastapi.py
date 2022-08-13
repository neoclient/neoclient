from fastapi import FastAPI, Path

app = FastAPI()

@app.get("/{item}")
def get_root(*, item: str = Path("foo", title="Some Item")):
    return {"item": item}