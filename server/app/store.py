import random
import string

from typing import Dict, Optional

from app.user import WebClient, User
from app.game import Game


class Store:
    __sentinel = object()

    def __init__(self):
        self._users: Dict[WebClient, User] = {}
        self._games: Dict[str, Game] = {}

    def add_user(self, client: WebClient) -> User:
        user = User(client)
        self._users[client] = user
        return user

    def get_user(self, client) -> User:
        return self._users[client]

    def modify_user(self, user, name=__sentinel) -> User:
        if name is not self.__sentinel:
            user.name = name

        return user

    def remove_user(self, client):
        # user = self.get_user(client)
        #
        # if user.current_game and len(user.current_game.players) == 1:
        #     print("Deleting game {} because the last user in the game {} has left".format(
        #         user.current_game.code, user.name
        #     ))
        #     del self._games[user.current_game.code]

        del self._users[client]

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
        game.add_player(player)
        return player, game
