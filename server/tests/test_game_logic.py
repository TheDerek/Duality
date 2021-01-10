from unittest.mock import MagicMock

from app.store import Player
from app import game_logic


def get_mock_player(id_):
    player = MagicMock()
    player.id_ = id_
    return player


def get_mock_prompt(id_, player_id):
    prompt = MagicMock()
    prompt.id_ = id_
    prompt.player_id = player_id
    return prompt


def test_get_drawing_prompts():
    players = [get_mock_player(i) for i in range(3)]
    prompts = [get_mock_prompt(i, int(i/2)) for i in range(6)]

    drawing_prompts = game_logic.get_drawing_prompts(players[0], prompts)

    assert len(prompts) == 4
    assert len(drawing_prompts) == 2

    assert drawing_prompts[0] not in prompts
    assert drawing_prompts[1] not in prompts

    assert drawing_prompts[0].id_ == 2
    assert drawing_prompts[0].player_id == 1

    assert drawing_prompts[1].id_ == 4
    assert drawing_prompts[1].player_id == 2


def test_get_drawing_prompts_all():
    players = [get_mock_player(i) for i in range(3)]
    prompts = [get_mock_prompt(i, int(i/2)) for i in range(6)]

    for player in players:
        drawing_prompts = game_logic.get_drawing_prompts(player, prompts)
        # assert len(prompts) == 4
        # assert len(drawing_prompts) == 2

        assert drawing_prompts[0] not in prompts
        assert drawing_prompts[1] not in prompts

        print([(f"{prompt.id_=}", f"{prompt.player_id=}") for prompt in drawing_prompts])
