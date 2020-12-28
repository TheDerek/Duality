from typing import Dict, Tuple, Set
from enum import Enum, auto

from websockets.server import WebSocketServerProtocol as WebClient

from app.user import User


class Game:
    class State(Enum):
        SUBMIT_ATTRIBUTES: auto()

    def __init__(self, code: str, admin: User):
        self.players: Set[User] = set()
        self.state = Game.State.SUBMIT_ATTRIBUTES
        # List of names already used in the game
        self._names: Set[str] = set()

        self.code: str = code
        self.admin: User = admin
        self.add_player(self.admin)

    def add_player(self, player: User):
        player.current_game = self
        self.players.add(player)
        self._names.add(player.name.lower())

    def is_admin(self, player: User):
        return player == self.admin

    def get_players_response(self, current_user: User):
        return [player.join_game_json(current_user) for player in self.players]

    def has_name(self, name: str) -> bool:
        return name.lower() in self._names
