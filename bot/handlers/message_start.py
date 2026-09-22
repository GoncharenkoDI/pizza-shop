import json

from bot.domain.messenger import Messenger
from bot.domain.pizza import build_pizza_type_keyboard
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class MessageStart(Handler):
    def can_handle(
        self,
        update: dict,
        state: str,
        order_data: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        return (
            "message" in update
            and "text" in update["message"]
            and (
                update["message"]["text"] == "/start"
                or update["message"]["text"].lower() == "старт"
            )
        )

    def handle(
        self,
        update: dict,
        state: str,
        order_data: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["message"]["from"]["id"]

        storage.clear_user_state(telegram_id)
        storage.update_user_state(telegram_id, "WAIT_FOR_PIZZA_NAME")

        messenger.send_message(
            chat_id=update["message"]["chat"]["id"],
            text="🍕 Вітаю в магазині PIZZA SHOP.",
            reply_markup=json.dumps({"remove_keyboard": True}),
        )

        messenger.send_message(
            chat_id=update["message"]["chat"]["id"],
            text="Будь ласка, оберіть Вашу піцу.",
            reply_markup=json.dumps({"inline_keyboard": build_pizza_type_keyboard()}),
        )

        return HandlerStatus.STOP
