from enum import Enum, auto
from app.user import WebClient


class ErrorType(Enum):
    LOBBY_ERROR = auto()
    WAITING_ROOM_ERROR = auto()
    PROMPT_SUBMISSION_ERROR = auto()
    DATABASE_ERROR = auto()


class RequestError(Exception):
    def __init__(self, exception_type: ErrorType, message: str):
        super().__init__(message)
        self._type: ErrorType = exception_type

    def get_error_response(self):
        return {"error": {"type": self._type.name, "userMessage": str(self)}}


class PromptError(RequestError):
    def __init__(self, message: str):
        super().__init__(ErrorType.PROMPT_SUBMISSION_ERROR, message)


class DatabaseError(RequestError):
    def __init__(self, message: str):
        super().__init__(ErrorType.DATABASE_ERROR, message)


class WaitingRoomError(RequestError):
    def __init__(self, message: str):
        super().__init__(ErrorType.WAITING_ROOM_ERROR, message)


class LobbyError(RequestError):
    def __init__(self, message: str):
        super().__init__(ErrorType.LOBBY_ERROR, message)
