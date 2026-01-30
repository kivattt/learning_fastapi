import datetime
from threading import Lock
from typing import Optional
from uuid import uuid4, UUID

from pydantic import ValidationError, BaseModel, PrivateAttr

from webserver.chat import User, Chat, Message

THE_SERVER_USER: User = User(username="server")


class Server(BaseModel):
    serialization_version: str = "v1"
    chats: dict[UUID, Chat]
    _chats_lock: Lock = PrivateAttr(default_factory=Lock)  # The underscore prefix avoids pydantic serializing this

    # Creates a new chat and returns its UUID
    def create_new_chat(self, title) -> UUID:
        chat_created_message = Message(
            is_server_message=True,
            string="Chat created",
            timestamp=datetime.datetime.now(),  # This timestamp is too fine-grained.
            author=THE_SERVER_USER,
        )

        new_chat: Chat = Chat(title=title, message_history=list())
        new_chat.add_message(chat_created_message)

        chat_uuid = uuid4()

        with self._chats_lock:
            self.chats[chat_uuid] = new_chat
        return chat_uuid


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
