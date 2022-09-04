from fastclient import FastClient

app = FastClient("https://httpbin.org/")


@app.get("/get")
def get(message: str):
    ...