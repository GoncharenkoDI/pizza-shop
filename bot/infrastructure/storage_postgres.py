import json
import logging
import os
import time

import pg8000
from dotenv import load_dotenv

from bot.domain.storage import Storage

load_dotenv()

# Налаштування логування для обробки запитів до БД
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s.%(msecs)03d] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


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
        # створення таблиць
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                # cursor.execute("DROP TABLE IF EXISTS telegram_events")
                # cursor.execute("DROP TABLE IF EXISTS users")
                # print("Таблиці видалені")
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
        start_time = time.time()
        method_name = "persist_updates"
        sql = "INSERT INTO telegram_events (payload) VALUES (%s)"

        payloads = []
        for update in updates:
            payloads.append((json.dumps(update, ensure_ascii=False, indent=2),))

        logger.info(f"[DB] - {method_name} {sql}- start")
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.executemany(sql, payloads)
                conn.commit()

            duration = (time.time() - start_time) * 1000
            logger.info(f"[DB] - {method_name} - finished - {duration:.2f}ms")
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(
                f"[DB] - {method_name} - failed - {duration:.2f}ms. Error: {e}"
            )
            raise

    def persist_update(self, update: dict) -> None:
        start_time = time.time()
        method_name = "persist_update"
        sql = "INSERT INTO telegram_events (payload) VALUES (%s)"
        payload: str = json.dumps(update, ensure_ascii=False, indent=2)
        logger.info(f"[DB] - {method_name} {sql}- start")
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (payload,))
                conn.commit()

            duration = (time.time() - start_time) * 1000
            logger.info(f"[DB] - {method_name} - finished - {duration:.2f}ms\n")

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(
                f"[DB] - {method_name} - failed - {duration:.2f}ms. Error: {e}\n"
            )
            raise

    def ensure_user_exists(self, telegram_id: int) -> None:
        """
        Ensure a users with given telegram_id exists in users table.
        If user doesn't exists, create them.
        All operation happen in single transaction.
        """
        start_time = time.time()
        method_name = "ensure_user_exists"
        try:
            logger.info(f"[DB] - {method_name} - start")
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # check if user exists.
                    sql = "SELECT 1 FROM users WHERE telegram_id = %s"
                    logger.info(f"[DB] - {method_name} {sql} - start")
                    cursor.execute(sql, (telegram_id,))
                    result = cursor.fetchone()
                    duration = (time.time() - start_time) * 1000
                    logger.info(
                        f"[DB] - {method_name} {sql} - finished - {duration:.2f}ms."
                    )
                    # If user doesn't exists, create them.
                    if result is None:
                        start_time2 = time.time()
                        sql = "INSERT INTO users (telegram_id) VALUES (%s)"
                        logger.info(f"[DB] - {method_name} {sql} - start")
                        cursor.execute(sql, (telegram_id,))
                        duration = (time.time() - start_time2) * 1000
                        logger.info(
                            f"[DB] - {method_name} {sql} - finished - {duration:.2f}ms."
                        )
                conn.commit()

            duration = (time.time() - start_time) * 1000
            logger.info(f"[DB] - {method_name} - finished - {duration:.2f}ms.")
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(
                f"[DB] - {method_name} - failed - {duration:.2f}ms. Error: {e}"
            )
            raise

    def clear_user_state(self, telegram_id: int) -> None:
        """Clear user state and order_json in table users"""
        sql = "UPDATE users SET state=NULL, order_json = NULL WHERE telegram_id = %s"
        start_time = time.time()
        method_name = "clear_user_state"
        logger.info(f"[DB] - {method_name} {sql} - start")
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        sql,
                        (telegram_id,),
                    )
                conn.commit()
            duration = (time.time() - start_time) * 1000
            logger.info(f"[DB] - {method_name} - finished - {duration:.2f}ms")
        except Exception:
            duration = (time.time() - start_time) * 1000
            logger.error(f"[DB] - {method_name} - failed - {duration:.2f}ms")
            raise

    def update_user_state(self, telegram_id: int, state: str) -> None:
        """Update user state in table users"""
        sql = "UPDATE users SET state=%s WHERE telegram_id = %s"
        start_time = time.time()
        method_name = "update_user_state"
        logger.info(f"[DB] - {method_name} {sql} - start")
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        sql,
                        (state, telegram_id),
                    )
                conn.commit()

            duration = (time.time() - start_time) * 1000
            logger.info(f"[DB] - {method_name} - finished - {duration:.2f}ms")

        except Exception:
            duration = (time.time() - start_time) * 1000
            logger.error(f"[DB] - {method_name} - failed - {duration:.2f}ms")
            raise

    def update_user_order_json(self, telegram_id: int, order_data: dict) -> None:
        """Update user state in table users"""
        sql = "UPDATE users SET order_json=%s WHERE telegram_id = %s"
        start_time = time.time()
        method_name = "update_user_order_json"
        logger.info(f"[DB] - {method_name} {sql} - start")
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        sql,
                        (
                            json.dumps(order_data, ensure_ascii=False, indent=2),
                            telegram_id,
                        ),
                    )
                conn.commit()

            duration = (time.time() - start_time) * 1000
            logger.info(f"[DB] - {method_name} - finished - {duration:.2f}ms")

        except Exception:
            duration = (time.time() - start_time) * 1000
            logger.error(f"[DB] - {method_name} - failed - {duration:.2f}ms")
            raise

    def get_user(self, telegram_id: int) -> dict:
        sql = "SELECT id, telegram_id, created_at, state, order_json FROM users WHERE telegram_id = %s"
        method_name = "get_user"
        start_time = time.time()
        logger.info(f"[DB] - {method_name} - {sql} started.")
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        sql,
                        (telegram_id,),
                    )
                    result = cursor.fetchone()
                conn.commit()
            duration = (time.time() - start_time) * 1000
            logger.info(f"[DB] - {method_name} finished - {duration:.2f}ms.")
        except Exception:
            duration = (time.time() - start_time) * 1000
            logger.error(f"[DB] - {method_name} failed - {duration}ms.")
            raise
        if result:
            return {
                "id": result[0],
                "telegram_id": result[1],
                "created_at": result[2],
                "state": result[3],
                "order_json": result[4],
            }
        return None
