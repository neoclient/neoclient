from fastclient import FastClient

client = FastClient("https://httpbin.org/")


@client.middleware
def log_request(call_next, request):
    print("Sending request:", request)

    return call_next(request)


@client.get("/ip")
def get_ip():
    ...


ip = get_ip()
