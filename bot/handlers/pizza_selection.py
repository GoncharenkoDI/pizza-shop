import json

import bot.database_client
import bot.telegram_client
from bot.handlers.handler import Handler, HandlerStatus
from bot.pizza import build_pizza_size_keyboard, is_exits_pizza_type


class PizzaSelectionHandler(Handler):
    def can_handle(self, update: dict, state: str, order_data: dict) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_PIZZA_NAME":
            return False

        if "data" not in update["callback_query"]:
            return False

        callback_data = update["callback_query"]["data"]

        return is_exits_pizza_type(callback_data)

    def handle(self, update: dict, state: str, order_data: dict) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        pizza_type = update["callback_query"]["data"]
        order_data = {"pizza_type": pizza_type}
        bot.database_client.update_user_state(telegram_id, "WAIT_FOR_PIZZA_SIZE")
        bot.database_client.update_user_order_json(telegram_id, order_data)

        bot.telegram_client.answer_callback_query(update["callback_query"]["id"])
        bot.telegram_client.delete_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        bot.telegram_client.send_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text="Будь ласка, оберіть розмір піци.",
            reply_markup=json.dumps({"inline_keyboard": build_pizza_size_keyboard()}),
        )
        return HandlerStatus.STOP
