import time

from bot.dispatcher import Dispatcher
from bot.domain.messenger import Messenger


def start_long_polling(dispatcher: Dispatcher, messenger: Messenger):
    next_update_offset = 0
    while True:
        updates = messenger.get_updates(offset=next_update_offset)
        for update in updates:
            dispatcher.dispatch(update)
            next_update_offset = max(next_update_offset, update["update_id"]) + 1
            print(".", end="", flush=True)
        time.sleep(1)
