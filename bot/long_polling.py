import time

import bot.telegram_client
from bot.dispatcher import Dispatcher


def start_long_polling(dispatcher: Dispatcher):
    next_update_offset = 0
    while True:
        updates = bot.telegram_client.get_updates(offset=next_update_offset)
        for update in updates:
            dispatcher.dispatch(update)
            next_update_offset = max(next_update_offset, update["update_id"]) + 1
            print(".", end="", flush=True)
        time.sleep(1)
