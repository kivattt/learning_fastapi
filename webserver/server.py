import datetime
from threading import Lock
from typing import Optional

from pydantic import ValidationError, BaseModel, PrivateAttr

from webserver.chat import User, Chat, Message
from webserver.invite_code import generate_invite_code

THE_SERVER_USER: User = User(username="server")


class Server(BaseModel):
    serialization_version: str = "v1"
    chats: dict[str, Chat]
    _chats_lock: Lock = PrivateAttr(default_factory=Lock)  # The underscore prefix avoids pydantic serializing this

    # Creates a new chat and returns its ID aka invite code
    def create_new_chat(self, title) -> str:
        chat_created_message = Message(
            is_server_message=True,
            string="Chat created",
            timestamp=datetime.datetime.now(),  # This timestamp is too fine-grained.
            author=THE_SERVER_USER,
        )

        new_chat: Chat = Chat(title=title, message_history=list())
        new_chat.add_message(chat_created_message)

        chat_id = generate_invite_code()

        with self._chats_lock:
            self.chats[chat_id] = new_chat
        return chat_id


# Throws a TypeError or OSError on failure
def write_server_file(server: Server, filename: str):
    data = server.model_dump_json()
    with open(filename, "w+", encoding="utf-8") as file:
        file.write(data)


def load_server_from_file(filename: str) -> Optional[Server]:
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = file.read()
            try:
                return Server.model_validate_json(data)
            except ValidationError:
                return None
    except OSError:
        return None
