from bot.handlers.approval_order import ApprovalOrder
from bot.handlers.cancel_order import CancelOrder
from bot.handlers.drink_selection import DrinkSelection
from bot.handlers.ensure_user_exists import EnsureUserExists
from bot.handlers.handler import Handler
from bot.handlers.message_start import MessageStart
from bot.handlers.pizza_selection import PizzaSelectionHandler
from bot.handlers.size_selection import SizeSelection
from bot.handlers.update_database_logger import UpdateDataBaseLogger


def get_handlers() -> list[Handler]:
    return [
        UpdateDataBaseLogger(),
        EnsureUserExists(),
        MessageStart(),
        PizzaSelectionHandler(),
        SizeSelection(),
        DrinkSelection(),
        ApprovalOrder(),
        CancelOrder(),
    ]
