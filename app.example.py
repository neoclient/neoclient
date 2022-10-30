from fastclient import FastClient

app = FastClient("https://httpbin.org/")

@app.get("/anything/{path}")
def anything(path: str):
    ...