from enum import Enum
from typing import List

from pydantic import BaseModel


class Role(Enum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


class Message(BaseModel):
    role: Role
    content: str


class ChatState(BaseModel):
    keywords: List[str]
    messages: List[Message]
    excluded_ids: List[str]


class InitChat(BaseModel):
    chat_id: str
    user_id: str
    ai_outputs: list


class Chat(BaseModel):
    chat_id: str
    user_id: str
    ai_outputs: List[str]
    current_keywords: List[str]
