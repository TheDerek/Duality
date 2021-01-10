from typing import List

from app.store import Store, Player, GameState, Prompt, Drawing


class ResponseGenerator:
    def __init__(self, store: Store):
        self._store: Store = store

    @staticmethod
    def generate_update_game_state(state: GameState):
        return {"updateGameState": {"gameState": state.name}}

    def generate_join_game(self, game_code: str, player_id: int, uuid: str) -> dict:
        state: GameState = self._store.get_game_state(game_code)

        if state != GameState.WAITING_ROOM and self._store.player_finished_submission(
            game_code, player_id
        ):
            state = GameState.WAITING_FOR_PLAYERS

        return {
            "joinGame": {
                "gameCode": game_code,
                "players": self._generate_players(game_code, player_id),
                "admin": self._store.is_admin_of_game(player_id, game_code),
                "currentPlayer": self._generate_player(
                    game_code, player_id, private_info=True
                ),
                "gameState": state.name,
                "uuid": uuid,
                "drawingPrompts": self._store.get_drawing_prompts_for_player(player_id),
                "drawing": self._store.get_current_drawing(game_code)
            }
        }

    def generate_player_joined_game(self, player_id: int, code: str):
        return {"playerJoinedGame": {"player": self._generate_player(code, player_id)}}

    def generate_update_player(
        self, code: str, player_id: int, status=None, private_info: bool = False
    ):
        return {
            "updatePlayer": {
                "player": self._generate_player(code, player_id, private_info),
                "status": status,
            }
        }

    def drawing_prompts(self, player_id: int):
        # Get the players drawing
        prompts: List[str] = self._store.get_drawing_prompts_for_player(player_id)
        return {
            "setDrawingPrompts": {
                "prompts": prompts
            }
        }

    def current_drawing(self, game_code):
        drawing: str = self._store.get_current_drawing(game_code)
        return {
            "setDrawing": {
                "drawing": drawing
            }
        }

    def _generate_player(
        self, game_code: str, player_id: int, private_info=False
    ) -> dict:
        player: Player = self._store.get_player(player_id)
        prompt_count = self._store.player_prompt_count(game_code, player_id)

        response = {
            "name": player.name,
            "admin": player.admin,
            "submissionFinished": self._store.player_finished_submission(
                game_code, player_id
            ),
            "currentPlayer": private_info,
        }

        if private_info:
            prompts: List[Prompt] = self._store.get_prompts(game_code, player.id_)

            response["private"] = {
                "currentPromptNumber": prompt_count + 1,
                "prompts": [prompt.prompt for prompt in prompts],
            }

        return response

    def _generate_players(self, game_code: str, player_id: int) -> list:
        players: List[Player] = self._store.get_players(game_code)

        return [
            self._generate_player(
                game_code, player.id_, private_info=player_id == player.id_
            )
            for player in players
        ]
