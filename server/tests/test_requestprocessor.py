import pytest

from unittest.mock import MagicMock, patch, AsyncMock

from app.request_processor import on_create_game


@patch("app.request_processor.store")
@patch("app.request_processor.dispatcher")
@pytest.mark.asyncio
async def test_create_game(dispatcher, store):
    dispatcher.add_to_message_queue = AsyncMock()

    mock_game = MagicMock()

    mock_game_code = MagicMock()
    mock_game.code = mock_game_code

    mock_players_response = MagicMock()
    mock_game.get_players_response = MagicMock(return_value=mock_players_response)

    store.create_game = MagicMock(return_value=mock_game)

    client = MagicMock()

    request = {
        "playerName": "John"
    }

    await on_create_game(client, request)

    dispatcher.add_to_message_queue.assert_called_with(
        client,
        {
            "joinGame": {
                "gameCode": mock_game_code,
                "players": mock_players_response,
                "admin": True
            }
        }
    )