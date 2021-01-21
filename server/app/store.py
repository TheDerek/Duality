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
        id_: int,
        round_id: int,
        player_id: int,
        sequence: int,
        current: bool,
        client: sqlite3.Connection,
    ):
        self.id_: int = id_
        self.round_id: int = round_id
        self.player_id: int = player_id
        self.sequence: int = sequence
        self.current: bool = current
        self._db: sqlite3.Connection = client

    @property
    def drawing(self):
        cursor = self._db.cursor()
        cursor.execute("SELECT drawing from drawing WHERE id=?", (self.id_,))
        return cursor.fetchone()["drawing"]


@dataclass()
class Prompt:
    id_: int
    player_id: int
    round_id: int
    prompt_number: int
    prompt: str
    drawing_id: Optional[int]
    enabled: bool


@dataclass()
class AssignedPrompt:
    player_name: str
    prompt: str
    correct: bool


@dataclass()
class Score:
    previous: int
    current_round: int

    @property
    def total(self):
        return self.previous + self.current_round


class GameState(Enum):
    WAITING_ROOM = auto()
    SUBMIT_PROMPTS = auto()
    DRAW_PROMPTS = auto()
    WAITING_FOR_PLAYERS = auto()
    ASSIGN_PROMPTS = auto()
    DISPLAY_RESULTS = auto()
    DISPLAY_SCORES = auto()


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
        new_number = old_number + 1 if old_number is not None else 0

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

        sql = (
            "SELECT prompt, prompt_number, id as id_, drawing_id, round_id, player_id, "
            "NOT EXISTS(SELECT 1 FROM assigned_prompt WHERE assigned_prompt.prompt_id=prompt.id) as enabled "
            "FROM prompt where round_id=?"
        )
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
            " WHERE round.game_code=? AND drawing.drawing IS NOT NULL"
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
                "WHERE round.game_code=? AND drawing.player_id=? "
                "AND round.current = TRUE AND drawing.drawing IS NOT NULL",
                (code, player_id),
            ).fetchone()
        )

    def add_drawing(
        self,
        round_id: int,
        player_id: int,
        sequence: int,
        prompt_1_id: int,
        prompt_2_id: int,
        current: bool,
    ):
        cursor: sqlite3.Cursor = self._db.cursor()
        cursor.execute(
            "INSERT INTO drawing (round_id, player_id, sequence, current) "
            "VALUES (?, ?, ?, ?)",
            (round_id, player_id, sequence, current),
        )
        drawing_id: int = cursor.lastrowid

        for prompt_id in [prompt_1_id, prompt_2_id]:
            self._db.execute(
                "UPDATE prompt SET drawing_id=? WHERE id=?", (drawing_id, prompt_id)
            )

        self._db.commit()

    def set_player_drawing_image(self, code: str, player_id: int, drawing: str):
        round_id: int = self.get_current_round_id(code)
        self._db.execute(
            "UPDATE drawing SET drawing=? WHERE round_id=? AND player_id=?",
            (drawing, round_id, player_id),
        )
        self._db.commit()

    def player_finished_submission(self, code: str, player_id: int) -> bool:
        game_state = self.get_game_state(code)

        if game_state == GameState.SUBMIT_PROMPTS:
            return self.player_finished_prompt_submission(code, player_id)

        if game_state == GameState.DRAW_PROMPTS:
            return self.has_submitted_drawing(code, player_id)

        if game_state == GameState.ASSIGN_PROMPTS:
            return self.player_finished_assigning_prompts(code, player_id)

        # We don't really care that much about the value otherwise but return False for
        # consistency
        return False

    def get_current_round_drawings(self, game_code: str):
        round_id: int = self.get_current_round_id(game_code)

        cursor = self._db.cursor()
        cursor.execute(
            "SELECT id, player_id, sequence, current FROM drawing where round_id=?",
            (round_id,),
        )
        return [
            Drawing(
                row["id"],
                round_id,
                row["player_id"],
                row["sequence"],
                row["current"],
                self._db,
            )
            for row in cursor
        ]

    def get_drawing_prompts_for_player(self, player_id):
        cursor = self._db.cursor()
        cursor.execute(
            "SELECT prompt FROM prompt INNER JOIN drawing d on prompt.drawing_id = d.id WHERE d.player_id=?",
            (player_id,),
        )
        return [row["prompt"] for row in cursor]

    def update_drawings_sequence(self, drawings: List[Drawing]):
        self._db.executemany(
            "UPDATE drawing SET sequence=? AND current=? WHERE round_id=? AND player_id=?",
            (
                (drawing.sequence, drawing.current, drawing.round_id, drawing.player_id)
                for drawing in drawings
            ),
        )
        self._db.commit()

    def get_current_drawing(self, game_code) -> Optional[Drawing]:
        round_id: int = self.get_current_round_id(game_code)

        cursor = self._db.cursor()
        cursor.execute(
            "SELECT id, player_id, sequence, current FROM drawing where round_id=? and current=TRUE",
            (round_id,),
        )
        row = cursor.fetchone()
        if row:
            return Drawing(
                row["id"],
                round_id,
                row["player_id"],
                row["sequence"],
                row["current"],
                self._db,
            )
        else:
            return None

    def get_current_drawing_image(self, game_code):
        drawing: Drawing = self.get_current_drawing(game_code)

        if drawing:
            return drawing.drawing
        else:
            return None

    def player_finished_assigning_prompts(self, game_code, player_id):
        drawing: Drawing = self.get_current_drawing(game_code)

        cursor = self._db.cursor()
        cursor.execute(
            "SELECT 1 FROM assigned_prompt WHERE player_id=? AND drawing_id=?",
            (player_id, drawing.id_),
        )
        return bool(cursor.fetchone())

    def player_has_prompt_for_current_round(self, player_id, prompt):
        cursor = self._db.cursor()
        cursor.execute(
            "SELECT 1 FROM player, round, prompt "
            "WHERE player.id=? AND round.game_code=player.game_code AND round.current=TRUE "
            "AND prompt.round_id=round.id AND prompt.prompt=?",
            (player_id, prompt),
        )
        return bool(cursor.fetchone())

    def assign_prompt_to_current_image(
        self, game_code: str, player_id: int, prompt: str
    ):
        if self.player_finished_submission(game_code, player_id):
            raise PromptError("Player has already assigned a prompt for this drawing")

        if prompt and not self.player_has_prompt_for_current_round(player_id, prompt):
            raise PromptError("Player does not have this prompt")

        if prompt:
            self._db.execute(
                "INSERT INTO assigned_prompt (drawing_id, prompt_id, player_id) "
                "SELECT drawing.id, prompt.id, player.id "
                "FROM player, round, drawing, prompt "
                "WHERE player.id=? AND round.game_code=player.game_code AND round.current=TRUE "
                "AND drawing.round_id=round.id AND drawing.current=TRUE AND prompt.round_id=round.id "
                "AND prompt.prompt=?",
                (player_id, prompt),
            )
        else:
            self._db.execute(
                "INSERT INTO assigned_prompt (drawing_id, prompt_id, player_id) "
                "SELECT drawing.id, NULL, player.id "
                "FROM player, round, drawing "
                "WHERE player.id=? AND round.game_code=player.game_code AND round.current=TRUE "
                "AND drawing.round_id=round.id AND drawing.current=TRUE",
                (player_id,),
            )

        self._db.commit()

    def prompts_assigned_for_current_round(self, game_code):
        cursor: sqlite3.Cursor = self._db.cursor()
        cursor.execute(
            "SELECT (SELECT COUNT(1) FROM round, drawing, assigned_prompt "
            "WHERE round.game_code=? AND round.current=TRUE AND drawing.round_id=round.id AND drawing.current = TRUE "
            "AND assigned_prompt.drawing_id=drawing.id) "
            "= (SELECT COUNT(1) from player WHERE game_code=?) as finished",
            (game_code, game_code),
        )
        return cursor.fetchone()["finished"]

    def get_assigned_prompts(self, game_code: str) -> List[AssignedPrompt]:
        """
        Fetch the prompts assigned to the current rounds current drawing for the given game code
        """
        cursor: sqlite3.Cursor = self._db.cursor()
        cursor.execute(
            """
            SELECT
                 player.name as player_name,
                 prompt.prompt,
                 prompt.drawing_id=assigned_prompt.drawing_id as correct
            FROM
                 round, prompt, drawing, assigned_prompt, player
            WHERE
                  round.game_code=? AND
                  round.current=TRUE AND
                  prompt.round_id=round.id AND
                  prompt.player_id=player.id AND
                  drawing.round_id=round.id AND
                  drawing.current=TRUE AND
                  assigned_prompt.prompt_id = prompt.id AND
                  assigned_prompt.drawing_id=drawing.id
            """,
            (game_code,),
        )
        return [AssignedPrompt(**row) for row in cursor]

    def next_drawing(self, game_code):
        """Update the database to set the next drawing in the sequence as the current drawing"""
        drawing: Drawing = self.get_current_drawing(game_code)

        # Remove current from the current drawing
        self._db.execute(
            """
            UPDATE drawing
            SET current=0
            WHERE round_id = (
                SELECT round_id
                FROM round
                WHERE round.game_code = ?
                  AND round.current = TRUE
            )
              AND drawing.current = 1
            """,
            (game_code,)
        )

        # Set the next drawing in line as the current drawing
        self._db.execute(
            """
            UPDATE drawing
            SET current=1
            WHERE round_id = (
                SELECT round_id
                FROM round
                WHERE round.game_code = ?
                  AND round.current = TRUE
            )
              AND drawing.sequence = ? + 1
            """,
            (game_code, drawing.sequence)
        )

        self._db.commit()

    def all_results_finished(self, game_code):
        """Return True if all drawings have been assigned prompts and all results
        thereof have been displayed"""
        cursor = self._db.cursor()
        cursor.execute(
            """
            SELECT 1 FROM round, drawing
            WHERE round.game_code = ?
              AND round.current = TRUE
              AND drawing.round_id = round.id
              AND drawing.sequence > (
                  SELECT sequence FROM drawing
                  WHERE round.game_code = ?
                    AND round.current = TRUE
                    AND drawing.round_id = round.id
                    AND drawing.current = TRUE)
            LIMIT 1
            """,
            (game_code, game_code)
        )

        drawings_are_left = bool(cursor.fetchone())
        return not drawings_are_left

    def get_score(self, player_id: int) -> Score:
        cursor = self._db.cursor()
        cursor.execute(
            "SELECT round_number, score FROM scores WHERE player_id=? ORDER BY round_number",
            (player_id,)
        )

        rows = list(cursor.fetchall())
        previous_score = sum(row["score"] for row in rows[:-1])
        current_round_score = rows[-1]["score"]

        return Score(previous_score, current_round_score)

    def _database_has_user(self, uuid: str) -> bool:
        cursor: sqlite3.Cursor = self._db.cursor()
        return bool(
            cursor.execute("SELECT uuid FROM user WHERE uuid=?", [uuid]).fetchone()
        )
