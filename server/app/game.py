from typing import Dict, Set, List
from dataclasses import dataclass, field
from enum import Enum, auto

from app.user import User


NUMBER_OF_ROUNDS = 3
NUMBER_OF_PROMPTS = 2


@dataclass()
class Round:
    number: int
    prompts: Dict[User, List[str]] = field(default_factory=dict)


class Game:
    class State(Enum):
        WAITING_ROOM = auto()
        SUBMIT_ATTRIBUTES = auto()

    def __init__(self, code: str, admin: User):
        # Players in the game
        self.players: Set[User] = set()
        # The current state the game is in, this will determine what the client displays
        self.state = Game.State.WAITING_ROOM
        # The game code, can be used to join the game if it has not started yet or to
        # rejoin the game
        self.code: str = code
        # The admin of the game, has the ability to start the game once the required
        # number of people are present
        self.admin: User = admin

        # The rounds in the game
        self._rounds: List[Round] = [Round(i) for i in range(0, NUMBER_OF_ROUNDS)]
        # List of names already used in the game
        self._names: Set[str] = set()
        # The index of the current round
        self._current_round: int = 0

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

    def get_current_round(self) -> Round:
        return self._rounds[self._current_round]
