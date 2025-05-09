from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class WebSocketCommand(BaseModel):
    type: str
    payload: Optional[Dict[str, Any]] = None


class WebSocketResponse(BaseModel):
    type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
