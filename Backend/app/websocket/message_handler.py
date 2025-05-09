import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import WebSocket

from app.models.message import MessageRole
from app.services.cosmos_db import CosmosDBService, get_cosmos_db
from app.services.azure_openai import AzureOpenAIService, get_openai_service

async def handle_chat_message(
    payload: Dict[str, Any], websocket: WebSocket, cosmos_db: CosmosDBService = None, openai_service: AzureOpenAIService = None
) -> Optional[Dict[str, Any]]:
    """WebSocket handler to send a message in a chat"""
    if cosmos_db is None:
        cosmos_db = get_cosmos_db()
        
    if openai_service is None:
        openai_service = get_openai_service()

    chat_id = payload.get("chatId")
    message = payload.get("content", "")

    if not chat_id or not message:
        return {"type": "ERROR", "error": "Chat ID and message are required"}

    # Store the user message
    user_message = {
        "id": str(uuid.uuid4()),
        "content": message,
        "role": MessageRole.USER,
        "chat_id": chat_id,
        "created_at": datetime.utcnow().isoformat(),
    }

    await cosmos_db.add_message(chat_id, user_message)

    # Get previous messages for context
    chat_messages = await cosmos_db.get_chat_messages(chat_id)
    
    # Format messages for OpenAI
    openai_messages = [
        {"role": "user" if msg["role"] == MessageRole.USER else "assistant", 
         "content": msg["content"]}
        for msg in chat_messages
    ]
    
    # Generate trace ID for the response
    trace_id = str(uuid.uuid4())
    
    # Initialize full content to store in the database
    full_content = ""

    # Stream the response from OpenAI
    try:
        async for chunk in openai_service.generate_response(openai_messages):
            if chunk.choices and chunk.choices[0].delta.content:
                content_chunk = chunk.choices[0].delta.content
                full_content += content_chunk
                
                # Send chunk to the client
                await websocket.send_text(
                    json.dumps(
                        {"type": "MESSAGE", "content": content_chunk, "traceId": trace_id, "end": False}
                    )
                )
        
        # Send final chunk to indicate end of message
        await websocket.send_text(
            json.dumps({"type": "MESSAGE", "content": "", "traceId": trace_id, "end": True})
        )
        
        # Store the assistant response
        assistant_message = {
            "id": trace_id,
            "content": full_content,
            "role": MessageRole.ASSISTANT,
            "chat_id": chat_id,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        await cosmos_db.add_message(chat_id, assistant_message)
        
    except Exception as e:
        # Send error message
        await websocket.send_text(
            json.dumps({"type": "ERROR", "error": str(e)})
        )

    return None
