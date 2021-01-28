#!/usr/bin/env python

import asyncio
import functools
import json
import logging
from asyncio import Future

import websockets

from app.request_processor import dispatcher as request_dispatcher
from app.user import WebClient
from app.exceptions import RequestError, PromptError

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
        request = json.loads(message)
        name, data = next(iter(request.items()))

        if name not in request_dispatcher.requests:
            print(f"ERROR: No handler for {name} request")
            continue

        print("Received request: ", request)

        try:
            await request_dispatcher.requests[name](websocket, data)
        except Exception as e:
            # Can't quite figure out how catching async exceptions work, this is a hack
            # to catch RequestExceptions until I can figure out something better
            if hasattr(e, "_type"):
                print(str(e._type) + ": " + str(e))
                await request_dispatcher.add_to_message_queue(
                    websocket,
                    e.get_error_response()
                )
            else:
                raise


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


print("Starting server...")
start_server = websockets.serve(handler, "0.0.0.0", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
