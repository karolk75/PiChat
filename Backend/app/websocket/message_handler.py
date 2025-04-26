import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import WebSocket

from app.models.chat import MessageRole
from app.services.cosmos_db import CosmosDBService, get_cosmos_db


async def handle_chat_message(
    payload: Dict[str, Any], websocket: WebSocket, db: CosmosDBService = None
) -> Optional[Dict[str, Any]]:
    """WebSocket handler to send a message in a chat"""
    if db is None:
        db = get_cosmos_db()

    chat_id = payload.get("chatId")
    message = payload.get("message")

    if not chat_id or not message:
        return {"type": "ERROR", "error": "Chat ID and message are required"}

    # Store the user message
    user_message = {
        "id": message.get("id", str(uuid.uuid4())),
        "content": message.get("content", ""),
        "role": MessageRole.USER,
        "chat_id": chat_id,
        "created_at": datetime.utcnow().isoformat(),
    }

    await db.add_message(chat_id, user_message)

    # Generate a mock response for the assistant
    # In a real app, you'd call your AI service here
    trace_id = str(uuid.uuid4())
    content = f"This is a response to: {message.get('content')}"

    # Send streaming response chunks to simulate streaming
    chunks = [content[i : i + 10] for i in range(0, len(content), 10)]

    for i, chunk in enumerate(chunks):
        await websocket.send_text(
            json.dumps(
                {"type": "MESSAGE", "content": chunk, "traceId": trace_id, "end": False}
            )
        )

    # Send final chunk to indicate end of message
    await websocket.send_text(
        json.dumps({"type": "MESSAGE", "content": "", "traceId": trace_id, "end": True})
    )

    # Store the assistant response
    assistant_message = {
        "id": trace_id,
        "content": content,
        "role": MessageRole.ASSISTANT,
        "chat_id": chat_id,
        "created_at": datetime.now().isoformat(),
    }

    await db.add_message(chat_id, assistant_message)

    return None
