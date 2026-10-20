import datetime

from bot.dispatcher import Dispatcher
from bot.handlers.pizza_selection import PizzaSelectionHandler
from tests.mocks import Mock


def test_pizza_selection_execution():
    test_update = {
        "update_id": 366965252,
        "callback_query": {
            "id": "3291890577305615337",
            "from": {
                "id": 766453001,
                "is_bot": False,
                "first_name": "Дмитро",
                "last_name": "Гончаренко",
                "language_code": "ru",
            },
            "message": {
                "message_id": 340,
                "from": {
                    "id": 8669703310,
                    "is_bot": True,
                    "first_name": "Гончаренко Д.І. бот",
                    "username": "hdi_lesson_bot",
                },
                "chat": {
                    "id": 766453001,
                    "first_name": "Дмитро",
                    "last_name": "Гончаренко",
                    "type": "private",
                },
                "date": 1791383345,
                "text": "Будь ласка, оберіть Вашу піцу.",
                "reply_markup": {
                    "inline_keyboard": [
                        [
                            {"text": "Маргарита", "callback_data": "margherita"},
                            {"text": "Пеппероні", "callback_data": "pepperoni"},
                        ],
                        [
                            {"text": "Чотири сира", "callback_data": "four_cheeses"},
                            {"text": "Гавайська", "callback_data": "hawaiian"},
                        ],
                        [
                            {"text": "Куриця барбекю", "callback_data": "bbq_chicken"},
                            {"text": "М'ясна", "callback_data": "all_meet"},
                        ],
                        [{"text": "Вегетаріанська", "callback_data": "vegetarian"}],
                    ]
                },
            },
            "chat_instance": "-6286455501612302882",
            "data": "four_cheeses",
        },
    }

    get_user_called = False
    update_user_state_called = False
    update_user_order_json_called = False
    answer_callback_query_called = False
    delete_message_called = False
    send_message_called = False

    def get_user(telegram_id: int) -> dict:
        nonlocal get_user_called
        get_user_called = True
        assert telegram_id == 766453001
        return {
            "id": 1,  # int
            "telegram_id": 766453001,  # bigint
            "created_at": datetime.datetime(
                2026, 10, 19, 15, 30, 45, 123456
            ),  # timestamp without time zone
            "state": "WAIT_FOR_PIZZA_NAME",  # str
            "order_json": None,  # text - json str
        }

    # update_user_state(telegram_id, "WAIT_FOR_PIZZA_SIZE")
    def update_user_state(telegram_id: int, state: str) -> None:
        nonlocal update_user_state_called
        update_user_state_called = True
        assert telegram_id == 766453001  # update["callback_query"]["from"]["id"]
        assert state == "WAIT_FOR_PIZZA_SIZE"

    # update_user_order_json(telegram_id, order_data)
    def update_user_order_json(telegram_id: int, order_data: dict) -> None:
        nonlocal update_user_order_json_called
        update_user_order_json_called = True
        assert telegram_id == 766453001  # update["callback_query"]["from"]["id"]
        assert order_data == {
            "pizza_type": "four_cheeses"
        }  # pizza_type = update["callback_query"]["data"]

    # messenger.answer_callback_query(update["callback_query"]["id"])
    def answer_callback_query(callback_query_id: str) -> bool:
        nonlocal answer_callback_query_called
        answer_callback_query_called = True
        assert callback_query_id == "3291890577305615337"

    # messenger.delete_message(chat_id=update["callback_query"]["message"]["chat"]["id"], message_id=update["callback_query"]["message"]["message_id"],)
    def delete_message(chat_id: int, message_id: int) -> bool:
        nonlocal delete_message_called
        delete_message_called = True
        assert chat_id == 766453001
        assert message_id == 340

    # messenger.send_message(chat_id=update["callback_query"]["message"]["chat"]["id"], text="Будь ласка, оберіть розмір піци.",reply_markup=json.dumps({"inline_keyboard": build_pizza_size_keyboard()}),)
    def send_message(chat_id: int, text: str, **params) -> dict:
        nonlocal send_message_called
        send_message_called = True
        assert chat_id == 766453001
        assert text == "Будь ласка, оберіть розмір піци."

    mock_storage = Mock(
        {
            "update_user_state": update_user_state,
            "update_user_order_json": update_user_order_json,
            "get_user": get_user,  # Використовується в Dispatcher.dispatch
        }
    )

    mock_messenger = Mock(
        {
            "answer_callback_query": answer_callback_query,
            "delete_message": delete_message,
            "send_message": send_message,
        }
    )

    dispatcher = Dispatcher(mock_storage, mock_messenger)
    dispatcher.add_handlers(PizzaSelectionHandler())
    dispatcher.dispatch(test_update)

    assert get_user_called
    assert update_user_state_called
    assert update_user_order_json_called
    assert answer_callback_query_called
    assert delete_message_called
    assert send_message_called
