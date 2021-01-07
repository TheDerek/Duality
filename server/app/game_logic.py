"""Game logic more complicated than simple crud stuff"""
from typing import List
from random import shuffle

from app.store import Store, Player


def prepare_assign_prompts(store: Store, game_code: str):
    """Prepare the database for the assign prompts phase"""
    # Shuffle the drawings in the database
    drawings = store.get_current_round_drawings(game_code)
    shuffle(drawings)
    for index, drawing in enumerate(drawings):
        drawing.sequence = index

    store.update_drawings_sequence(drawings)
