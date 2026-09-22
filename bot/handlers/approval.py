import json

import bot.database_client
import bot.telegram_client
from bot.handlers.handler import Handler, HandlerStatus
from bot.pizza import get_drinks, get_pizza_size, get_pizza_type


class Approval(Handler):
    def can_handle(self, update: dict, state: str, order_data: dict) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_ORDER_APPROVAL":
            return False

        if "data" not in update["callback_query"]:
            return False

        callback_data = update["callback_query"]["data"]

        return callback_data in ["approval", "cancel"]

    def handle(self, update: dict, state: str, order_data: dict) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        is_approval = update["callback_query"]["data"] == "approval"
        user_data = bot.database_client.get_user(telegram_id)
        order_data = json.loads(user_data["order_json"])

        bot.database_client.clear_user_state(telegram_id)

        bot.telegram_client.answer_callback_query(update["callback_query"]["id"])
        bot.telegram_client.delete_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        message_text = ""
        if is_approval:
            message_text = f"""
                Ви обрали:
                піцу - {get_pizza_type(order_data["pizza_type"])},
                розмір - {get_pizza_size(order_data["pizza_size"])},
                напій - {get_drinks(order_data["drink"])}
                Ваше замовлення вже в дорозі!
            """

        bot.telegram_client.send_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text=message_text,
            reply_markup=json.dumps(
                {
                    "keyboard": [
                        [
                            {"text": "Старт"},
                        ]
                    ],
                    "resize_keyboard": True,
                }
            ),
        )
        return HandlerStatus.STOP
