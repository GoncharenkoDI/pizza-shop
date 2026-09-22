import json

from bot.domain.messenger import Messenger
from bot.domain.pizza import (
    get_drinks,
    get_pizza_size,
    get_pizza_type,
    is_exists_drinks,
)
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class DrinkSelection(Handler):
    def can_handle(
        self,
        update: dict,
        state: str,
        order_data: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_DRINKS":
            return False

        if "data" not in update["callback_query"]:
            return False

        callback_data = update["callback_query"]["data"]

        return is_exists_drinks(callback_data)

    def handle(
        self,
        update: dict,
        state: str,
        order_data: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        drink = update["callback_query"]["data"]
        user_data = storage.get_user(telegram_id)
        order_data = json.loads(user_data["order_json"])
        order_data["drink"] = drink

        storage.update_user_state(telegram_id, "WAIT_FOR_ORDER_APPROVAL")
        storage.update_user_order_json(telegram_id, order_data)

        messenger.answer_callback_query(update["callback_query"]["id"])
        messenger.delete_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        messenger.send_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text=f"""
                Ви обрали:
                піцу - {get_pizza_type(order_data["pizza_type"])},
                розмір - {get_pizza_size(order_data["pizza_size"])},
                напій - {get_drinks(order_data["drink"])} 
            """,
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {"text": "Підтвердити", "callback_data": "approval"},
                            {"text": "Відмова", "callback_data": "cancel"},
                        ]
                    ]
                }
            ),
        )
        return HandlerStatus.STOP
