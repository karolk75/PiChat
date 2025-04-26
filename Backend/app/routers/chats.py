from fastapi import APIRouter, Depends, HTTPException, WebSocket, status
from typing import List, Dict, Any, Optional
import uuid
import json
import logging
from datetime import datetime
from ..services.cosmos_db import get_cosmos_db, CosmosDBService
from ..schemas.chat import Chat, ChatCreate, ChatWithMessages, ChatMessage, ChatMessageCreate, MessageRole
from ..auth import get_api_key

router = APIRouter()
logger = logging.getLogger(__name__)

# REST API endpoints for chats
@router.get("/chats", response_model=List[Chat], dependencies=[Depends(get_api_key)])
async def get_chats(db: CosmosDBService = Depends(get_cosmos_db)):
    """Get all chats"""
    chats = await db.get_all_chats()
    return chats

@router.post("/chats", response_model=Chat, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_api_key)])
async def create_chat(chat: ChatCreate, db: CosmosDBService = Depends(get_cosmos_db)):
    """Create a new chat"""
    new_chat = await db.create_chat(chat.name)
    return new_chat

@router.get("/chats/{chat_id}", response_model=ChatWithMessages, dependencies=[Depends(get_api_key)])
async def get_chat_with_messages(chat_id: str, db: CosmosDBService = Depends(get_cosmos_db)):
    """Get a chat with its messages"""
    chat = await db.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    messages = await db.get_chat_messages(chat_id)
    return ChatWithMessages(
        id=chat["id"],
        name=chat["name"],
        active=chat.get("active", False),
        created_at=chat["created_at"],
        messages=messages
    )

@router.delete("/chats/{chat_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_api_key)])
async def delete_chat(chat_id: str, db: CosmosDBService = Depends(get_cosmos_db)):
    """Delete a chat and all its messages"""
    success = await db.delete_chat(chat_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat not found")
    return None

@router.post("/chats/{chat_id}/messages", response_model=ChatMessage, dependencies=[Depends(get_api_key)])
async def add_chat_message(chat_id: str, message: ChatMessageCreate, db: CosmosDBService = Depends(get_cosmos_db)):
    """Add a message to a chat"""
    chat = await db.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    new_message = {
        "id": str(uuid.uuid4()),
        "content": message.content,
        "role": message.role,
        "chat_id": chat_id,
        "created_at": datetime.utcnow().isoformat()
    }
    
    created_message = await db.add_message(chat_id, new_message)
    return created_message

@router.get("/chats/{chat_id}/messages", response_model=List[ChatMessage], dependencies=[Depends(get_api_key)])
async def get_chat_messages(chat_id: str, db: CosmosDBService = Depends(get_cosmos_db)):
    """Get all messages for a chat"""
    chat = await db.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    messages = await db.get_chat_messages(chat_id)
    return messages

# WebSocket handlers
async def handle_get_chats(payload: Dict[str, Any], websocket: WebSocket, db: CosmosDBService = None) -> Dict[str, Any]:
    """WebSocket handler to get all chats"""
    if db is None:
        db = get_cosmos_db()
    
    chats = await db.get_all_chats()
    
    return {
        "type": "CHAT_LIST",
        "chats": chats
    }

async def handle_create_chat(payload: Dict[str, Any], websocket: WebSocket, db: CosmosDBService = None) -> Dict[str, Any]:
    """WebSocket handler to create a new chat"""
    if db is None:
        db = get_cosmos_db()
    
    chat_name = payload.get('name', f'Chat {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    new_chat = await db.create_chat(chat_name)
    
    return {
        "type": "NEW_CHAT",
        "chat": new_chat
    }

async def handle_get_chat_history(payload: Dict[str, Any], websocket: WebSocket, db: CosmosDBService = None) -> Dict[str, Any]:
    """WebSocket handler to get chat history"""
    if db is None:
        db = get_cosmos_db()
    
    chat_id = payload.get('chatId')
    if not chat_id:
        return {"type": "ERROR", "error": "Chat ID is required"}
    
    messages = await db.get_chat_messages(chat_id)
    
    return {
        "type": "CHAT_HISTORY",
        "messages": messages
    }

async def handle_delete_chat(payload: Dict[str, Any], websocket: WebSocket, db: CosmosDBService = None) -> Dict[str, Any]:
    """WebSocket handler to delete a chat"""
    if db is None:
        db = get_cosmos_db()
    
    chat_id = payload.get('chatId')
    if not chat_id:
        return {"type": "ERROR", "error": "Chat ID is required"}
    
    success = await db.delete_chat(chat_id)
    
    return {
        "type": "CHAT_DELETED",
        "chatId": chat_id
    }

async def handle_chat_message(payload: Dict[str, Any], websocket: WebSocket, db: CosmosDBService = None) -> Optional[Dict[str, Any]]:
    """WebSocket handler to send a message in a chat"""
    if db is None:
        db = get_cosmos_db()
    
    chat_id = payload.get('chatId')
    message = payload.get('message')
    
    if not chat_id or not message:
        return {"type": "ERROR", "error": "Chat ID and message are required"}
    
    # Store the user message
    user_message = {
        "id": message.get('id', str(uuid.uuid4())),
        "content": message.get('content', ''),
        "role": MessageRole.USER,
        "chat_id": chat_id,
        "created_at": datetime.utcnow().isoformat()
    }
    
    await db.add_message(chat_id, user_message)
    
    # Generate a mock response for the assistant
    # In a real app, you'd call your AI service here
    trace_id = str(uuid.uuid4())
    content = f"This is a response to: {message.get('content')}"
    
    # Send streaming response chunks to simulate streaming
    chunks = [content[i:i+10] for i in range(0, len(content), 10)]
    
    for i, chunk in enumerate(chunks):
        await websocket.send_text(json.dumps({
            "type": "MESSAGE",
            "content": chunk,
            "traceId": trace_id,
            "end": False
        }))
    
    # Send final chunk to indicate end of message
    await websocket.send_text(json.dumps({
        "type": "MESSAGE",
        "content": "",
        "traceId": trace_id,
        "end": True
    }))
    
    # Store the assistant response
    assistant_message = {
        "id": trace_id,
        "content": content,
        "role": MessageRole.ASSISTANT,
        "chat_id": chat_id,
        "created_at": datetime.utcnow().isoformat()
    }
    
    await db.add_message(chat_id, assistant_message)
    
    # No need to return anything as we've already sent streaming responses
    return None 