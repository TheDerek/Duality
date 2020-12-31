from typing import List

from app.store import Store, Player, GameState


class ResponseGenerator:
    def __init__(self, store: Store):
        self._store: Store = store

    def generate_join_game(self, game_code: str, user_uuid: str) -> dict:
        return {
            "joinGame": {
                "gameCode": game_code,
                "players": self._generate_players(game_code, user_uuid),
                "admin": self._store.is_admin_of_game(user_uuid, game_code),
                "currentPlayer": self._generate_player(game_code, user_uuid),
                "gameState": self._store.get_game_state(game_code),
                "uuid": user_uuid,
            }
        }

    def generate_player_joined_game(self, uuid: str, code: str):
        return {
            "playerJoinedGame": {
                "player": self._generate_player(code, uuid)
            }
        }

    def generate_update_game_state(self, state: GameState):
        return {
            "updateGameState": {
                "gameState": state.name
            }
        }

    def _generate_player(self, game_code: str, user_uuid: str) -> dict:
        player: Player = self._store.get_player(game_code, user_uuid)

        return {
            "name": player.name,
            "admin": player.admin,
        }

    def _generate_players(self, game_code: str, user_uuid: str) -> list:
        players: List[Player] = self._store.get_players(game_code)

        return [
            {
                "name": player.name,
                "admin": player.admin,
            }
            for player in players
        ]
