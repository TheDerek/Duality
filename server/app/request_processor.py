import asyncio

from typing import List, Tuple

from websockets.server import WebSocketServerProtocol

from app import game_logic
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
    game_code, player_id = store.create_game(client, uuid, request["playerName"])

    await dispatcher.add_to_message_queue(
        client, response_generator.generate_join_game(game_code, player_id, uuid)
    )


@dispatcher.request("joinGame")
async def join_game(client: WebClient, request: dict):
    code: str = request["gameCode"].upper().strip()
    name: str = request["playerName"].strip()
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

        player: Player = store.add_user_to_game(
            client, uuid, code, request["playerName"]
        )

        response = response_generator.generate_player_joined_game(player.id_, code)
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
        client,
        response_generator.generate_join_game(
            code, store.get_player_id(code, uuid), uuid
        ),
    )


@dispatcher.request("startGame")
async def start_game(client: WebClient, request: dict):
    code: str = request["gameCode"]
    uuid: str = store.get_uuid(client)

    if store.get_game_state(code) != GameState.WAITING_ROOM:
        raise WaitingRoomError("Game already started")

    player: Player = store.get_player_from_game(code, uuid)

    if not player.admin:
        raise WaitingRoomError("Not in a game to start")

    players: List[Player] = store.get_players(code)

    if len(players) < MINIMUM_PLAYERS:
        raise WaitingRoomError("Not enough players to start")

    # Create the first round of the game
    store.create_next_round(code)

    # Update the game states state and inform clients
    await change_state_and_inform(code, GameState.SUBMIT_PROMPTS)


@dispatcher.request("submitPrompt")
async def submit_prompt(client: WebClient, request: dict):
    code: str = request["gameCode"]
    uuid: str = store.get_uuid(client)

    if store.get_game_state(code) != GameState.SUBMIT_PROMPTS:
        raise PromptError("Incorrect game state")

    player: Player = store.get_player_from_game(code, uuid)

    store.submit_prompt(code, player.id_, request["prompt"])

    if store.all_prompts_submitted_for_round(code):
        # informing the players that this guy has finished his submissions
        await update_player(code, uuid)

        # Prepare the next stage of the game
        game_logic.prepare_draw_prompts(store, code)

        # Send the players the data they need for the drawing stage
        players: List[Player] = store.get_players(code)
        await asyncio.gather(
            *[
                dispatcher.add_to_message_queue(
                    p.client, response_generator.drawing_prompts(p.id_)
                )
                for p in players
            ]
        )

        # Reset the player submission status
        # Update the game states state and inform clients
        await reset_players_submission_status(players)
        await change_state_and_inform(code, GameState.DRAW_PROMPTS)
        return

    # Inform the players that someone has finished the submission
    if store.player_finished_prompt_submission(code, player.id_):
        # informing the players that this guy has finished his submissions
        await update_player(code, uuid)

        # Yeet the player into the waiting for players state
        await dispatcher.add_to_message_queue(
            client,
            response_generator.generate_update_game_state(
                GameState.WAITING_FOR_PLAYERS
            ),
        )
        return

    # If the player still has to submit some prompts then inform them of that
    await dispatcher.add_to_message_queue(
        client,
        response_generator.generate_update_player(
            code, player.id_, private_info=True, status="NORMAL"
        ),
    )


@dispatcher.request("submitDrawing")
async def submit_drawing(client: WebClient, request: dict):
    code: str = request["gameCode"]
    drawing: str = request["drawing"]
    uuid: str = store.get_uuid(client)

    if store.get_game_state(code) != GameState.DRAW_PROMPTS:
        raise PromptError("Incorrect game state")

    player: Player = store.get_player_from_game(code, uuid)

    if store.has_submitted_drawing(code, player.id_):
        raise PromptError("User already submitted drawing for this round")

    store.set_player_drawing_image(code, player.id_, drawing)

    # Inform players of updated player
    await update_player(code, uuid)

    if store.all_drawings_submitted_for_round(code):
        players = store.get_players(code)

        # Prepare the prompt assignment phase
        game_logic.prepare_assign_prompts(store, code)

        # Send the players the first drawing in the sequence
        response = response_generator.current_drawing(code)
        await asyncio.gather(
            *[
                dispatcher.add_to_message_queue(p.client, response)
                for p in players
            ]
        )

        # Reset the player submission status
        await reset_players_submission_status(players)
        await change_state_and_inform(code, GameState.ASSIGN_PROMPTS)
    else:
        # Otherwise just redirect the user to the waiting screen
        await dispatcher.add_to_message_queue(
            client,
            response_generator.generate_update_game_state(
                GameState.WAITING_FOR_PLAYERS
            ),
        )


@dispatcher.request("assignPrompt")
async def assign_prompt(client: WebClient, request: dict):
    code: str = request["gameCode"]
    prompt: str = request["prompt"]
    uuid: str = store.get_uuid(client)
    player: Player = store.get_player_from_game(code, uuid)

    if store.get_game_state(code) != GameState.ASSIGN_PROMPTS:
        raise PromptError("Incorrect game state")

    store.assign_prompt_to_current_image(code, player.id_, prompt)

    # Move players to the next state if the prompts have been submitted
    if store.prompts_assigned_for_current_round(code):
        response = response_generator.assigned_prompts(code)
        await send_response_to_players(response, store.get_players(code))
        await change_state_and_inform(code, GameState.DISPLAY_RESULTS)
        return

    # Otherwise move this player to the waiting room and inform the others
    # he is finished
    await update_player(code, uuid)
    await dispatcher.add_to_message_queue(
        client,
        response_generator.generate_update_game_state(GameState.WAITING_FOR_PLAYERS),
    )


@dispatcher.request("finishResults")
async def finish_results(client: WebClient, request: dict):
    code: str = request["gameCode"]
    uuid: str = store.get_uuid(client)
    player: Player = store.get_player_from_game(code, uuid)

    if not player.admin:
        raise PromptError("Player is not admin")

    if store.get_game_state(code) != GameState.DISPLAY_RESULTS:
        raise PromptError("Incorrect game state")

    if store.all_results_finished(code):
        await game_logic.prepare_display_scores(store, code)

    players = store.get_players(code)

    # Advance the drawing and send it to players
    store.next_drawing(game_code=code)
    response = response_generator.current_drawing(code)
    await send_response_to_players(response, players)

    # Redirect players to the assign prompts phase
    await change_state_and_inform(code, GameState.ASSIGN_PROMPTS)


async def update_player(code: str, uuid: str):
    """Update the given player for all clients in the current game"""
    # informing the players that this guy has finished his submissions
    players: List[Player] = store.get_players(code)
    player_id: int = store.get_player_id(code, uuid)
    await asyncio.gather(
        *[
            dispatcher.add_to_message_queue(
                p.client,
                response_generator.generate_update_player(
                    code, player_id, private_info=player_id == p.id_
                ),
            )
            for p in players
        ]
    )


async def change_state_and_inform(game_code: str, new_state: GameState):
    """
    Change the games state and inform all connected users of the change
    :param game_code: The code of the game's state to change
    :param new_state: The new state for the game
    """

    # Update the game state in the db
    store.update_game_state(game_code, new_state)

    # Get the connected clients for this game
    response = response_generator.generate_update_game_state(new_state)

    await asyncio.gather(
        *[
            dispatcher.add_to_message_queue(client, response)
            for client in store.get_clients_for_game(game_code)
        ]
    )


async def send_response_to_players(response: dict, players: List[Player]):
    await asyncio.gather(
        *[
            dispatcher.add_to_message_queue(player.client, response)
            for player in players
        ]
    )


async def reset_players_submission_status(players: List[Player]):
    response = response_generator.reset_submission_status()
    await send_response_to_players(response, players)
