from bot.dispatcher import Dispatcher
from bot.handlers.ensure_user_exists import EnsureUserExists
from tests.mocks import Mock


def test_ensure_user_exists_execution():
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

    ensure_user_exists_called = False

    def ensure_user_exists(telegram_id: int) -> None:
        # telegram_id = update["message"]["from"]["id"]
        assert telegram_id == 766453001
        nonlocal ensure_user_exists_called
        ensure_user_exists_called = True

    def get_user(telegram_id: int) -> dict:
        # update["callback_query"]["from"]["id"] or update["message"]["from"]["id"]
        assert telegram_id == 766453001
        return {
            "state": "WAIT_FOR_DRINKS",
            "order_json": "{}",
        }

    mock_storage = Mock(
        {
            "ensure_user_exists": ensure_user_exists,
            "get_user": get_user,  # Використовується в Dispatcher.dispatch
        }
    )

    mock_messenger = Mock({})

    dispatcher = Dispatcher(mock_storage, mock_messenger)
    dispatcher.add_handlers(EnsureUserExists())
    dispatcher.dispatch(test_update)

    assert ensure_user_exists_called
