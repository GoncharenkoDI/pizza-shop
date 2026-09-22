from bot.domain.storage import Storage
from bot.infrastructure.storage_sqlite import StorageSqlite

storage: Storage = StorageSqlite()
storage.recreate_database()
