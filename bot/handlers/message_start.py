import json

import bot.database_client
import bot.telegram_client
from bot.handlers.handler import Handler, HandlerStatus
from bot.pizza import build_pizza_type_keyboard


class MessageStart(Handler):
    def can_handle(self, update: dict, state: str, order_data: dict) -> bool:
        return (
            "message" in update
            and "text" in update["message"]
            and (
                update["message"]["text"] == "/start"
                or update["message"]["text"].lower() == "старт"
            )
        )

    def handle(self, update: dict, state: str, order_data: dict) -> HandlerStatus:
        telegram_id = update["message"]["from"]["id"]

        bot.database_client.clear_user_state(telegram_id)
        bot.database_client.update_user_state(telegram_id, "WAIT_FOR_PIZZA_NAME")

        bot.telegram_client.send_message(
            chat_id=update["message"]["chat"]["id"],
            text="🍕 Вітаю в магазині PIZZA SHOP.",
            reply_markup=json.dumps({"remove_keyboard": True}),
        )

        bot.telegram_client.send_message(
            chat_id=update["message"]["chat"]["id"],
            text="Будь ласка, оберіть Вашу піцу.",
            reply_markup=json.dumps({"inline_keyboard": build_pizza_type_keyboard()}),
        )

        return HandlerStatus.STOP
