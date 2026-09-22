import json

import bot.database_client
import bot.telegram_client
from bot.handlers.handler import Handler, HandlerStatus
from bot.pizza import get_drinks, get_pizza_size, get_pizza_type, is_exists_drinks


class DrinkSelection(Handler):
    def can_handle(self, update: dict, state: str, order_data: dict) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_DRINKS":
            return False

        if "data" not in update["callback_query"]:
            return False

        callback_data = update["callback_query"]["data"]

        return is_exists_drinks(callback_data)

    def handle(self, update: dict, state: str, order_data: dict) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        drink = update["callback_query"]["data"]
        user_data = bot.database_client.get_user(telegram_id)
        order_data = json.loads(user_data["order_json"])
        order_data["drink"] = drink

        bot.database_client.update_user_state(telegram_id, "WAIT_FOR_ORDER_APPROVAL")
        bot.database_client.update_user_order_json(telegram_id, order_data)

        bot.telegram_client.answer_callback_query(update["callback_query"]["id"])
        bot.telegram_client.delete_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        bot.telegram_client.send_message(
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
