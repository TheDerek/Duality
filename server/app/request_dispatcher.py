import asyncio
from typing import Dict
from app.user import WebClient
from collections import defaultdict


class RequestDispatcher:
    def __init__(self):
        # Queue of messages to send
        self.queues: Dict[WebClient, asyncio.Queue] = defaultdict(asyncio.Queue)
        self.requests = {}
        self.on_client_connected_func = None
        self.on_client_closed_func = None

    async def add_to_message_queue(self, message: dict, client: WebClient):
        await self.queues[client].put(message)

    def get_message(self, client: WebClient):
        return self.queues[client].get()

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
