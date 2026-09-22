from abc import ABC, abstractmethod


class Messenger(ABC):

    @abstractmethod
    def get_updates(self, **params) -> list[dict]: ...

    @abstractmethod
    def send_message(self, chat_id: int, text: str, **params) -> dict: ...

    @abstractmethod
    def send_photo(self, chat_id: int, photo: str, **params) -> dict: ...

    @abstractmethod
    def answer_callback_query(self, callback_query_id: str) -> list[dict]: ...

    @abstractmethod
    def delete_message(self, chat_id: int, message_id: int) -> bool: ...
