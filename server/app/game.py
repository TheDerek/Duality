from typing import Dict, Tuple, Set
from websockets.server import WebSocketServerProtocol
from app.user import User

WebClient = WebSocketServerProtocol


class Game:
    def __init__(self, code: str, admin: User):
        self.players: Set[User] = set()
        self.code: str = code
        self.admin: User = admin

        self.add_player(self.admin)

    def add_player(self, player: User):
        player.current_game = self
        self.players.add(player)

    def is_admin(self, player: User):
        return player == self.admin

    def get_players_response(self, current_user: User):
        return [player.join_game_json(current_user) for player in self.players]
