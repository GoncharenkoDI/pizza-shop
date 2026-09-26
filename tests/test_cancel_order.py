import json

from bot.dispatcher import Dispatcher
from bot.domain.pizza import get_drinks, get_pizza_size, get_pizza_type
from bot.handlers.cancel_order import CancelOrder
from tests.mocks import Mock


def test_cancel_order_execution():
    test_update = {
        "update_id": 366965213,
        "callback_query": {
            "id": "3291890575283026332",
            "from": {
                "id": 766453001,
                "is_bot": False,
                "first_name": "Дмитро",
                "last_name": "Гончаренко",
                "language_code": "ru",
            },
            "message": {
                "message_id": 284,
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
                "date": 1790319683,
                "text": "Ви обрали:\n                піцу - Пеппероні,\n                розмір - Середня (30 см.),\n                напій - Яблучний сік",
                "reply_markup": {
                    "inline_keyboard": [
                        [
                            {"text": "Підтвердити", "callback_data": "approval"},
                            {"text": "Відмова", "callback_data": "cancel"},
                        ]
                    ]
                },
            },
            "chat_instance": "-6286455501612302882",
            "data": "cancel",
        },
    }
    order_data = {
        "pizza_type": "margherita",
        "pizza_size": "size_small",
        "drink": "coca_cola",
    }

    clear_user_state_called = False
    answer_callback_query_called = False
    delete_message_called = False


    def clear_user_state(telegram_id: int) -> None:
        nonlocal clear_user_state_called
        clear_user_state_called = True
        assert telegram_id == 766453001

    def get_user(telegram_id: int) -> dict:  # Використовується в Dispatcher.dispatch
        assert telegram_id == 766453001
        # order_data - {"pizza_type": PIZZA_TYPE_key, "pizza_size": PIZZA_SIZE_key, "drink": DRINKS_key}
        nonlocal order_data
        return {
            "state": "WAIT_FOR_ORDER_APPROVAL",
            "order_json": json.dumps(order_data),
        }

    mock_storage = Mock(
        {
            "clear_user_state": clear_user_state,
            "get_user": get_user,
        }
    )

    send_message_calls = []

    def answer_callback_query(callback_query_id: str):
        assert callback_query_id == "3291890575283026332"
        nonlocal answer_callback_query_called
        answer_callback_query_called = True
        return True

    def delete_message(chat_id: int, message_id: int):
        assert chat_id == 766453001
        assert message_id ==  284
        nonlocal delete_message_called
        delete_message_called = True
        return True

    def send_message(chat_id: int, text: str, **params) -> dict:
        assert chat_id == 766453001
        send_message_calls.append({"text": text})
        return {"ok": True}

    mock_messenger = Mock(
        {
            "send_message": send_message,
            "delete_message": delete_message,
            "answer_callback_query": answer_callback_query,
        }
    )

    dispatcher = Dispatcher(mock_storage, mock_messenger)
    dispatcher.add_handlers(CancelOrder())

    dispatcher.dispatch(test_update)

    assert clear_user_state_called
    assert answer_callback_query_called
    assert delete_message_called

    assert len(send_message_calls) == 1
   
    text = f"""
            Ви обрали:
            піцу - {get_pizza_type(order_data["pizza_type"])},
            розмір - {get_pizza_size(order_data["pizza_size"])},
            напій - {get_drinks(order_data["drink"])}
            На жаль Ви відмовились від замовлення!
        """
    
    assert send_message_calls[0]["text"] == text
