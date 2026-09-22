import json
import os
import urllib.request

from dotenv import load_dotenv

from bot.domain.messenger import Messenger

load_dotenv()


class MessengerTelegram(Messenger):
    def _get_telegram_base_uri(self) -> str:
        return f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"

    def _get_telegram_file_uri(self) -> str:
        return f"https://api.telegram.org/file/bot{os.getenv('TELEGRAM_TOKEN')}"

    def _make_request(self, method: str, **kwargs):
        json_data = json.dumps(kwargs).encode("utf-8")

        request = urllib.request.Request(
            method="POST",
            url=f"{self._get_telegram_base_uri()}/{method}",
            headers={"Content-Type": "application/json"},
            data=json_data,
        )

        with urllib.request.urlopen(request) as response:
            response_body = response.read().decode("utf-8")
            response_json = json.loads(response_body)
            assert response_json["ok"] == True
            return response_json["result"]

    def get_updates(self, **kwargs) -> list[dict]:
        """
        Reference of the method:  https://core.telegram.org/bots/api#getupdates
        Returned:   List of Update object
        Reference of the update object:  https://core.telegram.org/bots/api#update
        """
        return self._make_request("getUpdates", **kwargs)

    def send_message(self, chat_id: int, text: str, **kwargs) -> dict:
        """
        Reference of the method:  https://core.telegram.org/bots/api#sendmessage
        Returned:   Message object
        Reference of the Message object  https://core.telegram.org/bots/api#message
        """
        return self._make_request("sendMessage", chat_id=chat_id, text=text, **kwargs)

    def get_me(self) -> dict:
        """
        A simple method for testing your bot's authentication token. Requires no parameters.
        Returns basic information about the bot in form of a User object
        Reference of the User object:  https://core.telegram.org/bots/api#user
        """
        return self._make_request("getMe")

    def send_photo(self, chat_id: int, photo: str, **kwargs) -> dict:
        """
        Reference of the method:  https://core.telegram.org/bots/api#sendphoto
        Returned:   Message object
        Reference of the Message object  https://core.telegram.org/bots/api#message
        """
        return self._make_request("sendPhoto", chat_id=chat_id, photo=photo, **kwargs)

    def answer_callback_query(self, callback_query_id: str) -> list[dict]:
        """
        Reference of the method:  https://core.telegram.org/bots/api#answercallbackquery
        Returned:   True
        """
        return self._make_request(
            "answerCallbackQuery", callback_query_id=callback_query_id
        )

    def delete_message(self, chat_id: int, message_id: int) -> bool:
        """
        Reference of the method:  https://core.telegram.org/bots/api#deletemessage
        Returned:   True
        """
        return self._make_request(
            "deleteMessage", chat_id=chat_id, message_id=message_id
        )
