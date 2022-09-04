from fastclient import (
    FastClient,
    Header,
    Body,
    Query,
    Path,
    Cookie,
    Headers,
    Cookies,
    QueryParams,
    Depends,
)
from fastclient.dependencies import HeaderResponse
from fastclient import dependencies

client = FastClient("http://127.0.0.1:8000/")


def origin(body: dict = Body()) -> str:
    return body["origin"]


def powered_by(x_powered_by: str = Header()) -> str:
    return x_powered_by


def message(message: str = Query()) -> str:
    return message


def path_value(value: str = Path()) -> str:
    return value


def consent(consent: str = Cookie()) -> str:
    return consent


def all_headers(headers: dict = Headers()) -> dict:
    return headers


def all_cookies(cookies: dict = Cookies()) -> dict:
    return cookies


def all_queries(queries: dict = QueryParams()) -> dict:
    return queries


def powered_by_2(headers: dict = Depends(all_headers)) -> str:
    return headers["x-powered-by"]


@client.get("/ip", response=origin)
def get_ip() -> str:
    ...


@client.get("/header", response=HeaderResponse("x-powered-by"))
def get_header() -> str:
    ...


@client.get("/header", response=powered_by_2)
def get_header_2() -> str:
    ...


@client.get("/query", response=message)
def get_query(message: str) -> str:
    ...


@client.get("/path/{value}", response=path_value)
def get_path(value: str) -> str:
    ...


@client.get("/cookie", response=consent)
def get_cookie() -> str:
    ...


@client.get("/headers", response=all_headers)
def get_headers() -> dict:
    ...


@client.get("/cookies", response=all_cookies)
def get_cookies() -> dict:
    ...


@client.get("/queries", response=all_queries)
def get_queries(foo: str, bar: str) -> dict:
    ...


@client.get("/ip", response=dependencies.status_code)
def get_status_code() -> int:
    ...

@client.get("/ip", response=dependencies.status_phrase)
def get_status_phrase() -> str:
    ...

@client.get("/ip", response=dependencies.status_name)
def get_status_name() -> str:
    ...

@client.get("/ip", response=dependencies.status_description)
def get_status_description() -> str:
    ...

@client.get("/ip", response=dependencies.text)
def get_text() -> str:
    ...

@client.get("/ip", response=dependencies.content)
def get_content() -> bytes:
    ...

@client.get("/ip", response=dependencies.is_success)
def get_success() -> bytes:
    ...

ip: str = get_ip()
header: str = get_header()
header_2: str = get_header_2()
query: str = get_query("Hello, World")
path: str = get_path("foo")
cookie: str = get_cookie()
headers: dict = get_headers()
cookies: dict = get_cookies()
queries: dict = get_queries("foo", "bar")
status_code: int = get_status_code()
status_phrase: str = get_status_phrase()
status_name: str = get_status_name()
status_description: str = get_status_description()
text: str = get_text()
content: bytes = get_content()
success: bool = get_success()