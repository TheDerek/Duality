import uuid

from websockets.server import WebSocketServerProtocol

WebClient = WebSocketServerProtocol


class User:
    def __init__(self, web_client):
        self.web_client: WebClient = web_client
        self.name: str = ""
        self.current_game = None
        self.uuid: str = str(uuid.uuid4())

    def join_game_json(self, current_player=None, include_uuid=False):
        return {
            "name": self.name,
            "admin": self.current_game.is_admin(self),
            "currentPlayer": current_player == self,
            "uuid": self.uuid if include_uuid else None,
        }
