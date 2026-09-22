from bot.dispatcher import Dispatcher
from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers import get_handlers
from bot.infrastructure.messenger_telegram import MessengerTelegram
from bot.infrastructure.storage_sqlite import StorageSqlite
from bot.long_polling import start_long_polling

if __name__ == "__main__":
    try:
        messenger: Messenger = MessengerTelegram()
        storage: Storage = StorageSqlite()
        dispatcher = Dispatcher(storage, messenger)
        dispatcher.add_handler(get_handlers())
        start_long_polling(dispatcher, messenger)
    except KeyboardInterrupt:
        print("\nBye!")
