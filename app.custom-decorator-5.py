referer = Decorator()


@referer.operation
def _referer_operation(operation: Operation, /): ...


@referer.client
def _referer_client(client: ClientOptions, /): ...
