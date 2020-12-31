import random
import string
import sqlite3
from collections import defaultdict

from enum import Enum, auto
from uuid import uuid4
from typing import Dict, Optional, Set, List
from dataclasses import dataclass

from websockets.server import WebSocketServerProtocol as WebClient
from exceptions import DatabaseError


@dataclass()
class Player:
    uuid: str
    game_code: str
    name: str
    admin: bool
    client: Optional[WebClient]


class GameState(Enum):
    WAITING_ROOM = auto()
    SUBMIT_ATTRIBUTES = auto()


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
        uuid: str = self._users.pop(client)
        del self._clients[hash(client)]

    def add_user_to_game(
        self,
        client: WebClient,
        user_uuid: str,
        game_code: str,
        user_name: str,
        admin=False,
        commit=True,
    ) -> Player:
        # Add the user to the game
        self._db.execute(
            "INSERT INTO game_user (game_code, user_uuid, client_hash, admin, name)"
            "VALUES (?, ?, ?, ?, ?)",
            (game_code, user_uuid, hash(client), admin, user_name),
        )

        if commit:
            self._db.commit()

        return Player(
            uuid=user_uuid,
            game_code=game_code,
            name=user_name,
            admin=admin,
            client=client,
        )

    def create_game(self, client: WebClient, admin_uuid: str, admin_name: str) -> str:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))

        # Create the game
        self._db.execute("INSERT INTO game (code) VALUES (?)", [code])

        # Add the first user (also the admin) to the game
        self.add_user_to_game(
            client, admin_uuid, code, admin_name, admin=True, commit=False
        )

        # Write changes to db
        self._db.commit()

        return code

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

    def is_admin_of_game(self, user_uuid: str, game_code: str) -> bool:
        cursor: sqlite3.Cursor = self._db.cursor()
        return bool(
            cursor.execute(
                "SELECT admin FROM game_user WHERE user_uuid=? and game_code=?",
                [user_uuid, game_code],
            ).fetchone()["admin"]
        )

    def get_game_state(self, game_code: str) -> str:
        cursor: sqlite3.Cursor = self._db.cursor()
        return cursor.execute(
            "SELECT state FROM game WHERE code=?", [game_code],
        ).fetchone()["state"]

    def get_player(self, game_code: str, user_uuid: str) -> Player:
        cursor: sqlite3.Cursor = self._db.cursor()
        db_player = cursor.execute(
            "SELECT name, admin, client_hash FROM game_user "
            "WHERE game_code=? and user_uuid=?",
            [game_code, user_uuid],
        ).fetchone()

        if not db_player:
            raise DatabaseError(f"User {user_uuid} is not in game {user_uuid}")

        return Player(
            uuid=user_uuid,
            game_code=game_code,
            name=db_player["name"],
            admin=bool(db_player["admin"]),
            client=self._clients[db_player["client_hash"]],
        )

    def get_players(self, game_code) -> List[Player]:
        cursor: sqlite3.Cursor = self._db.cursor()
        db_players = cursor.execute(
            "SELECT name, admin, user_uuid, client_hash FROM game_user WHERE game_code=?",
            [game_code],
        )

        return [
            Player(
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
                "SELECT user_uuid FROM game_user WHERE user_uuid=? and game_code=?",
                [uuid, code],
            ).fetchone()
            is not None
        )

    def update_player_client(self, uuid: str, code: str, client: WebClient):
        self._db.execute(
            "UPDATE game_user SET client_hash=? WHERE user_uuid=? and game_code=?",
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
                "SELECT name FROM game_user WHERE name=? and game_code=?",
                [name, code]
            ).fetchone()
        )

    def _database_has_user(self, uuid: str) -> bool:
        cursor: sqlite3.Cursor = self._db.cursor()
        return bool(
            cursor.execute("SELECT uuid FROM user WHERE uuid=?", [uuid]).fetchone()
        )
