from bot.dispatcher import Dispatcher
from bot.handlers.update_database_logger import UpdateDataBaseLogger
from tests.mocks import Mock


def test_update_database_logger_execution():
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
            "text": "Test message",
        },
    }
    persist_update_called = False

    def persist_update(update: dict) -> None:
        nonlocal persist_update_called
        persist_update_called = True
        assert update == test_update

    def get_user(telegram_id: int) -> dict | None:
        assert telegram_id == 766453001
        return None

    mock_storage = Mock(
        {
            "persist_update": persist_update,
            "get_user": get_user,
        }
    )

    mock_messenger = Mock({})

    dispatcher = Dispatcher(mock_storage, mock_messenger)

    dispatcher.add_handlers(UpdateDataBaseLogger())
    dispatcher.dispatch(test_update)

    assert persist_update_called
