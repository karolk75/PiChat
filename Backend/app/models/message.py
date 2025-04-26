from enum import Enum

from pydantic import BaseModel


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    id: str
    content: str
    role: MessageRole
    chat_id: str
    created_at: str

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    content: str
    role: MessageRole = MessageRole.USER
