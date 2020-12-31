import asyncio

from typing import List

from websockets.server import WebSocketServerProtocol

from app.response_generator import ResponseGenerator
from app.request_dispatcher import RequestDispatcher
from app.store import Store, Player, GameState
from app.exceptions import LobbyError, PromptError, WaitingRoomError, DatabaseError
from app.constants import MINIMUM_PLAYERS


WebClient = WebSocketServerProtocol

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
    game_code: str = store.create_game(client, uuid, request["playerName"])

    await dispatcher.add_to_message_queue(
        client, response_generator.generate_join_game(game_code, uuid)
    )


@dispatcher.request("joinGame")
async def join_game(client: WebClient, request: dict):
    code: str = request["gameCode"]
    name: str = request["playerName"]
    uuid: str = store.get_or_create_user(client, request["uuid"])
    already_in_game: bool = store.is_user_in_game(uuid, code)

    if not already_in_game:
        if store.get_game_state(code) != GameState.WAITING_ROOM:
            raise LobbyError("Game has already started")

        if store.game_has_name(code, name):
            raise LobbyError(
                f"Name '{name}' is already in use for this game, please "
                f"choose another name"
            )

        # Get the players in the game before the user joins
        old_players = store.get_players(code)

        store.add_user_to_game(client, uuid, code, request["playerName"])

        response = response_generator.generate_player_joined_game(uuid, code)
        await asyncio.gather(
            *[
                dispatcher.add_to_message_queue(player.client, response)
                for player in old_players
            ]
        )
    else:
        # If the player was in the game previously we need to update their client with
        # the one they've connected with
        store.update_player_client(uuid, code, client)

    # Inform the user himself that he has joined the game
    await dispatcher.add_to_message_queue(
        client, response_generator.generate_join_game(code, uuid)
    )


@dispatcher.request("startGame")
async def start_game(client: WebClient, request: dict):
    code: str = request["gameCode"]
    uuid: str = store.get_uuid(client)

    if store.get_game_state(code) != GameState.WAITING_ROOM:
        raise WaitingRoomError("Game already started")

    player: Player = store.get_player(code, uuid)

    if not player.admin:
        raise WaitingRoomError("Not in a game to start")

    players: List[Player] = store.get_players(code)

    if len(players) < MINIMUM_PLAYERS:
        raise WaitingRoomError("Not enough players to start")

    # Update the game state in the db so players who rejoin start in the right state
    store.update_game_state(code, GameState.SUBMIT_ATTRIBUTES)

    # Create the first round of the game
    store.create_next_round(code)

    response = response_generator.generate_update_game_state(
        GameState.SUBMIT_ATTRIBUTES
    )
    await asyncio.gather(
        *[
            dispatcher.add_to_message_queue(player.client, response)
            for player in players
        ]
    )


@dispatcher.request("submitPrompt")
async def submit_prompt(client: WebClient, request: dict):
    code: str = request["gameCode"]
    uuid: str = store.get_uuid(client)

    if store.get_game_state(code) != GameState.SUBMIT_ATTRIBUTES:
        raise PromptError("Incorrect game state")

    store.submit_prompt(code, uuid, request["prompt"])

    # Inform the players that someone has finished the submission
    if store.has_finished_prompt_submission(code, uuid):
        # TODO: If all players have submitted move onto the next stage instead of
        # informing the players that the last player has submitted
        players: List[Player] = store.get_players(code)
        await asyncio.gather(
            *[
                dispatcher.add_to_message_queue(
                    player.client,
                    response_generator.generate_update_player(
                        code,
                        uuid,
                        private_info=uuid == player.uuid,
                        status="FINISHED_PROMPT_SUBMISSION"
                        if uuid == player.uuid
                        else None,
                    ),
                )
                for player in players
            ]
        )
    else:
        # Otherwise just inform the submitting player of their submission status
        await dispatcher.add_to_message_queue(
            client,
            response_generator.generate_update_player(
                code, uuid, private_info=True, status="NORMAL"
            ),
        )
