from httpx import Headers, URL
from neoclient.di import inject_request, inject_response
from neoclient.models import RequestOpts, Response

request = RequestOpts("GET", "/", headers={"origin": "Request!"})
response = Response(200, headers={"origin": "Response!"}, request=request)


# def my_dependency(headers: Headers, /):
#     return headers["origin"]

def my_dependency(url: URL, /):
  return url


d1 = inject_request(my_dependency, request)
d2 = inject_response(my_dependency, response)
