from websockets.server import WebSocketServerProtocol

WebClient = WebSocketServerProtocol


class User:
    def __init__(self, web_client):
        self.web_client: WebClient = web_client
        self.name: str = ""
        self.current_game = None
