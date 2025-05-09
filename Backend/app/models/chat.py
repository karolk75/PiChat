from typing import List

from pydantic import BaseModel

from app.models.message import ChatMessage



class Chat(BaseModel):
    id: str
    name: str
    active: bool = False
    created_at: str

    class Config:
        from_attributes = True


class ChatCreate(BaseModel):
    name: str = "New Chat"


class ChatWithMessages(Chat):
    messages: List[ChatMessage] = []

    class Config:
        from_attributes = True
