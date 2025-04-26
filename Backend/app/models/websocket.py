from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class WebSocketCommand(BaseModel):
    type: str
    chatId: Optional[str] = None
    message: Optional[Dict[str, Any]] = None
    name: Optional[str] = None


class WebSocketResponse(BaseModel):
    type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
