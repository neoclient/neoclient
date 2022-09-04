from fastclient import FastClient, Headers, Depends, Header


class Foo:
    headers: dict

    def __init__(self, headers: dict = Headers()) -> None:
        self.headers = headers

    def __call__(self) -> dict:
        return self.headers


class Bar:
    def __call__(self, x_powered_by: str = Header()) -> str:
        return x_powered_by


app = FastClient("http://127.0.0.1:8000/")


def foo(inst: Foo = Depends(Foo)) -> Foo:
    return inst


def bar(powered_by: str = Depends(Bar())) -> str:
    return powered_by


@app.get("/headers", response=foo)
def get_foo() -> Foo:
    ...


@app.get("/header", response=bar)
def get_bar() -> str:
    ...


f: Foo = get_foo()
b: str = get_bar()
