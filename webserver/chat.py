from dataclasses import dataclass
from datetime import datetime

import nh3
from pydantic import BaseModel


class User(BaseModel):
    username: str


@dataclass(frozen=True)
class Message(BaseModel):
    is_server_message: bool
    author: User
    string: str
    timestamp: datetime

def sanitize_message(msg: Message) -> Message:
    message_copy = Message(
        is_server_message=msg.is_server_message,
        author=msg.author,
        string=nh3.clean(msg.string),
        timestamp=msg.timestamp,
    )
    return message_copy

class Chat(BaseModel):
    title: str
    message_history: list[Message]

    def add_message(self, new_message: Message):
        self.message_history.append(new_message)

    def add_server_message(self, new_message: Message):
        new_message.is_server_message = True
        self.message_history.append(new_message)
