from typing import Dict, Tuple, Set
from websockets.server import WebSocketServerProtocol
from app.user import User

WebClient = WebSocketServerProtocol


class Game:
    def __init__(self, code: str, admin: User):
        self.players: Set[User] = set()
        self.code: str = code
        self.admin = admin

        self.add_player(self.admin)

    def add_player(self, player: User):
        player.current_game = self
        self.players.add(player)
