class RequestDispatcher:
    def __init__(self):
        self.requests = {}
        self.on_client_connected_func = None
        self.on_client_closed_func = None

    def request(self, name: str):
        def func(request_func):
            self.requests[name] = request_func
            return request_func
        return func

    def on_client_connected(self, func):
        self.on_client_connected_func = func
        return func

    def on_client_closed(self, func):
        self.on_client_closed_func = func
        return func
