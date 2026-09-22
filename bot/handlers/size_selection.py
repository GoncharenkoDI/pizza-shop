import json

from bot.domain.messenger import Messenger
from bot.domain.pizza import build_drinks_keyboard, is_exists_pizza_size
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class SizeSelection(Handler):
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

        if state != "WAIT_FOR_PIZZA_SIZE":
            return False

        if "data" not in update["callback_query"]:
            return False

        callback_data = update["callback_query"]["data"]

        return is_exists_pizza_size(callback_data)

    def handle(
        self,
        update: dict,
        state: str,
        order_data: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        pizza_size = update["callback_query"]["data"]
        user_data = storage.get_user(telegram_id)
        order_data = json.loads(user_data["order_json"])
        order_data["pizza_size"] = pizza_size

        storage.update_user_state(telegram_id, "WAIT_FOR_DRINKS")
        storage.update_user_order_json(telegram_id, order_data)

        messenger.answer_callback_query(update["callback_query"]["id"])
        messenger.delete_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        messenger.send_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text="Будь ласка, оберіть напій.",
            reply_markup=json.dumps({"inline_keyboard": build_drinks_keyboard()}),
        )
        return HandlerStatus.STOP
