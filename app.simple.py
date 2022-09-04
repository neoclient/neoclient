from fastclient import get, FastClient

@get("https://httpbin.org/anything")
def anything():
    ...

anything2 = FastClient(headers={"foo": "bar"}).bind(anything)

print(anything())
print(anything2())