from typing import List

from app.store import Store, Player


class ResponseGenerator:
    def __init__(self, store: Store):
        self._store: Store = store

    def gen_join_game(self, game_code: str, user_uuid: str) -> dict:
        return {
            "joinGame": {
                "gameCode": game_code,
                "players": self.generate_players(game_code, user_uuid),
                "admin": self._store.is_admin_of_game(user_uuid, game_code),
                "currentPlayer": self.generate_player(game_code, user_uuid),
                "gameState": self._store.get_game_state(game_code)
            }
        }

    def generate_player(self, game_code: str, user_uuid: str) -> dict:
        player: Player = self._store.get_player(game_code, user_uuid)

        return {
            "name": player.name,
            "admin": player.admin,
        }

    def generate_players(self, game_code: str, user_uuid: str) -> list:
        players: List[Player] = self._store.get_players(game_code)

        return [
            {
                "name": player.name,
                "admin": player.admin,
            }
            for player in players
        ]
