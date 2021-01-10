import random
import string
import sqlite3

from collections import defaultdict
from enum import Enum, auto
from uuid import uuid4
from typing import Dict, Optional, Set, List, Iterable, Tuple
from dataclasses import dataclass

from websockets.server import WebSocketServerProtocol as WebClient

from app import constants
from app.exceptions import DatabaseError, PromptError


@dataclass()
class Player:
    id_: int
    uuid: str
    game_code: str
    name: str
    admin: bool
    client: WebClient


class Drawing:
    def __init__(
        self,
        drawing_id: int,
        round_id: int,
        player_id: int,
        sequence: int,
        client: sqlite3.Connection,
    ):
        self.drawing_id: int = drawing_id
        self.round_id: int = round_id
        self.player_id: int = player_id
        self.sequence: int = sequence
        self._db: sqlite3.Connection = client

    @property
    def drawing(self):
        cursor = self._db.cursor()
        cursor.execute("SELECT drawing from drawing WHERE id=?", (self.drawing_id,))
        return cursor.fetchone()["drawing"]


@dataclass()
class Prompt:
    id_: int
    player_id: int
    round_id: int
    prompt_number: int
    prompt: str
    drawing_id: Optional[int]
    assigned_drawing_id: Optional[int]


class GameState(Enum):
    WAITING_ROOM = auto()
    SUBMIT_ATTRIBUTES = auto()
    DRAW_PROMPTS = auto()
    WAITING_FOR_PLAYERS = auto()
    ASSIGN_PROMPTS = auto()


class Store:
    __sentinel = object()

    def __init__(self):
        # Maps connected clients to uuids
        self._users: Dict[WebClient, Optional[str]] = {}
        # Maps connected clients to their hashes
        self._clients: Dict[int, Optional[WebClient]] = defaultdict(lambda: None)

        self._db: sqlite3.Connection = sqlite3.connect(
            "/home/derek/git/boss-fight/database/db.sqlite3"
        )
        self._db.row_factory = sqlite3.Row

    def __exit__(self, exc_type, exc_value, traceback):
        self._db.close()

    def add_client(self, client: WebClient):
        print("Adding client")
        self._users[client] = None
        self._clients[hash(client)] = client

    def remove_client(self, client):
        print("Removing client")
        del self._clients[hash(client)]

    def add_user_to_game(
        self,
        client: WebClient,
        user_uuid: str,
        game_code: str,
        user_name: str,
        admin=False,
    ) -> Player:
        # Add the user to the game
        cursor = self._db.cursor()
        cursor.execute(
            "INSERT INTO player (game_code, user_uuid, client_hash, admin, name)"
            "VALUES (?, ?, ?, ?, ?)",
            (game_code, user_uuid, hash(client), admin, user_name.strip()),
        )

        return Player(
            uuid=user_uuid,
            game_code=game_code,
            name=user_name,
            admin=admin,
            client=client,
            id_=cursor.lastrowid,
        )

    def create_game(
        self, client: WebClient, admin_uuid: str, admin_name: str
    ) -> Tuple[str, int]:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))

        # Create the game
        self._db.execute("INSERT INTO game (code) VALUES (?)", [code])

        # Add the first user (also the admin) to the game
        player_id: int = self.add_user_to_game(
            client, admin_uuid, code, admin_name, admin=True
        ).id_

        # Write changes to db
        self._db.commit()

        return code, player_id

    def create_game_player(self, uuid: str):
        pass

    def get_or_create_user(self, client: WebClient, uuid: Optional[str]) -> str:
        # If the user has not provided a uuid or has provided a fake uuid that is not
        # in the database generate a new uuid for them
        if not uuid or not self._database_has_user(uuid):
            uuid = str(uuid4())
            self._db.execute("INSERT INTO user (uuid) values (?)", [uuid])
            self._db.commit()

        # Assign the uuid to the connected client and to the database
        self._users[client] = uuid
        return uuid

    def is_admin_of_game(self, player_id: int, game_code: str) -> bool:
        cursor: sqlite3.Cursor = self._db.cursor()
        return bool(
            cursor.execute(
                "SELECT admin FROM player WHERE id=? and game_code=?",
                [player_id, game_code],
            ).fetchone()["admin"]
        )

    def get_game_state(self, game_code: str) -> GameState:
        cursor: sqlite3.Cursor = self._db.cursor()
        db_state = cursor.execute(
            "SELECT state FROM game WHERE code=?",
            [game_code],
        ).fetchone()

        if not db_state:
            raise DatabaseError(f"Game {game_code} does not exist")

        return GameState[db_state["state"]]

    def get_player_id(self, game_code: str, uuid: str) -> int:
        cursor: sqlite3.Cursor = self._db.cursor()
        return cursor.execute(
            "SELECT id FROM player where game_code=? and user_uuid=?", (game_code, uuid)
        ).fetchone()["id"]

    def get_player_from_game(self, game_code, uuid):
        player_id: int = self.get_player_id(game_code, uuid)
        return self.get_player(player_id)

    def get_player(self, player_id: int) -> Player:
        cursor: sqlite3.Cursor = self._db.cursor()
        db_player = cursor.execute(
            "SELECT name, admin, client_hash, user_uuid, game_code FROM player "
            "WHERE id=?",
            [player_id],
        ).fetchone()

        return Player(
            id_=player_id,
            uuid=db_player["user_uuid"],
            game_code=db_player["game_code"],
            name=db_player["name"],
            admin=bool(db_player["admin"]),
            client=self._clients[db_player["client_hash"]],
        )

    def get_players(self, game_code) -> List[Player]:
        cursor: sqlite3.Cursor = self._db.cursor()
        db_players = cursor.execute(
            "SELECT name, admin, user_uuid, client_hash, id FROM player WHERE game_code=?",
            [game_code],
        )

        return [
            Player(
                id_=db_player["id"],
                uuid=db_player["user_uuid"],
                game_code=game_code,
                name=db_player["name"],
                admin=bool(db_player["admin"]),
                client=self._clients[db_player["client_hash"]],
            )
            for db_player in db_players
        ]

    def is_user_in_game(self, uuid: str, code: str) -> bool:
        cursor: sqlite3.Cursor = self._db.cursor()
        return (
            cursor.execute(
                "SELECT user_uuid FROM player WHERE user_uuid=? and game_code=?",
                [uuid, code],
            ).fetchone()
            is not None
        )

    def update_player_client(self, uuid: str, code: str, client: WebClient):
        self._db.execute(
            "UPDATE player SET client_hash=? WHERE user_uuid=? and game_code=?",
            (hash(client), uuid, code),
        )
        self._db.commit()

    def get_uuid(self, client: WebClient) -> str:
        return self._users[client]

    def update_game_state(self, code: str, state: GameState):
        self._db.execute(
            "UPDATE game SET state=? WHERE code=?",
            (state.name, code),
        )
        self._db.commit()

    def game_has_name(self, code: str, name: str):
        cursor: sqlite3.Cursor = self._db.cursor()
        return bool(
            cursor.execute(
                "SELECT 1 FROM player WHERE LOWER(name)=? and game_code=?",
                [name.lower().strip(), code],
            ).fetchone()
        )

    def get_current_round_number(self, code: str) -> Optional[int]:
        cursor: sqlite3.Cursor = self._db.cursor()
        db_round_number = cursor.execute(
            "SELECT number FROM round WHERE game_code=? and current=?", [code, True]
        ).fetchone()

        if not db_round_number:
            return None

        return db_round_number["number"]

    def get_current_round_id(self, code: str) -> Optional[int]:
        cursor: sqlite3.Cursor = self._db.cursor()
        db_id = cursor.execute(
            "SELECT id FROM round WHERE game_code=? and current=?", [code, True]
        ).fetchone()

        if not db_id:
            return None

        return db_id["id"]

    def create_next_round(self, code: str) -> int:
        old_number = self.get_current_round_number(code)
        new_number = old_number + 1 if old_number else 0

        # Remove current from any old rounds in the game
        self._db.execute("UPDATE round SET current=FALSE WHERE game_code=?", (code,))

        # Add the new round
        self._db.execute(
            "INSERT INTO round (number, game_code, current) VALUES (?, ?, True)",
            (new_number, code),
        )

        self._db.commit()
        return new_number

    def get_prompts(self, code: str, player_id: Optional[int] = None) -> List[Prompt]:
        """Get the prompts submitted for the current round of the given game code"""
        round_id: int = self.get_current_round_id(code)

        cursor: sqlite3.Cursor = self._db.cursor()

        sql = "SELECT prompt, prompt_number, id as id_, drawing_id, assigned_drawing_id, round_id, player_id FROM prompt where round_id=?"
        fields = [round_id]

        if player_id:
            sql += " AND prompt.player_id=?"
            fields += [player_id]

        cursor.execute(sql, fields)

        return [Prompt(**row) for row in cursor]

    def player_prompt_count(self, code: str, player_id: int) -> int:
        """
        :return: the number of prompts the player has made for the current round
        """
        # TODO: Find a better way to do this
        return len(self.get_prompts(code, player_id))

    def game_has_prompt(self, code: str, prompt: str):
        """
        :return: True if the games current round has the given prompt, False otherwise
        """
        cursor: sqlite3.Cursor = self._db.cursor()
        return (
            cursor.execute(
                "SELECT 1 FROM prompt "
                "INNER JOIN round ON round.id=prompt.round_id "
                "WHERE round.current=TRUE AND round.game_code=? "
                "AND lower(prompt.prompt)=lower(?)",
                (code, prompt),
            ).fetchone()
            is not None
        )

    def submit_prompt(self, code: str, player_id: int, prompt: str) -> int:
        """Write a prompt to the database if it unique for that round and the user still
        has prompts to submit, otherwise throw a PromptError
        :param code: the game code to submit the prompt to
        :param player_id: the id of the player submitting the code
        :param prompt: the prompt being submitted
        :return: the number of prompts the player has submitted so far including this one
        """
        prompt = prompt.strip()

        if self.game_has_prompt(code, prompt):
            raise PromptError(
                f"Prompt has '{prompt}' has already been submitted for this round"
            )

        player_prompt_count = self.player_prompt_count(code, player_id)
        if player_prompt_count + 1 > constants.NUMBER_OF_PROMPTS_PER_USER:
            raise PromptError("User has already submitted all prompts for this round")

        round_id: int = self.get_current_round_id(code)

        # The prompts are 0-indexed in the database, so we can just return the current
        # count as the new prompt index
        self._db.execute(
            "INSERT INTO prompt "
            "(round_id, player_id, prompt_number, prompt) "
            "VALUES (?, ?, ?, ?)",
            (round_id, player_id, player_prompt_count, prompt),
        )

        self._db.commit()

        return player_prompt_count + 1

    def player_finished_prompt_submission(self, code: str, player_id: int):
        return (
            self.player_prompt_count(code, player_id)
            >= constants.NUMBER_OF_PROMPTS_PER_USER
        )

    def all_prompts_submitted_for_round(self, code: str) -> bool:
        """
        Check that all users have submitted their prompts for the games current round
        :param code: the game code to check
        :return: True if all players have submitted their prompts, False otherwise
        """
        sql = (
            " SELECT (SELECT COUNT(*) from player where game_code = ?) * ? ="
            "(SELECT COUNT(*)"
            " FROM prompt"
            " INNER JOIN round ON round.id = prompt.round_id"
            " WHERE round.game_code = ?"
            " AND round.current = TRUE) as finished"
        )

        cursor: sqlite3.Cursor = self._db.cursor()
        cursor.execute(sql, (code, constants.NUMBER_OF_PROMPTS_PER_USER, code))
        return bool(cursor.fetchone()["finished"])

    def all_drawings_submitted_for_round(self, code: str) -> bool:
        """
        Check that all users have submitted their drawings for the games current round
        :param code: the game code to check
        :return: True if all players have submitted their prompts, False otherwise
        """
        sql = (
            " SELECT (SELECT COUNT(*) from player where game_code = ?) ="
            "(SELECT COUNT(*)"
            " FROM drawing"
            " INNER JOIN round ON round.id = drawing.round_id"
            " WHERE round.game_code = ?"
            " AND round.current = TRUE) as finished"
        )

        cursor: sqlite3.Cursor = self._db.cursor()
        cursor.execute(sql, (code, code))
        return bool(cursor.fetchone()["finished"])

    def get_clients_for_game(self, game_code) -> Iterable[WebClient]:
        cursor = self._db.cursor()
        cursor.execute("SELECT client_hash FROM player WHERE game_code=?", (game_code,))
        return (self._clients[row["client_hash"]] for row in cursor)

    def has_submitted_drawing(self, code: str, player_id: int):
        cursor: sqlite3.Cursor = self._db.cursor()
        return bool(
            cursor.execute(
                "SELECT 1 FROM drawing "
                "INNER JOIN round on drawing.round_id = round.id "
                "WHERE round.game_code=? AND drawing.player_id=? AND round.current = TRUE",
                (code, player_id),
            ).fetchone()
        )

    def add_drawing(
            self,
            round_id: int,
            player_id: int,
            sequence: int,
            prompt_1_id: int,
            prompt_2_id: int
    ):
        cursor: sqlite3.Cursor = self._db.cursor()
        cursor.execute(
            "INSERT INTO drawing (round_id, player_id, sequence) " "VALUES (?, ?, ?)",
            (round_id, player_id, sequence),
        )
        drawing_id: int = cursor.lastrowid

        for prompt_id in [prompt_1_id, prompt_2_id]:
            self._db.execute("UPDATE prompt SET drawing_id=? WHERE id=?", (drawing_id, prompt_id))

        self._db.commit()

    def player_finished_submission(self, code: str, player_id: int) -> bool:
        game_state = self.get_game_state(code)

        if game_state == GameState.SUBMIT_ATTRIBUTES:
            return self.player_finished_prompt_submission(code, player_id)

        if game_state == GameState.DRAW_PROMPTS:
            return self.has_submitted_drawing(code, player_id)

        # We don't really care that much about the value otherwise but return False for
        # consistency
        return False

    def get_current_round_drawings(self, game_code: str):
        round_id: int = self.get_current_round_id(game_code)

        cursor = self._db.cursor()
        cursor.execute(
            "SELECT id, player_id FROM drawing where round_id=?", (round_id,)
        )
        return [
            Drawing(row["id"], round_id, row["player_id"], row["sequence"], self._db)
            for row in cursor
        ]

    def get_drawing_prompts_for_player(self, player_id):
        cursor = self._db.cursor()
        cursor.execute(
            "SELECT prompt FROM prompt INNER JOIN drawing d on prompt.drawing_id = d.id WHERE d.player_id=?",
            (player_id,)
        )
        return [row["prompt"] for row in cursor]

    def update_drawings_sequence(self, drawings: List[Drawing]):
        self._db.executemany(
            "UPDATE drawing SET sequence=? WHERE round_id=? AND player_id=?",
            (
                (drawing.sequence, drawing.round_id, drawing.player_id)
                for drawing in drawings
            ),
        )
        self._db.commit()

    def _database_has_user(self, uuid: str) -> bool:
        cursor: sqlite3.Cursor = self._db.cursor()
        return bool(
            cursor.execute("SELECT uuid FROM user WHERE uuid=?", [uuid]).fetchone()
        )
