import json

import bot.database_client
import bot.telegram_client
from bot.handlers.handler import Handler, HandlerStatus
from bot.pizza import build_drinks_keyboard, is_exists_pizza_size


class SizeSelection(Handler):
    def can_handle(self, update: dict, state: str, order_data: dict) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_PIZZA_SIZE":
            return False

        if "data" not in update["callback_query"]:
            return False

        callback_data = update["callback_query"]["data"]

        return is_exists_pizza_size(callback_data)

    def handle(self, update: dict, state: str, order_data: dict) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        pizza_size = update["callback_query"]["data"]
        user_data = bot.database_client.get_user(telegram_id)
        order_data = json.loads(user_data["order_json"])
        order_data["pizza_size"] = pizza_size

        bot.database_client.update_user_state(telegram_id, "WAIT_FOR_DRINKS")
        bot.database_client.update_user_order_json(telegram_id, order_data)

        bot.telegram_client.answer_callback_query(update["callback_query"]["id"])
        bot.telegram_client.delete_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        bot.telegram_client.send_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text="Будь ласка, оберіть напій.",
            reply_markup=json.dumps({"inline_keyboard": build_drinks_keyboard()}),
        )
        return HandlerStatus.STOP
