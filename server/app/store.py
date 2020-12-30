import random
import string
import sqlite3

from uuid import uuid4
from typing import Dict, Optional, Set

from app.user import WebClient


class Store:
    __sentinel = object()

    def __init__(self):
        self._users: Dict[WebClient, Optional[str]] = {}

        # Disconnected users associated by their uuid
        self._disconnected_users: Set[str] = set()

        self._db: sqlite3.Connection = sqlite3.connect(
            "/home/derek/git/boss-fight/database/db.sqlite3"
        )

    def __exit__(self, exc_type, exc_value, traceback):
        self._db.close()

    def add_client(self, client: WebClient):
        print("Adding client")
        self._users[client] = None

    def remove_client(self, client):
        print("Removing client")
        uuid: str = self._users.pop(client)

        if uuid:
            self._disconnected_users.add(uuid)

    def create_game(self, admin_uuid: str, admin_name: str) -> str:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))

        # Create the game
        self._db.execute(
            "INSERT INTO game (code) VALUES (?)",
            [code]
        )

        # Add the user to the game
        self._db.execute(
            "INSERT INTO game_user (game_code, user_uuid, admin, name)"
            "VALUES (?, ?, ?, ?)",
            (code, admin_uuid, True, admin_name)
        )

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

    def _database_has_user(self, uuid: str) -> bool:
        cursor: sqlite3.Cursor = self._db.cursor()
        return bool(
            cursor.execute("SELECT uuid FROM user WHERE uuid=?", [uuid]).fetchone()
        )
