import asyncio
import pytest

from unittest.mock import MagicMock

from app.request_processor import dispatcher
from app.user import User


# @pytest.mark.asyncio
# async def test_dispatcher_connect_user():
#     users.clear()
#
#     client = MagicMock()
#     await dispatcher.on_client_connected_func(client)
#     assert client in users
#
#
# @pytest.mark.asyncio
# async def test_dispatcher_disconnect_user():
#     users.clear()
#
#     client = MagicMock()
#     users[client] = User(client)
#
#     assert len(users) == 1
#     assert client in users
#
#     await dispatcher.on_client_closed_func(client)
#
#     assert len(users) == 0