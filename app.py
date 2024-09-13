from neoclient import NeoClient, header, param, params
from neoclient.decorators import set_header, add_header, add_param, set_param, cookie, headers, cookies

client = NeoClient(
    "https://httpbin.org/",
    headers={"name": "client"},
)

# @cookie("food", "chips", domain="b.com")
# @cookie("food", "pizza", domain="a.com")
# @param("action", "sleep")
# @param("action", "eat")
# @header("name", "b")
# @header("name", "a")
# @headers({"name": "bob"})
# @headers({"name": "sam"})
@cookies({"name": "bob"})
@cookies({"name": "sam"})
@client.get("/get")
def get(): ...
