import random
import string
import asyncio

from typing import Dict
from websockets.server import WebSocketServerProtocol
from app.game import Game
from app.user import User
from app.request_dispatcher import RequestDispatcher

WebClient = WebSocketServerProtocol

dispatcher = RequestDispatcher()

users: Dict[WebClient, User] = {}
games: Dict[str, Game] = {}


@dispatcher.on_client_connected
async def on_client_connected(web_client: WebClient):
    print(f"newClient={web_client}")
    users[web_client] = User(web_client)


@dispatcher.on_client_closed
async def on_client_closed(web_client: WebClient):
    print(f"clientClosed={web_client}")
    user = users[web_client]

    if user.current_game:
        if len(user.current_game.players) == 1:
            print(
                f"Deleting game {user.current_game.code} because the last player has left"
            )
            del games[user.current_game.code]

    del users[web_client]


@dispatcher.request("createGame")
async def on_create_game(client: WebClient, request: dict):
    # await asyncio.sleep(2)

    user = users[client]
    user.name = request["playerName"]

    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    game = Game(code, user)

    games[code] = game
    print(f"Created game {code} with admin {user.name}")

    await dispatcher.add_to_message_queue(
        client,
        {
            "joinGame": {
                "gameCode": code,
                "players": game.get_players_response(user),
                "admin": True
            }
        },
    )


@dispatcher.request("joinGame")
async def join_game(client: WebClient, request: dict):
    # await asyncio.sleep(2)

    user = users[client]
    user.name = request["playerName"]

    code = request["gameCode"]

    if code not in games:
        # TODO Send back game does not exist response
        print(f"{user.name} attempted to join game {code}, which does not exist")
        await dispatcher.add_to_message_queue(
            client, {"noGameFound": {"gameCode": code}}
        )
        return

    game = games[code]
    game.add_player(user)
    print(f"Player {user.name} joined game {code}")

    # Inform the user he joined the game
    await dispatcher.add_to_message_queue(
        client,
        {
            "joinGame": {
                "gameCode": code,
                "players": game.get_players_response(user),
                "admin": False
            }
        },
    )

    # Inform the other players in the game that someone has joined
    other_players = [player for player in game.players if player != user]
    joined_game_request = {"playerJoinedGame": {"player": user.join_game_json()}}

    await asyncio.gather(
        *[
            dispatcher.add_to_message_queue(player.web_client, joined_game_request)
            for player in other_players
        ]
    )
