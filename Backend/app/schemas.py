from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enum definitions for validation
class ModelType(str, Enum):
    GPT4 = "gpt-4"
    GPT35 = "gpt-3.5-turbo"

class VoiceGender(str, Enum):
    MALE = "male"
    FEMALE = "female"

class VoiceAccent(str, Enum):
    POLISH = "polish"
    US = "us"
    UK = "uk"

class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

# WebSocket Message Schema
class WebSocketMessage(BaseModel):
    action: str
    payload: Optional[Dict[str, Any]] = Field(default_factory=dict)

# User Schemas
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: str
    created_at: datetime
    
    class Config:
        orm_mode = True

# Conversation Schemas
class ConversationBase(BaseModel):
    title: str = "New Conversation"

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(BaseModel):
    title: str

class Conversation(ConversationBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class ConversationWithMessages(Conversation):
    messages: List['Message'] = []
    
    class Config:
        orm_mode = True

# Message Schemas
class MessageBase(BaseModel):
    content: str
    role: Role
    is_audio: bool = False

class MessageCreate(MessageBase):
    conversation_id: str

class Message(MessageBase):
    id: str
    conversation_id: str
    created_at: datetime
    
    class Config:
        orm_mode = True

# Settings Schemas
class VoiceSettings(BaseModel):
    gender: VoiceGender = VoiceGender.FEMALE
    accent: VoiceAccent = VoiceAccent.POLISH

class UserSettingsBase(BaseModel):
    selected_model: ModelType = ModelType.GPT35
    voice_settings: VoiceSettings = Field(default_factory=lambda: VoiceSettings())

class UserSettingsCreate(UserSettingsBase):
    user_id: str

class UserSettingsUpdate(UserSettingsBase):
    pass

class UserSettings(UserSettingsBase):
    id: str
    user_id: str
    
    class Config:
        orm_mode = True

# Circular import resolution
ConversationWithMessages.update_forward_refs() 