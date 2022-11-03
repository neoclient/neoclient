# examples/body
Example for a single body parameter

## Start the Server
```console
$ uvicorn example.server:app
INFO:     Started server process [229339]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## Use the Client
```python
from example.client import greet
from example.models import Person

person: Person = Person(name="sam")

greeting: str = greet(person)
```
```python
>>> greeting
'Hello, sam!'
```