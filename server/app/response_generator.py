from typing import List

from app.store import Store, Player, GameState


class ResponseGenerator:
    def __init__(self, store: Store):
        self._store: Store = store

    def generate_join_game(self, game_code: str, user_uuid: str) -> dict:
        state: GameState = self._store.get_game_state(game_code)

        if state != GameState.WAITING_ROOM and self._store.player_finished_submission(game_code, user_uuid):
            state = GameState.WAITING_FOR_PLAYERS

        return {
            "joinGame": {
                "gameCode": game_code,
                "players": self._generate_players(game_code, user_uuid),
                "admin": self._store.is_admin_of_game(user_uuid, game_code),
                "currentPlayer": self._generate_player(
                    game_code, user_uuid, private_info=True
                ),
                "gameState": state.name,
                "uuid": user_uuid,
            }
        }

    def generate_player_joined_game(self, uuid: str, code: str):
        return {"playerJoinedGame": {"player": self._generate_player(code, uuid)}}

    def generate_update_game_state(self, state: GameState):
        return {"updateGameState": {"gameState": state.name}}

    def generate_update_player(self, code: str, uuid: str, status=None, private_info: bool = False):
        return {
            "updatePlayer": {
                "player": self._generate_player(code, uuid, private_info),
                "status": status
            }
        }

    def _generate_player(
        self, game_code: str, user_uuid: str, private_info=False
    ) -> dict:
        player: Player = self._store.get_player(game_code, user_uuid)
        prompt_count = self._store.player_prompt_count(game_code, user_uuid)

        response = {
            "name": player.name,
            "admin": player.admin,
            "submissionFinished": self._store.player_finished_submission(
                game_code, user_uuid
            ),
            "currentPlayer": private_info
        }

        if private_info:
            prompts = self._store.get_prompts(game_code, user_uuid)

            response["private"] = {
                "uuid": user_uuid,
                "currentPromptNumber": prompt_count + 1,
                "prompts": list(prompts)
            }

        return response

    def _generate_players(self, game_code: str, uuid: str) -> list:
        players: List[Player] = self._store.get_players(game_code)

        return [self._generate_player(game_code, player.uuid, private_info=uuid == player.uuid) for player in players]
