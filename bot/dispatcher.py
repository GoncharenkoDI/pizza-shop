import json

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class Dispatcher:
    def __init__(self, storage: Storage, messenger: Messenger):
        self._handlers: list[Handler] = []
        self._messenger: Messenger = messenger
        self._storage: Storage = storage

    def add_handlers(self, *handlers: list[Handler]) -> None:
        for handle in handlers:
            self._handlers.append(handle)

    def _get_telegram_id_from_update(self, update: dict) -> int:
        if "message" in update:
            return update["message"]["from"]["id"]
        if "callback_query" in update:
            return update["callback_query"]["from"]["id"]
        return None

    def dispatch(self, update: dict) -> None:
        telegram_id = self._get_telegram_id_from_update(update)
        user = self._storage.get_user(telegram_id) if telegram_id else None
        user_state = user.get("state") if user else None
        user_order_json = user.get("order_json") if user else "{}"
        if user_order_json is None:
            user_order_json = "{}"
        user_order_data = json.loads(user_order_json)

        for handler in self._handlers:
            if handler.can_handle(
                update, user_state, user_order_data, self._storage, self._messenger
            ):
                signal = handler.handle(
                    update, user_state, user_order_data, self._storage, self._messenger
                )
                if signal == HandlerStatus.STOP:
                    break
