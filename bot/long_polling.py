import os

from dotenv import load_dotenv

from bot.dispatcher import Dispatcher
from bot.domain.messenger import Messenger

load_dotenv()


def start_long_polling(dispatcher: Dispatcher, messenger: Messenger):
    next_update_offset = 0
    timeout = int(os.getenv("LP_TIMEOUT"))
    while True:
        updates = messenger.get_updates(timeout, offset=next_update_offset)
        for update in updates:
            dispatcher.dispatch(update)
            next_update_offset = max(next_update_offset, update["update_id"]) + 1
            print(".", end="", flush=True)
