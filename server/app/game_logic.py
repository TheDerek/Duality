"""Game logic more complicated than simple crud stuff"""
from functools import reduce
from typing import List
from random import shuffle

from app import constants
from app.store import Store, Player, Prompt


def prepare_assign_prompts(store: Store, game_code: str):
    """Prepare the database for the assign prompts phase"""
    pass
    # Shuffle the drawings in the database
    # drawings = store.get_current_round_drawings(game_code)
    # shuffle(drawings)
    # for index, drawing in enumerate(drawings):
    #     drawing.sequence = index
    #
    # store.update_drawings_sequence(drawings)


def prepare_draw_prompts(store: Store, game_code: str):
    """Prepare the the drawing prompts phase"""
    prompts: List[Prompt] = store.get_prompts(game_code)
    players: List[Player] = store.get_players(game_code)
    round_id: int = store.get_current_round_id(game_code)

    shuffle(prompts)
    shuffle(players)

    # Generate a drawing for each player with two prompts
    for index, player in enumerate(players):
        drawing_prompts: List[Prompt] = _get_drawing_prompts(player, prompts)
        store.add_drawing(
            round_id,
            player.id_,
            index,
            drawing_prompts[0].id_,
            drawing_prompts[1].id_,
            index == 0,
        )


async def prepare_display_scores(store: Store, game_code: str):
    pass


def _get_drawing_prompts(player: Player, prompts: List[Prompt]) -> List[Prompt]:
    drawing_prompts: List[Prompt] = []
    drawing_prompts_player_ids = set()
    prompts_copy = list(prompts)

    # If we only have two prompts left then we have to return both of them even if they
    # were both submitted by the same person. This is due to a flaw in the code below that
    # sometimes results in the last two prompts left being from the same person
    if len(prompts) == constants.NUMBER_OF_PROMPTS_PER_USER:
        prompts.clear()
        return prompts_copy

    for prompt in prompts_copy:
        if (prompt.player_id != player.id_) and (
            prompt.player_id not in drawing_prompts_player_ids
        ):
            drawing_prompts_player_ids.add(prompt.player_id)
            drawing_prompts.append(prompt)
            prompts.remove(prompt)

        if len(drawing_prompts) == constants.NUMBER_OF_PROMPTS_PER_USER:
            return drawing_prompts

    return drawing_prompts
