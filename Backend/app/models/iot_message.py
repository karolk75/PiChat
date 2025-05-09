from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import uuid

class ChatMessage(BaseModel):
    role: str
    content: str

class IoTHubRequest(BaseModel):
    message: str
    conversation: Optional[List[Dict[str, str]]] = []
    device_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    device_test: Optional[bool] = False

class IoTHubResponse(BaseModel):
    response: str
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow) 