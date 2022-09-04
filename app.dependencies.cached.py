from fastclient import FastClient, Depends

app = FastClient("http://127.0.0.1:8000/")

def some_dependency() -> str:
    print("some_dependency called")

    return "foo"

def response(a: str = Depends(some_dependency), b: str = Depends(some_dependency)) -> str:
    return a + b

@app.get("/ip", response=response)
def get_ip() -> str:
    ...

ip = get_ip()