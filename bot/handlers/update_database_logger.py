from bot.database_client import persist_update
from bot.handlers.handler import Handler, HandlerStatus


class UpdateDataBaseLogger(Handler):
    def can_handle(self, update: dict, state: str, order_data: dict) -> bool:
        return True

    def handle(self, update: dict, state: str, order_data: dict) -> HandlerStatus:
        persist_update(update)
        return HandlerStatus.CONTINUE
