import json

from bot.dispatcher import Dispatcher
from bot.domain.pizza import get_drinks, get_pizza_size, get_pizza_type
from bot.handlers.drink_selection import DrinkSelection
from tests.mocks import Mock


def test_drink_selection_execution():
    test_update = {
        "update_id": 366965259,
        "callback_query": {
            "id": "3291890576422690968",
            "from": {
                "id": 766453001,
                "is_bot": False,
                "first_name": "Дмитро",
                "last_name": "Гончаренко",
                "language_code": "ru",
            },
            "message": {
                "message_id": 349,
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
                "date": 1791624132,
                "text": "Будь ласка, оберіть напій.",
                "reply_markup": {
                    "inline_keyboard": [
                        [
                            {"text": "Кока-кола", "callback_data": "coca_cola"},
                            {"text": "Пепсі", "callback_data": "pepsi"},
                        ],
                        [
                            {"text": "Апельсиновий сік", "callback_data": "orange_jus"},
                            {"text": "Яблучний сік", "callback_data": "apple_jus"},
                        ],
                        [{"text": "Без напою", "callback_data": "no_drinks"}],
                    ]
                },
            },
            "chat_instance": "-6286455501612302882",
            "data": "no_drinks",
        },
    }
    order_data = {
        "pizza_type": "margherita",
        "pizza_size": "size_small",
    }

    update_user_state_called = False
    update_user_order_json_called = False
    answer_callback_query_called = False
    delete_message_called = False
    send_message_called = False

    def update_user_state(telegram_id: int, state: str) -> None:
        nonlocal update_user_state_called
        update_user_state_called = True
        assert telegram_id == 766453001
        assert state == "WAIT_FOR_ORDER_APPROVAL"

    def update_user_order_json(telegram_id: int, order_data: dict) -> None:
        nonlocal update_user_order_json_called
        update_user_order_json_called = True
        assert telegram_id == 766453001
        drink = order_data.get("drink")
        assert drink == "no_drinks"

    def get_user(telegram_id: int) -> dict:
        assert telegram_id == 766453001
        # order_data - {"pizza_type": PIZZA_TYPE_key, "pizza_size": PIZZA_SIZE_key, "drink": DRINKS_key}
        nonlocal order_data
        return {
            "state": "WAIT_FOR_DRINKS",
            "order_json": json.dumps(order_data),
        }

    mock_storage = Mock(
        {
            "update_user_state": update_user_state,
            "update_user_order_json": update_user_order_json,
            "get_user": get_user,  # Використовується в Dispatcher.dispatch
        }
    )

    def send_message(chat_id: int, text: str, **params) -> dict:
        assert chat_id == 766453001
        assert text == f"""
                Ви обрали:
                піцу - {get_pizza_type(order_data["pizza_type"])},
                розмір - {get_pizza_size(order_data["pizza_size"])},
                напій - {get_drinks("no_drinks")} 
            """
        nonlocal send_message_called
        send_message_called = True

    def delete_message(chat_id: int, message_id: int) -> bool:
        assert chat_id == 766453001
        assert message_id == 349
        nonlocal delete_message_called
        delete_message_called = True

    def answer_callback_query(callback_query_id: str) -> bool:
        assert callback_query_id == "3291890576422690968"
        nonlocal answer_callback_query_called
        answer_callback_query_called = True
        return True

    mock_messenger = Mock(
        {
            "send_message": send_message,
            "delete_message": delete_message,
            "answer_callback_query": answer_callback_query,
        }
    )

    dispatcher = Dispatcher(mock_storage, mock_messenger)
    dispatcher.add_handlers(DrinkSelection())
    dispatcher.dispatch(test_update)

    assert update_user_state_called
    assert update_user_order_json_called
    assert answer_callback_query_called
    assert delete_message_called
    assert send_message_called
