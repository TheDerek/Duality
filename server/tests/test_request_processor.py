import pytest

from unittest.mock import MagicMock, patch, AsyncMock

from app.request_processor import on_create_game, join_game


@pytest.fixture()
def mock_dispatcher():
    with patch("app.request_processor.dispatcher") as dispatcher:
        dispatcher.add_to_message_queue = AsyncMock()
        yield dispatcher


@patch("app.request_processor.store")
@pytest.mark.asyncio
async def test_create_game(store, mock_dispatcher):
    mock_game = store.create_game.return_value
    client = MagicMock()

    request = {
        "playerName": "John"
    }

    await on_create_game(client, request)

    mock_dispatcher.add_to_message_queue.assert_called_with(
        client,
        {
            "joinGame": {
                "gameCode": mock_game.code,
                "players": mock_game.get_players_response.return_value,
                "admin": True
            }
        }
    )


@patch("app.request_processor.store")
@pytest.mark.asyncio
async def test_join_valid_game(store, mock_dispatcher):
    mock_dispatcher.add_to_message_queue = AsyncMock()

    mock_game = store.get_game.return_value
    mock_user = store.get_user.return_value
    store.add_player_to_game.return_value = mock_user, mock_game

    client = MagicMock()
    game_code = MagicMock()

    request = {
        "gameCode": game_code,
        "playerName":  mock_user.name
    }

    await join_game(client, request)

    store.get_user.assert_called_with(client)
    store.modify_user.assert_called_with(mock_user, name=mock_user.name)

    mock_dispatcher.add_to_message_queue.assert_called_with(
        client,
        {
            "joinGame": {
                "gameCode": game_code,
                "players": mock_game.get_players_response.return_value,
                "admin": False
            }
        }
    )