from bot.domain.storage import Storage

# from bot.infrastructure.storage_sqlite import StorageSqlite
from bot.infrastructure.storage_postgres import StoragePostgres

storage: Storage = StoragePostgres()
storage.recreate_database()
