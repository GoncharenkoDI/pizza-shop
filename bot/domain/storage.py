from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    def recreate_database(self) -> None: ...

    @abstractmethod
    def persist_updates(self, updates: list[dict]) -> None: ...

    @abstractmethod
    def persist_update(self, update: dict) -> None: ...

    @abstractmethod
    def ensure_user_exists(self, telegram_id: int) -> None:
        """
        Ensure a users with given telegram_id exists in users table.
        If user doesn't exists, create them.
        All operation happen in single transaction.
        """

    @abstractmethod
    def clear_user_state(self, telegram_id: int) -> None:
        """Clear user state and order_json in table users"""

    @abstractmethod
    def update_user_state(self, telegram_id: int, state: str) -> None:
        """Update user state in table users"""

    @abstractmethod
    def update_user_order_json(self, telegram_id: int, order_data: dict) -> None:
        """Update user state in table users"""

    @abstractmethod
    def get_user(self, telegram_id: int) -> dict:
        """
        Get complete user object from table users by telegram_id
        {id, telegram_id, created_at, state, order_json}
        """
