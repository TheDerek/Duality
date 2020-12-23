#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import functools
import json
import logging

import websockets
from app.request_processor import dispatcher as request_dispatcher


class Game:
    def __init__(self):
        pass


logging.basicConfig()


def log_call(fn):
    @functools.wraps(fn)
    def logged(*args, **kwargs):
        print(f"{fn.__name__}{args}")
        return fn(*args, **kwargs)

    return logged


async def counter(websocket, path):
    request_dispatcher.on_client_connected_func(websocket)
    try:
        async for message in websocket:
            print("Received message:", message)
            request = json.loads(message)
            name, data = next(iter(request.items()))
            request_dispatcher.requests[name](websocket, data)

    finally:
        request_dispatcher.on_client_closed_func(websocket)


start_server = websockets.serve(counter, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()