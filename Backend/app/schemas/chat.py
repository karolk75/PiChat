from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

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
        
# WebSocket schemas
class WebSocketCommand(BaseModel):
    type: str
    chatId: Optional[str] = None
    message: Optional[Dict[str, Any]] = None
    name: Optional[str] = None
    
class WebSocketResponse(BaseModel):
    type: str
    payload: Dict[str, Any] = Field(default_factory=dict) 