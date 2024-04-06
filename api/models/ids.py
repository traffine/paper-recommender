from pydantic import BaseModel


class UserId(BaseModel):
    user_id: str


class ChatId(BaseModel):
    chat_id: str
