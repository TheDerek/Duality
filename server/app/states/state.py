from abc import ABC, abstractmethod

from app.store import Store
from app.request_dispatcher import RequestDispatcher


class State(ABC):
    def __init__(self, store: Store, dispatcher: RequestDispatcher):
        self._store: Store = store
        self._dispatcher: RequestDispatcher = dispatcher

    @abstractmethod
    def on_enter(self, game_code: str):
        pass

    @abstractmethod
    def on_exit(self, game_code: str):
        pass
