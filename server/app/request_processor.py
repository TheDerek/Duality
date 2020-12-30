import asyncio

from websockets.server import WebSocketServerProtocol

from app.response_generator import ResponseGenerator
from app.request_dispatcher import RequestDispatcher
from app.store import Store
from app.exceptions import RequestError, ErrorType, PromptError
from app.game import Game, State

WebClient = WebSocketServerProtocol

MINIMUM_PLAYERS = 3

dispatcher = RequestDispatcher()
store = Store()
response_generator = ResponseGenerator(store)


@dispatcher.on_client_connected
async def on_client_connected(web_client: WebClient):
    print(f"newClient={web_client}")
    store.add_client(web_client)


@dispatcher.on_client_closed
async def on_client_closed(web_client: WebClient):
    print(f"clientClosed={web_client}")

    store.remove_client(web_client)


@dispatcher.request("createGame")
async def on_create_game(client: WebClient, request: dict):
    uuid: str = store.get_or_create_user(client, request["uuid"])
    game_code: str = store.create_game(uuid, request["playerName"])

    await dispatcher.add_to_message_queue(
        client,
        response_generator.gen_join_game(game_code, uuid)
    )


@dispatcher.request("joinGame")
async def join_game(client: WebClient, request: dict):
    uuid: str = store.get_or_create_user(client, request["uuid"])



@dispatcher.request("startGame")
async def start_game(client: WebClient, request: dict):
    user = store.get_user(client)

    if not user.current_game:
        raise RequestError(ErrorType.WAITING_ROOM_ERROR, "Not in a game to start")

    game: Game = user.current_game
    store.set_game_state(game, State.SUBMIT_ATTRIBUTES)

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


@dispatcher.request("submitPrompt")
async def submit_prompt(client: WebClient, request: dict):
    user = store.get_user(client)
    game = user.current_game

    if game.state != State.SUBMIT_ATTRIBUTES:
        raise PromptError("Incorrect game state")

    store.add_prompt(user, request["prompt"])
