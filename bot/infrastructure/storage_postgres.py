import json
import os

import pg8000
from dotenv import load_dotenv

from bot.domain.storage import Storage

load_dotenv()


class StoragePostgres(Storage):
    def _get_connection(self):
        """Create and return Postgres connection"""
        host = os.getenv("POSTGRES_HOST")
        port = os.getenv("POSTGRES_PORT")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        database = os.getenv("POSTGRES_DB")

        if host is None:
            raise ValueError("POSTGRES_HOST value is not set!!!")
        if port is None:
            port = "3452"
        if user is None:
            raise ValueError("POSTGRES_USER value is not set!!!")
        if password is None:
            raise ValueError("POSTGRES_PASSWORD value is not set!!!")
        if database is None:
            raise ValueError("POSTGRES_DB value is not set!!!")

        return pg8000.connect(
            host=host, port=int(port), user=user, password=password, database=database
        )

    def recreate_database(self) -> None:
        # connection = sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH"))
        # створення таблиць
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS telegram_events")
                cursor.execute("DROP TABLE IF EXISTS users")
                print("Таблиці видалені")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS telegram_events
                    (
                        id SERIAL PRIMARY KEY,
                        payload TEXT NOT NULL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users
                    (
                        id SERIAL PRIMARY KEY,
                        telegram_id BIGINT NOT NULL UNIQUE,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        state TEXT DEFAULT NULL,
                        order_json TEXT DEFAULT NULL
                    )
                """)
            conn.commit()
            print(" Таблиці створені")

    def persist_updates(self, updates: list[dict]) -> None:
        payloads = []
        for update in updates:
            payloads.append((json.dumps(update, ensure_ascii=False, indent=2),))

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.executemany(
                    "INSERT INTO telegram_events (payload) VALUES (%s)", payloads
                )
            conn.commit()

    def persist_update(self, update: dict) -> None:
        payload: str = json.dumps(update, ensure_ascii=False, indent=2)

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO telegram_events (payload) VALUES (%s)", (payload,)
                )
            conn.commit()

    def ensure_user_exists(self, telegram_id: int) -> None:
        """
        Ensure a users with given telegram_id exists in users table.
        If user doesn't exists, create them.
        All operation happen in single transaction.
        """
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                # check if user exists.
                cursor.execute(
                    "SELECT 1 FROM users WHERE telegram_id = %s", (telegram_id,)
                )
                # If user doesn't exists, create them.
                if cursor.fetchone() is None:
                    cursor.execute(
                        "INSERT INTO users (telegram_id) VALUES (%s)", (telegram_id,)
                    )
            conn.commit()

    def clear_user_state(self, telegram_id: int) -> None:
        """Clear user state and order_json in table users"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET state=NULL, order_json = NULL WHERE telegram_id = %s",
                    (telegram_id,),
                )
            conn.commit()

    def update_user_state(self, telegram_id: int, state: str) -> None:
        """Update user state in table users"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET state=%s WHERE telegram_id = %s",
                    (state, telegram_id),
                )
            conn.commit()

    def update_user_order_json(self, telegram_id: int, order_data: dict) -> None:
        """Update user state in table users"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET order_json=%s WHERE telegram_id = %s",
                    (
                        json.dumps(order_data, ensure_ascii=False, indent=2),
                        telegram_id,
                    ),
                )
            conn.commit()

    def get_user(self, telegram_id: int) -> dict:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, telegram_id, created_at, state, order_json FROM users WHERE telegram_id = %s",
                    (telegram_id,),
                )
                result = cursor.fetchone()
            conn.commit()
        if result:
            return {
                "id": result[0],
                "telegram_id": result[1],
                "created_at": result[2],
                "state": result[3],
                "order_json": result[4],
            }
        return None
