import asyncio

from websockets.server import WebSocketServerProtocol
from app.request_dispatcher import RequestDispatcher
from app.store import Store
from app.exceptions import RequestError, ErrorType
from app.game import Game

WebClient = WebSocketServerProtocol

MINIMUM_PLAYERS = 3

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
                "currentPlayer": user.join_game_json(user, include_uuid=True),
                "gameState": game.state.name
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
        raise RequestError(
            ErrorType.LOBBY_ERROR,
            f"Game {code} does not exist, please try another code or create a game"
        )

    new_join = user not in game.players

    if new_join:
        user, game = store.add_player_to_game(user, game)
        print(f"Player {user.name} joined game {code}")

    # Inform the user he joined the game
    await dispatcher.add_to_message_queue(
        client,
        {
            "joinGame": {
                "gameCode": code,
                "players": game.get_players_response(user),
                "admin": False,
                "currentPlayer": user.join_game_json(user, include_uuid=True),
                "gameState": game.state.name
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


@dispatcher.request("startGame")
async def start_game(client: WebClient, request: dict):
    user = store.get_user(client)

    if not user.current_game:
        raise RequestError(ErrorType.WAITING_ROOM_ERROR, "Not in a game to start")

    game: Game = user.current_game
    store.set_game_state(game, Game.State.SUBMIT_ATTRIBUTES)

    if len(game.players) < MINIMUM_PLAYERS:
        raise RequestError(ErrorType.WAITING_ROOM_ERROR, "Not enough players to start")

    if not game.admin == user:
        raise RequestError(ErrorType.WAITING_ROOM_ERROR, "Not admin of game")

    def response(player):
        return {
            "startedGame": {
                "gameCode": game.code,
                "players": game.get_players_response(player),
                "currentPlayer": player.join_game_json(user, True),
                "admin": game.admin == player,
                "gameState": game.state.name
            }
        }

    await asyncio.gather(
        *[
            dispatcher.add_to_message_queue(player.web_client, response(user))
            for player in game.players
        ]
    )


@dispatcher.request("startGame")
async def submit_prompt(client: WebClient, request: dict):
    pass