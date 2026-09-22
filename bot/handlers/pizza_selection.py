import json

from bot.domain.messenger import Messenger
from bot.domain.pizza import build_pizza_size_keyboard, is_exits_pizza_type
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class PizzaSelectionHandler(Handler):
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

        if state != "WAIT_FOR_PIZZA_NAME":
            return False

        if "data" not in update["callback_query"]:
            return False

        callback_data = update["callback_query"]["data"]

        return is_exits_pizza_type(callback_data)

    def handle(
        self,
        update: dict,
        state: str,
        order_data: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        pizza_type = update["callback_query"]["data"]
        order_data = {"pizza_type": pizza_type}
        storage.update_user_state(telegram_id, "WAIT_FOR_PIZZA_SIZE")
        storage.update_user_order_json(telegram_id, order_data)

        messenger.answer_callback_query(update["callback_query"]["id"])
        messenger.delete_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        messenger.send_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text="Будь ласка, оберіть розмір піци.",
            reply_markup=json.dumps({"inline_keyboard": build_pizza_size_keyboard()}),
        )
        return HandlerStatus.STOP
