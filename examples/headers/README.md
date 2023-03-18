# examples/headers
Example for the `Headers` parameter

## Start the Server
```console
$ uvicorn example.server:app
INFO:     Started server process [229339]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## Run the Example
```console
$ python3 app.py
{'accept': '*/*',
 'accept-encoding': 'gzip, deflate, br',
 'age': '43',
 'connection': 'keep-alive',
 'host': '127.0.0.1:8000',
 'name': 'sam',
 'user-agent': 'neoclient/0.1.24'}
```