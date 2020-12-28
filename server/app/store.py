import random
import string

from typing import Dict, Optional, Tuple

from app.user import WebClient, User
from app.game import Game
from app.exceptions import RequestError


class Store:
    __sentinel = object()

    def __init__(self):
        self._users: Dict[WebClient, User] = {}
        # Disconnected users associated by their uuid
        self._disconnected_users: Dict[str, User] = {}
        self._games: Dict[str, Game] = {}

    def add_user(self, client: WebClient) -> User:
        user = User(client)
        self._users[client] = user
        return user

    def get_user(self, client) -> User:
        return self._users[client]

    def get_or_sync_user(self, client, uuid: str) -> Tuple[User, bool]:
        synced = uuid in self._disconnected_users

        if synced:
            self._users[client] = self._disconnected_users.pop(uuid)
            self._users[client].web_client = client

        return self._users[client], synced

    def modify_user(self, user, name=__sentinel) -> User:
        if name is not self.__sentinel:
            user.name = name

        return user

    def remove_user(self, client):
        user = self._users.pop(client)
        self._disconnected_users[user.uuid] = user

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
                f"Game {game.code} already has a player named {player.name}, please "
                f" choose a different name",
                "LOBBY_ERROR",
                player.web_client
            )

        game.add_player(player)
        return player, game

    def set_game_state(self, game: Game, state: Game.State):
        game.state = state
        return game
