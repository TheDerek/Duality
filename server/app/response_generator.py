from typing import List, Optional

from app.situations import Situation
from app.store import Store, Player, GameState, Prompt, Drawing, AssignedPrompt


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

        display_scores: bool = state == GameState.DISPLAY_SCORES

        return {
            "joinGame": {
                "gameCode": game_code,
                "players": self._generate_players(game_code, player_id, display_scores),
                "admin": self._store.is_admin_of_game(player_id, game_code),
                "currentPlayer": self._generate_player(
                    game_code, player_id, private_info=True, scores=display_scores
                ),
                "gameState": state.name,
                "uuid": uuid,
                "drawingPrompts": self._store.get_drawing_prompts_for_player(player_id, game_code),
                "drawing": self._store.get_current_drawing_image(game_code),
                "assignedPrompts": self._generate_assigned_prompts(
                    self._store.get_assigned_prompts(game_code)
                ),
                "isGameFinished": self._store.is_game_finished(game_code),
                "situation": self._situation(self._store.get_current_situation(game_code))
            }
        }

    def generate_set_situation(self, game_code: str):
        situation: Optional[Situation] = self._store.get_current_situation(game_code)
        return {
            "setSituation": {
                "situation": self._situation(situation)
            }
        }

    def generate_player_joined_game(self, player_id: int, code: str):
        return {"playerJoinedGame": {"player": self._generate_player(code, player_id)}}

    def generate_update_player(
        self, code: str, player_id: int, status=None, private_info: bool = False, scores: bool = False
    ):
        return {
            "updatePlayer": {
                "player": self._generate_player(code, player_id, private_info, scores),
                "status": status,
            }
        }

    def generate_update_all_players(self, game_code: str, players: List[Player], player_id: int, scores: bool = False):
        """Generate a Response to update all players"""
        return {
            "updateAllPlayers": {
                "players": self._generate_players(game_code, player_id, scores),
                "currentPlayer": self._generate_player(game_code, player_id, True, scores),
                "gameState": self._store.get_game_state(game_code).name
            }
        }

    def drawing_prompts(self, player_id: int, game_code: str):
        # Get the players drawing
        prompts: List[str] = self._store.get_drawing_prompts_for_player(player_id, game_code)
        return {"setDrawingPrompts": {"prompts": prompts}}

    def current_drawing(self, game_code):
        drawing: str = self._store.get_current_drawing(game_code).drawing
        return {"setDrawing": {"drawing": drawing}}

    def assigned_prompts(self, game_code: str):
        """Return a list of prompts assigned for the current drawing for the current
        round"""

        prompts: List[AssignedPrompt] = self._store.get_assigned_prompts(game_code)
        return {
            "setAssignedPrompts": {
                "prompts": [
                    {
                        "player_name": prompt.player_name,
                        "prompt": prompt.prompt,
                        "correct": prompt.correct,
                    }
                    for prompt in prompts
                ]
            }
        }

    def reset_submission_status(self):
        return {
            "resetSubmissionStatus": {

            }
        }

    def finished_game(self):
            return {
                "finishedGame": {

                }
            }

    def _situation(self, situation: Optional[Situation]):
        if not situation:
            return None

        return {
            "prompts": situation.prompts,
            "drawing": situation.drawing,
            "results": situation.results
        }

    def _generate_assigned_prompts(self, prompts: List[AssignedPrompt]):
        return [
            {
                "player_name": prompt.player_name,
                "prompt": prompt.prompt,
                "correct": prompt.correct,
            }
            for prompt in prompts
        ]

    def _generate_player(
        self, game_code: str, player_id: int, private_info=False, scores=False
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
                "prompts": [{"prompt": prompt.prompt, "enabled": prompt.enabled} for prompt in prompts],
            }

        if scores:
            score = self._store.get_score(player_id)
            response["score"] = {
                "previous": score.previous,
                "current_round": score.current_round,
                "total": score.total
            }

        return response

    def _generate_players(self, game_code: str, player_id: int, scores: bool = False) -> list:
        players: List[Player] = self._store.get_players(game_code)

        return [
            self._generate_player(
                game_code, player.id_, player_id == player.id_, scores
            )
            for player in players
        ]
