import random
import string
import asyncio

from typing import Dict
from websockets.server import WebSocketServerProtocol
from app.game import Game
from app.user import User
from app.request_dispatcher import RequestDispatcher
from app.store import Store

WebClient = WebSocketServerProtocol

dispatcher = RequestDispatcher()
store = Store()


@dispatcher.on_client_connected
async def on_client_connected(web_client: WebClient):
    print(f"newClient={web_client}")
    store.add_user(web_client)


@dispatcher.on_client_closed
async def on_client_closed(web_client: WebClient):
    print(f"clientClosed={web_client}")
    user = store.get_user(web_client)

    store.remove_user(web_client)


@dispatcher.request("createGame")
async def on_create_game(client: WebClient, request: dict):
    user = store.get_user(client)
    user = store.modify_user(user, name=request["playerName"])

    game = store.create_game(user)
    print(f"Created game {game.code} with admin {game.admin.name}")

    await dispatcher.add_to_message_queue(
        client,
        {
            "joinGame": {
                "gameCode": game.code,
                "players": game.get_players_response(user),
                "admin": True,
                "currentPlayer": user.join_game_json(user, include_uuid=True)
            }
        },
    )


@dispatcher.request("joinGame")
async def join_game(client: WebClient, request: dict):
    user, synced = store.get_or_sync_user(client, request["uuid"])

    # Only modify the users name if they don't have one yet
    if not user.name:
        user = store.modify_user(user, name=request["playerName"])

    code = request["gameCode"]
    game = store.get_game(code)

    if game is None:
        # TODO Send back game does not exist response
        print(f"{user.name} attempted to join game {code}, which does not exist")
        await dispatcher.add_to_message_queue(
            client, {"noGameFound": {"gameCode": code}}
        )
        return

    new_join = user not in game.players

    if new_join:
        player, game = store.add_player_to_game(user, game)
        print(f"Player {user.name} joined game {code}")

    # Inform the user he joined the game
    await dispatcher.add_to_message_queue(
        client,
        {
            "joinGame": {
                "gameCode": code,
                "players": game.get_players_response(user),
                "admin": False,
                "currentPlayer": user.join_game_json(user, include_uuid=True)
            }
        },
    )

    # No need to do anything else if the user has been in the lobby previously
    if not new_join:
        return

    # Inform the other players in the game that someone has joined
    other_players = [player for player in game.players if player != user]
    joined_game_request = {"playerJoinedGame": {"player": user.join_game_json()}}

    await asyncio.gather(
        *[
            dispatcher.add_to_message_queue(player.web_client, joined_game_request)
            for player in other_players
        ]
    )
