import json
import os
import urllib.request

from dotenv import load_dotenv

load_dotenv()


def make_request(method: str, **params):
    json_data = json.dumps(params).encode("utf-8")

    request = urllib.request.Request(
        method="POST",
        url=f"{os.getenv('TELEGRAM_BASE_URI')}/{method}",
        headers={"Content-Type": "application/json"},
        data=json_data,
    )
    with urllib.request.urlopen(request) as response:
        response_body = response.read().decode("utf-8")
        response_json = json.loads(response_body)
        assert response_json["ok"] == True
        return response_json["result"]


def get_updates(**params) -> list[dict]:
    """
    Reference of the method:  https://core.telegram.org/bots/api#getupdates
    Returned:   List of Update object
    Reference of the update object:  https://core.telegram.org/bots/api#update
    """
    return make_request("getUpdates", **params)


def send_message(chat_id: int, text: str, **params) -> dict:
    """
    Reference of the method:  https://core.telegram.org/bots/api#sendmessage
    Returned:   Message object
    Reference of the Message object  https://core.telegram.org/bots/api#message
    """
    return make_request("sendMessage", chat_id=chat_id, text=text, **params)


def get_me() -> dict:
    """
    A simple method for testing your bot's authentication token. Requires no parameters.
    Returns basic information about the bot in form of a User object
    Reference of the User object:  https://core.telegram.org/bots/api#user
    """
    return make_request("getMe")


def send_photo(chat_id: int, photo: str, **params) -> dict:
    """
    Reference of the method:  https://core.telegram.org/bots/api#sendphoto
    Returned:   Message object
    Reference of the Message object  https://core.telegram.org/bots/api#message
    """
    return make_request("sendPhoto", chat_id=chat_id, photo=photo, **params)


def answer_callback_query(callback_query_id: str) -> list[dict]:
    """
    Reference of the method:  https://core.telegram.org/bots/api#answercallbackquery
    Returned:   True
    """
    return make_request("answerCallbackQuery", callback_query_id=callback_query_id)


def delete_message(chat_id: int, message_id: int) -> bool:
    """
    Reference of the method:  https://core.telegram.org/bots/api#deletemessage
    Returned:   True
    """
    return make_request("deleteMessage", chat_id=chat_id, message_id=message_id)
