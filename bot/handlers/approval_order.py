import json

from bot.domain.messenger import Messenger
from bot.domain.pizza import get_drinks, get_pizza_size, get_pizza_type
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class ApprovalOrder(Handler):
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

        if state != "WAIT_FOR_ORDER_APPROVAL":
            return False

        if "data" not in update["callback_query"]:
            return False

        callback_data = update["callback_query"]["data"]

        return callback_data == "approval"

    def handle(
        self,
        update: dict,
        state: str,
        order_data: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_query_id = update["callback_query"]["id"]
        chat_id = update["callback_query"]["message"]["chat"]["id"]
        message_id = update["callback_query"]["message"]["message_id"]

        storage.clear_user_state(telegram_id)

        messenger.answer_callback_query(callback_query_id)
        messenger.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )

        message_text = f"""
            Ви обрали:
            піцу - {get_pizza_type(order_data["pizza_type"])},
            розмір - {get_pizza_size(order_data["pizza_size"])},
            напій - {get_drinks(order_data["drink"])}
            Ваше замовлення вже в дорозі!
        """

        messenger.send_message(
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
