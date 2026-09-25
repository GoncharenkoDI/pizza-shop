import json

from bot.dispatcher import Dispatcher
from bot.handlers.message_start import MessageStart
from tests.mocks import Mock


def test_message_start_execution():
    test_update = {
        "update_id": 366965026,
        "message": {
            "message_id": 6,
            "from": {
                "id": 766453001,
                "is_bot": False,
                "first_name": "Дмитро",
                "last_name": "Гончаренко",
                "language_code": "ru",
            },
            "chat": {
                "id": 766453001,
                "first_name": "Дмитро",
                "last_name": "Гончаренко",
                "type": "private",
            },
            "date": 1789224767,
            "text": "/start",
        },
    }

    clear_user_state_called = False
    update_user_state_called = False

    def clear_user_state(telegram_id: int) -> None:
        nonlocal clear_user_state_called
        clear_user_state_called = True
        assert telegram_id == 766453001

    def update_user_state(telegram_id: int, state: str) -> None:
        nonlocal update_user_state_called
        update_user_state_called = True
        assert telegram_id == 766453001
        assert state == "WAIT_FOR_PIZZA_NAME"

    def get_user(telegram_id: int) -> dict | None:
        assert telegram_id == 766453001
        return {"state": None, "order_json": json.dumps({})}

    mock_storage = Mock(
        {
            "clear_user_state": clear_user_state,
            "update_user_state": update_user_state,
            "get_user": get_user,
        }
    )

    send_message_calls = []

    def send_message(chat_id: int, text: str, **params) -> dict:
        assert chat_id == 766453001
        send_message_calls.append({"text": text})
        return {"ok": True}

    mock_messenger = Mock({"send_message": send_message})

    dispatcher = Dispatcher(mock_storage, mock_messenger)
    dispatcher.add_handlers(MessageStart())

    dispatcher.dispatch(test_update)

    assert clear_user_state_called
    assert update_user_state_called

    assert len(send_message_calls) == 2
    assert send_message_calls[0]["text"] == "🍕 Вітаю в магазині PIZZA SHOP."
    assert send_message_calls[1]["text"] == "Будь ласка, оберіть Вашу піцу."
