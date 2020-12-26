#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import functools
import json
import logging

import websockets

from app.request_processor import dispatcher as request_dispatcher
from app.user import WebClient

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


async def producer_handler(websocket, path):
    while True:
        message = await request_dispatcher.get_message(websocket)
        print(f"Sending {message} to {websocket}")
        await websocket.send(json.dumps(message))


async def consumer_handler(websocket, path):
    async for message in websocket:
        print("Received message:", message)
        request = json.loads(message)
        name, data = next(iter(request.items()))
        await request_dispatcher.requests[name](websocket, data)


async def handler(websocket: WebClient, path: str):
    await request_dispatcher.on_client_connected_func(websocket)
    try:
        consumer_task = asyncio.ensure_future(consumer_handler(websocket, path))
        producer_task = asyncio.ensure_future(producer_handler(websocket, path))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
    finally:
        await request_dispatcher.on_client_closed_func(websocket)


start_server = websockets.serve(handler, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
