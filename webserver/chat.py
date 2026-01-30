from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    username: str


@dataclass(frozen=True)
class Message(BaseModel):
    is_server_message: bool
    author: User
    string: str
    timestamp: datetime


class Chat(BaseModel):
    title: str
    message_history: list[Message]

    def add_message(self, new_message: Message):
        self.message_history.append(new_message)

    def add_server_message(self, new_message: Message):
        new_message.is_server_message = True
        self.message_history.append(new_message)
