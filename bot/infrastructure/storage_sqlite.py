import json
import os
import sqlite3

from dotenv import load_dotenv

from bot.domain.storage import Storage

load_dotenv()


class StorageSqlite(Storage):
    def recreate_database(self) -> None:
        connection = sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH"))
        # створення таблиць
        with connection:
            connection.execute("DROP TABLE IF EXISTS telegram_updates")
            connection.execute("""
                CREATE TABLE IF NOT EXISTS telegram_updates
                (
                    id INTEGER PRIMARY KEY,
                    payload TEXT NOT NULL
                )
            """)
            connection.execute("DROP TABLE IF EXISTS users")
            connection.execute("""
                CREATE TABLE IF NOT EXISTS users
                (
                    id INTEGER PRIMARY KEY,
                    telegram_id INTEGER NOT NULL UNIQUE,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    state TEXT DEFAULT NULL,
                    order_json TEXT DEFAULT NULL
                )
            """)
        connection.close()

    def persist_updates(self, updates: list[dict]) -> None:
        connection = sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH"))

        with connection:
            data = []
            for update in updates:
                data.append((json.dumps(update, ensure_ascii=False, indent=2),))
            connection.executemany(
                "INSERT INTO telegram_updates (payload) VALUES (?)", data
            )
        connection.close()

    def persist_update(self, update: dict) -> None:
        connection = sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH"))

        with connection:
            json_update: str = json.dumps(update, ensure_ascii=False, indent=2)
            connection.execute(
                "INSERT INTO telegram_updates (payload) VALUES (?)", (json_update,)
            )
        connection.close()

    def ensure_user_exists(self, telegram_id: int) -> None:
        """
        Ensure a users with given telegram_id exists in users table.
        If user doesn't exists, create them.
        All operation happen in single transaction.
        """
        with sqlite3.connect(
            os.getenv("SQLITE_DATABASE_PATH")
        ) as connection, connection:
            # check if user exists.
            cursor = connection.execute(
                "SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,)
            )
            # If user doesn't exists, create them.
            if cursor.fetchone() is None:
                connection.execute(
                    "INSERT INTO users (telegram_id) VALUES (?)", (telegram_id,)
                )

    def clear_user_state(self, telegram_id: int) -> None:
        """Clear user state and order_json in table users"""
        with sqlite3.connect(
            os.getenv("SQLITE_DATABASE_PATH")
        ) as connection, connection:
            connection.execute(
                "UPDATE users SET state=NULL, order_json = NULL WHERE telegram_id = ?",
                (telegram_id,),
            )

    def update_user_state(self, telegram_id: int, state: str) -> None:
        """Update user state in table users"""
        with sqlite3.connect(
            os.getenv("SQLITE_DATABASE_PATH")
        ) as connection, connection:
            connection.execute(
                "UPDATE users SET state=? WHERE telegram_id = ?",
                (state, telegram_id),
            )

    def update_user_order_json(self, telegram_id: int, order_data: dict) -> None:
        """Update user state in table users"""
        with sqlite3.connect(
            os.getenv("SQLITE_DATABASE_PATH")
        ) as connection, connection:
            # 1
            connection.execute(
                "UPDATE users SET order_json=? WHERE telegram_id = ?",
                (json.dumps(order_data, ensure_ascii=False, indent=2), telegram_id),
            )

    def get_user(self, telegram_id: int) -> dict:
        """
        Get complete user object from table users by telegram_id
        {id, telegram_id, created_at, state, order_json}
        """
        with sqlite3.connect(
            os.getenv("SQLITE_DATABASE_PATH")
        ) as connection, connection:
            cursor = connection.execute(
                "SELECT id, telegram_id, created_at, state, order_json FROM users WHERE telegram_id = ?",
                (telegram_id,),
            )
            result = cursor.fetchone()
            if result:
                return {
                    "id": result[0],
                    "telegram_id": result[1],
                    "created_at": result[2],
                    "state": result[3],
                    "order_json": result[4],
                }
            return None
