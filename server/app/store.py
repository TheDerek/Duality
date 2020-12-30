import random
import string
import asyncio

from typing import Dict, Optional, List, Set

import aiosqlite

from app.user import WebClient, User
from app.game import Game, State
from app.exceptions import RequestError, PromptError, ErrorType


class Store:
    __sentinel = object()

    def __init__(self):
        self._users: Dict[WebClient, Optional[str]] = {}

        # Disconnected users associated by their uuid
        self._disconnected_users: Set[str] = set()

        self._database: aiosqlite.Connection = aiosqlite.connect(
            "sqlite:////home/derek/git/boss-fight/database/db.sqlite3"
        )

    def __exit__(self, exc_type, exc_value, traceback):
        self._database.close()

    def add_client(self, client: WebClient):
        print("Adding client")
        self._users[client] = None

    def remove_client(self, client):
        print("Removing client")
        uuid: str = self._users.pop(client)

        if uuid:
            self._disconnected_users.add(uuid)

    def add_user(self, client: WebClient) -> User:
        user = User(client)
        self._users[client] = user
        return user

    def get_user(self, client) -> User:
        return self._users[client]

    def get_or_sync_user(self, client, uuid: str) -> User:
        synced = uuid in self._disconnected_users

        if synced:
            self._users[client] = self._disconnected_users.pop(uuid)
            self._users[client].web_client = client

        return self._users[client]

    def modify_user(self, user, name=__sentinel) -> User:
        if name is not self.__sentinel:
            user.name = name

        return user

    def create_game(self, admin: User) -> Game:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        game = Game(code, admin)

        self._games[code] = game
        return game

    def get_game(self, code: str) -> Optional[Game]:
        if code not in self._games:
            return None

        return self._games[code]

    def add_player_to_game(self, player: User, game: Game) -> (User, Game):
        if game.has_name(player.name):
            raise RequestError(
                ErrorType.LOBBY_ERROR,
                f"Game {game.code} already has a player named {player.name}, please "
                f" choose a different name"
            )

        game.add_player(player)
        return player, game

    def set_game_state(self, game: Game, state: State):
        game.state = state
        return game

    def get_user_prompts(self, user: User) -> List[str]:
        game: Game = user.current_game
        return game.get_current_round().prompts[user]

    def add_prompt(self, user: User, prompt: str) -> None:
        user.current_game.add_prompt(user, prompt)
